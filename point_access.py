"""Equipement de type Point d'accès Wi-Fi."""

from __future__ import annotations

import logging

from exceptions import DonneesInvalidesError
from models.enums import TypeEquipement
from models.equipement import EquipementBase

logger = logging.getLogger(__name__)


class PointAcces(EquipementBase):
    """Point d'accès Wi-Fi desservant des clients sans fil."""

    def __init__(self, nom: str, ip: str, canal: int = 6, ssid: str = "ISI-DAKAR") -> None:
        """Initialise un point d'accès.

        Args:
            nom: Nom de l'équipement.
            ip: Adresse IP.
            canal: Canal radio utilisé (1-13 en 2.4GHz).
            ssid: Nom du réseau Wi-Fi diffusé.
        """
        super().__init__(nom, ip, TypeEquipement.POINT_ACCES)
        if not 1 <= canal <= 13:
            raise DonneesInvalidesError("Le canal Wi-Fi doit être compris entre 1 et 13.")
        self.canal: int = canal
        self.ssid: str = ssid
        self.clients_connectes: int = 0

    def ping(self) -> bool:
        """Teste la connectivité du point d'accès (simulation)."""
        logger.debug("Ping du point d'accès %s (%s).", self.nom, self.ip)
        from models.enums import EtatEquipement
        return self.etat in (EtatEquipement.ACTIF, EtatEquipement.MAINTENANCE)

    def configurer(self, **parametres: object) -> None:
        """Applique une configuration (ex: canal, SSID)."""
        if "canal" in parametres:
            self.canal = int(parametres["canal"])
        if "ssid" in parametres:
            self.ssid = str(parametres["ssid"])
        logger.info("Point d'accès %s reconfiguré : %s", self.nom, parametres)

    def to_dict(self) -> dict:
        data = super().to_dict()
        data["canal"] = self.canal
        data["ssid"] = self.ssid
        data["clients_connectes"] = self.clients_connectes
        return data
