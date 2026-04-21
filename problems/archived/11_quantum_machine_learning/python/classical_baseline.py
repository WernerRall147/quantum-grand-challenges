"""Classical kernel ridge classification baseline for quantum ML instances."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import yaml


@dataclass(frozen=True)
class QMLInstance:
    instance_id: str
    name: str
    description: str
    samples: int
    features: int
    classes: int
    kernel_bandwidth: float
    noise: float
    train_split: float
    seed: int


def load_instances(instances_dir: Path) -> List[QMLInstance]:
    instances: List[QMLInstance] = []
    for path in sorted(instances_dir.glob("*.yaml")):
        raw = yaml.safe_load(path.read_text())
        instances.append(
            QMLInstance(
                instance_id=path.stem,
                name=str(raw.get("name", path.stem)),
                description=str(raw.get("description", "")),
                samples=int(raw.get("samples", 100)),
                features=int(raw.get("features", 4)),
                classes=int(raw.get("classes", 2)),
                kernel_bandwidth=float(raw.get("kernel_bandwidth", 1.0)),
                noise=float(raw.get("noise", 0.1)),
                train_split=float(raw.get("train_split", 0.7)),
                seed=int(raw.get("seed", 1234)),
            )
        )
    return instances


def generate_dataset(instance: QMLInstance) -> Tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(instance.seed)
    samples_per_class = instance.samples // instance.classes
    features = instance.features

    data = []
    labels = []
    for cls in range(instance.classes):
        center = rng.normal(loc=0.0, scale=1.5, size=features)
        spread = 0.5 + 0.3 * cls
        class_data = center + spread * rng.normal(size=(samples_per_class, features))
        data.append(class_data)
        labels.append(np.full(samples_per_class, cls, dtype=int))

    X = np.vstack(data)
    y = np.concatenate(labels)

    if instance.classes == 2:
        y = 2 * (y % 2) - 1  # map {0,1} -> {-1,+1}
    else:
        y = (y % 2) * 2 - 1

    X += instance.noise * rng.normal(size=X.shape)
    rng.shuffle(X)
    rng.shuffle(y)
    return X, y


def to_train_test(X: np.ndarray, y: np.ndarray, train_split: float) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    train_size = max(1, int(len(X) * train_split))
    X_train, X_test = X[:train_size], X[train_size:]
    y_train, y_test = y[:train_size], y[train_size:]
    return X_train, X_test, y_train, y_test


def rbf_kernel(a: np.ndarray, b: np.ndarray, bandwidth: float) -> np.ndarray:
    if bandwidth <= 0:
        raise ValueError("Kernel bandwidth must be positive.")
    diff = a[:, np.newaxis, :] - b[np.newaxis, :, :]
    dist_sq = np.sum(diff**2, axis=2)
    return np.exp(-dist_sq / (2.0 * bandwidth**2))


def normalize_rows(matrix: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms[norms == 0.0] = 1.0
    return matrix / norms


def kernel_ridge_classifier(X_train: np.ndarray, y_train: np.ndarray, X_eval: np.ndarray, bandwidth: float, reg_lambda: float = 1e-2) -> Tuple[np.ndarray, Dict[str, float]]:
    K = rbf_kernel(X_train, X_train, bandwidth)
    n = K.shape[0]
    alpha = np.linalg.solve(K + reg_lambda * np.eye(n), y_train)

    K_eval = rbf_kernel(X_eval, X_train, bandwidth)
    predictions = np.sign(K_eval @ alpha)

    kernel_alignment = float(np.mean(K * np.outer(y_train, y_train)))
    margin = float(np.mean(K_eval @ alpha))

    metrics = {
        "kernel_alignment": kernel_alignment,
        "solution_norm": float(alpha @ K @ alpha),
        "mean_margin": margin,
    }
    return predictions, metrics


def evaluate_instance(instance: QMLInstance) -> dict:
    X, y = generate_dataset(instance)
    X_train, X_test, y_train, y_test = to_train_test(X, y, instance.train_split)

    X_train_norm = normalize_rows(X_train)
    X_test_norm = normalize_rows(X_test)

    predictions_train, train_metrics = kernel_ridge_classifier(X_train_norm, y_train, X_train_norm, instance.kernel_bandwidth)
    predictions_test, test_metrics = kernel_ridge_classifier(X_train_norm, y_train, X_test_norm, instance.kernel_bandwidth)

    train_accuracy = float(np.mean(predictions_train == y_train)) if len(y_train) else 0.0
    test_accuracy = float(np.mean(predictions_test == y_test)) if len(y_test) else 0.0

    overlaps = np.abs(X_train_norm @ X_train_norm.T)
    expected_overlap = float(np.mean(overlaps))

    result = {
        "instance_id": instance.instance_id,
        "name": instance.name,
        "description": instance.description,
        "samples": instance.samples,
        "features": instance.features,
        "kernel_bandwidth": instance.kernel_bandwidth,
        "train_samples": int(len(X_train)),
        "test_samples": int(len(X_test)),
        "train_accuracy": train_accuracy,
        "test_accuracy": test_accuracy,
        "kernel_alignment": train_metrics["kernel_alignment"],
        "solution_norm": train_metrics["solution_norm"],
        "mean_margin": test_metrics["mean_margin"],
        "expected_overlap": expected_overlap,
    }
    return result


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    instances = load_instances(root / "instances")
    if not instances:
        raise RuntimeError("No quantum ML instances found. Add YAML files to ../instances.")

    results = [evaluate_instance(instance) for instance in instances]
    payload = {
        "problem_id": "11_quantum_machine_learning",
        "model": "kernel_ridge_classification",
        "results": results,
    }

    estimates_path = root / "estimates" / "classical_baseline.json"
    estimates_path.write_text(json.dumps(payload, indent=2))

    try:
        rel_path = estimates_path.resolve().relative_to(Path.cwd().resolve())
    except ValueError:
        rel_path = estimates_path

    print(f"✅ Classical baseline written to {rel_path}")


if __name__ == "__main__":
    main()
