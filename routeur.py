"""Equipement de type Routeur."""

from __future__ import annotations

import logging

from exceptions import DonneesInvalidesError
from models.enums import TypeEquipement
from models.equipement import EquipementBase

logger = logging.getLogger(__name__)


class Routeur(EquipementBase):
    """Routeur réseau, responsable du routage inter-réseaux."""

    def __init__(self, nom: str, ip: str, table_routage_taille: int = 0) -> None:
        """Initialise un routeur.

        Args:
            nom: Nom de l'équipement.
            ip: Adresse IP.
            table_routage_taille: Nombre de routes actuellement en table.
        """
        super().__init__(nom, ip, TypeEquipement.ROUTEUR)
        if table_routage_taille < 0:
            raise DonneesInvalidesError("La taille de la table de routage ne peut être négative.")
        self.table_routage_taille: int = table_routage_taille

    def ping(self) -> bool:
        """Teste la connectivité du routeur (simulation)."""
        logger.debug("Ping du routeur %s (%s).", self.nom, self.ip)
        from models.enums import EtatEquipement
        return self.etat in (EtatEquipement.ACTIF, EtatEquipement.MAINTENANCE)

    def configurer(self, **parametres: object) -> None:
        """Applique une configuration (ex: nouvelles routes statiques)."""
        nb_routes = parametres.get("table_routage_taille")
        if nb_routes is not None:
            self.table_routage_taille = int(nb_routes)
        logger.info("Routeur %s reconfiguré : %s", self.nom, parametres)

    def to_dict(self) -> dict:
        data = super().to_dict()
        data["table_routage_taille"] = self.table_routage_taille
        return data
