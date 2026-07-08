"""Equipement de type Switch."""

from __future__ import annotations

import logging

from exceptions import DonneesInvalidesError
from models.enums import TypeEquipement
from models.equipement import EquipementBase

logger = logging.getLogger(__name__)


class Switch(EquipementBase):
    """Commutateur réseau gérant un ensemble de ports."""

    def __init__(self, nom: str, ip: str, nombre_ports: int = 24) -> None:
        """Initialise un switch.

        Args:
            nom: Nom de l'équipement.
            ip: Adresse IP.
            nombre_ports: Nombre total de ports physiques.
        """
        super().__init__(nom, ip, TypeEquipement.SWITCH)
        if nombre_ports <= 0:
            raise DonneesInvalidesError("Le nombre de ports doit être strictement positif.")
        self.nombre_ports: int = nombre_ports
        self.ports_actifs: int = 0

    def ping(self) -> bool:
        """Teste la connectivité du switch (simulation)."""
        logger.debug("Ping du switch %s (%s).", self.nom, self.ip)
        from models.enums import EtatEquipement
        return self.etat in (EtatEquipement.ACTIF, EtatEquipement.MAINTENANCE)

    def configurer(self, **parametres: object) -> None:
        """Applique une configuration (ex: nombre de ports actifs)."""
        ports_actifs = parametres.get("ports_actifs")
        if ports_actifs is not None:
            if int(ports_actifs) > self.nombre_ports:
                raise DonneesInvalidesError(
                    f"{ports_actifs} ports actifs demandés mais seulement "
                    f"{self.nombre_ports} disponibles sur {self.nom}."
                )
            self.ports_actifs = int(ports_actifs)
        logger.info("Switch %s reconfiguré : %s", self.nom, parametres)

    def to_dict(self) -> dict:
        data = super().to_dict()
        data["nombre_ports"] = self.nombre_ports
        data["ports_actifs"] = self.ports_actifs
        return data
