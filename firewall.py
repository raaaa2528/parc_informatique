"""Equipement de type Firewall."""

from __future__ import annotations

import logging
from typing import List

from models.enums import TypeEquipement
from models.equipement import EquipementBase

logger = logging.getLogger(__name__)


class Firewall(EquipementBase):
    """Pare-feu réseau appliquant des règles de filtrage."""

    def __init__(self, nom: str, ip: str, regles: List[str] | None = None) -> None:
        """Initialise un firewall.

        Args:
            nom: Nom de l'équipement.
            ip: Adresse IP.
            regles: Liste initiale de règles de filtrage (facultatif).
        """
        super().__init__(nom, ip, TypeEquipement.FIREWALL)
        self.regles: List[str] = list(regles) if regles else []

    def ping(self) -> bool:
        """Teste la connectivité du firewall (simulation)."""
        logger.debug("Ping du firewall %s (%s).", self.nom, self.ip)
        from models.enums import EtatEquipement
        return self.etat in (EtatEquipement.ACTIF, EtatEquipement.MAINTENANCE)

    def configurer(self, **parametres: object) -> None:
        """Ajoute des règles de filtrage à la configuration."""
        nouvelles_regles = parametres.get("regles")
        if nouvelles_regles:
            self.regles.extend(nouvelles_regles)
        logger.info("Firewall %s reconfiguré, %d règle(s) au total.", self.nom, len(self.regles))

    def to_dict(self) -> dict:
        data = super().to_dict()
        data["regles"] = self.regles
        return data
