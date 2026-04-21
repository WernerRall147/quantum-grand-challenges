"""Knowledge-based classical baseline for protein folding contact maps."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List

import numpy as np
import yaml

HYDROPHOBICITY = {
    "A": 1.8,
    "C": 2.5,
    "D": -3.5,
    "E": -3.5,
    "F": 2.8,
    "G": -0.4,
    "H": -3.2,
    "I": 4.5,
    "K": -3.9,
    "L": 3.8,
    "M": 1.9,
    "N": -3.5,
    "P": -1.6,
    "Q": -3.5,
    "R": -4.5,
    "S": -0.8,
    "T": -0.7,
    "V": 4.2,
    "W": -0.9,
    "Y": -1.3,
}

NET_CHARGE = {
    "D": -1.0,
    "E": -1.0,
    "H": 0.1,
    "K": 1.0,
    "R": 1.0,
}

HBOND_RESIDUES = {"D", "E", "H", "K", "N", "Q", "R", "S", "T", "Y"}


@dataclass(frozen=True)
class Contact:
    residue_i: int
    residue_j: int
    distance: float
    weight: float


@dataclass(frozen=True)
class ProteinInstance:
    instance_id: str
    name: str
    description: str
    sequence: str
    temperature_kelvin: float
    ph: float
    contacts: List[Contact]

    @property
    def length(self) -> int:
        return len(self.sequence)


def _parse_contacts(raw_contacts: Iterable[dict]) -> List[Contact]:
    contacts: List[Contact] = []
    for entry in raw_contacts:
        residues = entry.get("residues")
        if not residues or len(residues) != 2:
            raise ValueError("Each contact must provide a two-element 'residues' list")
        i, j = int(residues[0]), int(residues[1])
        if i <= 0 or j <= 0:
            raise ValueError("Residue indices must be positive (1-based)")
        contacts.append(
            Contact(
                residue_i=i,
                residue_j=j,
                distance=float(entry.get("distance", 6.5)),
                weight=float(entry.get("weight", 1.0)),
            )
        )
    return contacts


def load_instances(instances_dir: Path) -> List[ProteinInstance]:
    instances: List[ProteinInstance] = []
    for path in sorted(instances_dir.glob("*.yaml")):
        raw = yaml.safe_load(path.read_text())
        contacts = _parse_contacts(raw.get("contacts", []))
        instances.append(
            ProteinInstance(
                instance_id=path.stem,
                name=str(raw.get("name", path.stem)),
                description=str(raw.get("description", "")),
                sequence=str(raw["sequence"]).strip().upper(),
                temperature_kelvin=float(raw.get("temperature_kelvin", 298.0)),
                ph=float(raw.get("ph", 7.0)),
                contacts=contacts,
            )
        )
    return instances


def _residue_property(sequence: str, index: int, mapping: dict, default: float = 0.0) -> float:
    if index < 0 or index >= len(sequence):
        return default
    return float(mapping.get(sequence[index], default))


def analyze_instance(instance: ProteinInstance) -> dict:
    if instance.length == 0:
        raise ValueError("Protein sequence cannot be empty")

    hydrophobic_energy = 0.0
    electrostatic_energy = 0.0
    hydrogen_bond_bonus = 0.0
    sequence_separations: List[int] = []

    for contact in instance.contacts:
        i = contact.residue_i - 1
        j = contact.residue_j - 1
        weight = contact.weight

        hi = _residue_property(instance.sequence, i, HYDROPHOBICITY)
        hj = _residue_property(instance.sequence, j, HYDROPHOBICITY)
        hydrophobic_energy += -0.6 * weight * (hi + hj) / 2.0

        qi = _residue_property(instance.sequence, i, NET_CHARGE)
        qj = _residue_property(instance.sequence, j, NET_CHARGE)
        if contact.distance > 0:
            electrostatic_energy += 2.5 * weight * qi * qj / contact.distance

        if (
            instance.sequence[i] in HBOND_RESIDUES
            and instance.sequence[j] in HBOND_RESIDUES
            and contact.distance <= 6.5
        ):
            hydrogen_bond_bonus += 0.45 * weight

        sequence_separations.append(abs(contact.residue_i - contact.residue_j))

    contact_count = len(instance.contacts)
    contact_order = float(np.mean(sequence_separations) / instance.length) if sequence_separations else 0.0
    compactness = float(contact_count) / float(instance.length) if contact_count > 0 else 0.0
    hydrophobic_density = hydrophobic_energy / max(contact_count, 1)

    total_energy = hydrophobic_energy + electrostatic_energy - hydrogen_bond_bonus
    stability_index = -total_energy + 4.0 * compactness - 1.5 * contact_order

    return {
        "instance_id": instance.instance_id,
        "name": instance.name,
        "description": instance.description,
        "sequence_length": instance.length,
        "temperature_kelvin": instance.temperature_kelvin,
        "ph": instance.ph,
        "contacts": contact_count,
        "contact_order": contact_order,
        "compactness": compactness,
        "hydrophobic_energy": hydrophobic_energy,
        "hydrophobic_density": hydrophobic_density,
        "electrostatic_energy": electrostatic_energy,
        "hydrogen_bond_bonus": hydrogen_bond_bonus,
        "total_energy": total_energy,
        "stability_index": stability_index,
    }


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    instances = load_instances(root / "instances")
    if not instances:
        raise RuntimeError("No protein folding instances found. Add YAML files to ../instances.")

    results = [analyze_instance(instance) for instance in instances]
    payload = {
        "problem_id": "08_protein_folding",
        "model": "knowledge_based_contact_scoring",
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
