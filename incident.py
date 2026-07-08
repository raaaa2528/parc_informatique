"""Modèle représentant un incident technique lié à un équipement.

Un Incident n'a de sens qu'en tant que sous-objet d'un Equipement : il est
créé par l'équipement lui-même (voir Equipement.signaler_incident) et son
cycle de vie est entièrement lié à celui de l'équipement. C'est la relation
de COMPOSITION exigée par le cahier des charges.
"""

from __future__ import annotations

import itertools
from datetime import datetime
from typing import Optional

from exceptions import TransitionEtatInvalideError
from models.enums import StatutIncident

_compteur_incidents = itertools.count(1)


class Incident:
    """Représente un incident technique déclaré sur un équipement."""

    def __init__(self, description: str) -> None:
        """Crée un incident à l'état OUVERT.

        Args:
            description: Description courte de l'incident.
        """
        self.id: int = next(_compteur_incidents)
        self.description: str = description
        self.statut: StatutIncident = StatutIncident.OUVERT
        self.date_creation: datetime = datetime.now()
        self.date_resolution: Optional[datetime] = None

    def prendre_en_charge(self) -> None:
        """Fait passer l'incident de OUVERT à EN_COURS."""
        if self.statut is not StatutIncident.OUVERT:
            raise TransitionEtatInvalideError(
                f"Incident #{self.id} : impossible de prendre en charge "
                f"un incident au statut {self.statut.name}."
            )
        self.statut = StatutIncident.EN_COURS

    def resoudre(self) -> None:
        """Fait passer l'incident à RESOLU et fige la date de résolution."""
        if self.statut is StatutIncident.RESOLU:
            raise TransitionEtatInvalideError(
                f"Incident #{self.id} est déjà résolu."
            )
        self.statut = StatutIncident.RESOLU
        self.date_resolution = datetime.now()

    def duree_resolution_heures(self) -> Optional[float]:
        """Retourne la durée de résolution en heures, ou None si non résolu."""
        if self.date_resolution is None:
            return None
        delta = self.date_resolution - self.date_creation
        return round(delta.total_seconds() / 3600, 2)

    def to_dict(self) -> dict:
        """Sérialise l'incident en dictionnaire compatible JSON."""
        return {
            "id": self.id,
            "description": self.description,
            "statut": self.statut.name,
            "date_creation": self.date_creation.isoformat(),
            "date_resolution": (
                self.date_resolution.isoformat() if self.date_resolution else None
            ),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Incident":
        """Reconstruit un Incident à partir d'un dictionnaire JSON."""
        incident = cls(description=data["description"])
        incident.id = data["id"]
        incident.statut = StatutIncident[data["statut"]]
        incident.date_creation = datetime.fromisoformat(data["date_creation"])
        if data.get("date_resolution"):
            incident.date_resolution = datetime.fromisoformat(data["date_resolution"])
        return incident

    def __repr__(self) -> str:
        return f"Incident(#{self.id}, {self.statut.name}, '{self.description}')"
