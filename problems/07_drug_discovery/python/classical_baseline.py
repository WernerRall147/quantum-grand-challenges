"""Classical docking baseline for the quantum-assisted drug discovery benchmark."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List

import numpy as np
import yaml

COULOMB_CONSTANT = 332.0636  # kcal·Å·mol⁻¹·e⁻²


@dataclass(frozen=True)
class Atom:
    element: str
    charge: float
    position: np.ndarray


@dataclass(frozen=True)
class DockingInstance:
    instance_id: str
    description: str
    ligand: List[Atom]
    protein: List[Atom]
    options: Dict[str, float]


def _load_atoms(entries: Iterable[dict]) -> List[Atom]:
    atoms: List[Atom] = []
    for entry in entries:
        atoms.append(
            Atom(
                element=str(entry["element"]).upper(),
                charge=float(entry.get("charge", 0.0)),
                position=np.asarray(entry.get("position", [0.0, 0.0, 0.0]), dtype=float),
            )
        )
    return atoms


def load_instances(instances_dir: Path) -> List[DockingInstance]:
    result: List[DockingInstance] = []
    for path in sorted(instances_dir.glob("*.yaml")):
        raw = yaml.safe_load(path.read_text())
        options = raw.get("options", {})
        result.append(
            DockingInstance(
                instance_id=path.stem,
                description=str(raw.get("description", "")),
                ligand=_load_atoms(raw.get("ligand_atoms", [])),
                protein=_load_atoms(raw.get("protein_atoms", [])),
                options={
                    "lennard_jones_epsilon": float(options.get("lennard_jones_epsilon", 0.15)),
                    "lennard_jones_sigma": float(options.get("lennard_jones_sigma", 3.2)),
                    "dielectric": float(options.get("dielectric", 60.0)),
                    "cutoff": float(options.get("cutoff", 10.0)),
                },
            )
        )
    return result


def pairwise_energy(instance: DockingInstance) -> Dict[str, float]:
    epsilon = instance.options["lennard_jones_epsilon"]
    sigma = instance.options["lennard_jones_sigma"]
    dielectric = instance.options["dielectric"]
    cutoff = instance.options["cutoff"]

    sigma6 = sigma**6
    sigma12 = sigma6**2

    total_lj = 0.0
    total_coulomb = 0.0
    contacts = 0

    for lig in instance.ligand:
        for prot in instance.protein:
            displacement = lig.position - prot.position
            distance = float(np.linalg.norm(displacement))
            if distance < 1e-6 or distance > cutoff:
                continue
            inv_r = 1.0 / distance
            inv_r6 = inv_r**6
            inv_r12 = inv_r6**2

            lj = 4.0 * epsilon * (sigma12 * inv_r12 - sigma6 * inv_r6)
            coulomb = (COULOMB_CONSTANT * lig.charge * prot.charge * inv_r) / dielectric

            total_lj += lj
            total_coulomb += coulomb
            contacts += 1

    return {
        "lj_energy": total_lj,
        "coulomb_energy": total_coulomb,
        "total_energy": total_lj + total_coulomb,
        "contact_pairs": contacts,
    }


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    instances = load_instances(root / "instances")
    if not instances:
        raise RuntimeError("No docking instances found. Add YAML files to ../instances.")

    results: List[Dict[str, object]] = []
    for instance in instances:
        energy = pairwise_energy(instance)
        results.append(
            {
                "instance_id": instance.instance_id,
                "description": instance.description,
                "num_ligand_atoms": len(instance.ligand),
                "num_protein_atoms": len(instance.protein),
                **energy,
                "options": instance.options,
            }
        )

    payload = {
        "problem_id": "07_drug_discovery",
        "model": "lennard_jones_coulomb_scoring",
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
