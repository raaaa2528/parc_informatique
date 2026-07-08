"""Classe abstraite définissant le contrat commun à tout équipement réseau."""

from __future__ import annotations

import logging
import re
from abc import ABC, abstractmethod
from typing import List

from exceptions import DonneesInvalidesError
from models.enums import EtatEquipement, TypeEquipement
from models.incident import Incident

logger = logging.getLogger(__name__)

_IPV4_REGEX = re.compile(
    r"^(25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)){3}$"
)


class EquipementBase(ABC):
    """Classe abstraite commune à tous les équipements réseau.

    Impose un contrat via les méthodes abstraites ``ping`` et ``configurer``.
    Chaque équipement CREE et POSSEDE ses propres incidents (composition) :
    la liste d'incidents ne peut être manipulée que via les méthodes de
    cette classe.
    """

    def __init__(self, nom: str, ip: str, type_equipement: TypeEquipement) -> None:
        """Initialise les attributs communs à tout équipement.

        Args:
            nom: Nom/identifiant lisible de l'équipement.
            ip: Adresse IPv4 de l'équipement.
            type_equipement: Type (Enum) de l'équipement.

        Raises:
            DonneesInvalidesError: Si le nom est vide ou l'IP mal formée.
        """
        if not nom or not nom.strip():
            raise DonneesInvalidesError("Le nom de l'équipement ne peut pas être vide.")
        if not _IPV4_REGEX.match(ip):
            raise DonneesInvalidesError(f"Adresse IP invalide : '{ip}'.")

        self.nom: str = nom.strip()
        self.ip: str = ip
        self.type_equipement: TypeEquipement = type_equipement
        self.etat: EtatEquipement = EtatEquipement.ACTIF
        self._incidents: List[Incident] = []

    @abstractmethod
    def ping(self) -> bool:
        """Simule un test de connectivité vers l'équipement."""
        raise NotImplementedError

    @abstractmethod
    def configurer(self, **parametres: object) -> None:
        """Applique une configuration spécifique à l'équipement."""
        raise NotImplementedError

    def signaler_incident(self, description: str) -> Incident:
        """Crée un nouvel incident possédé par cet équipement (composition).

        Args:
            description: Description du problème rencontré.

        Returns:
            L'incident nouvellement créé.

        Raises:
            DonneesInvalidesError: Si la description est vide.
        """
        if not description or not description.strip():
            raise DonneesInvalidesError("La description de l'incident est obligatoire.")
        incident = Incident(description=description.strip())
        self._incidents.append(incident)
        self.etat = EtatEquipement.EN_PANNE
        logger.warning(
            "Incident #%s signalé sur %s (%s) : %s",
            incident.id, self.nom, self.ip, description,
        )
        return incident

    def incidents(self) -> List[Incident]:
        """Retourne une copie de la liste des incidents de l'équipement."""
        return list(self._incidents)

    def nombre_incidents_ouverts(self) -> int:
        """Compte les incidents non résolus (OUVERT ou EN_COURS)."""
        from models.enums import StatutIncident
        return sum(
            1 for i in self._incidents if i.statut is not StatutIncident.RESOLU
        )

    def changer_etat(self, nouvel_etat: EtatEquipement) -> None:
        """Change l'état de l'équipement et journalise la transition."""
        ancien = self.etat
        self.etat = nouvel_etat
        logger.info("%s : état changé de %s à %s.", self.nom, ancien.name, nouvel_etat.name)

    def to_dict(self) -> dict:
        """Sérialise les attributs communs (les sous-classes complètent)."""
        return {
            "nom": self.nom,
            "ip": self.ip,
            "type_equipement": self.type_equipement.name,
            "etat": self.etat.name,
            "incidents": [i.to_dict() for i in self._incidents],
        }

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(nom={self.nom!r}, ip={self.ip!r}, etat={self.etat.name})"
