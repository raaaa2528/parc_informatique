"""Modèle représentant un site géographique hébergeant des équipements.

Un Site reçoit des objets Equipement créés en dehors de lui (par exemple
dans main.py ou dans un service). Le site ne crée pas lui-même ses
équipements et leur cycle de vie ne dépend pas du site : c'est la relation
d'AGREGATION exigée par le cahier des charges.
"""

from __future__ import annotations

from typing import List

from exceptions import DonneesInvalidesError, EquipementIntrouvableError
from models.enums import EtatEquipement
from models.equipement import EquipementBase


class Site:
    """Site géographique hébergeant un ensemble d'équipements réseau."""

    def __init__(self, nom: str, ville: str) -> None:
        """Initialise un site.

        Args:
            nom: Nom du site (ex: "Siège Dakar").
            ville: Ville où se trouve le site.

        Raises:
            DonneesInvalidesError: Si le nom ou la ville est vide.
        """
        if not nom or not nom.strip():
            raise DonneesInvalidesError("Le nom du site ne peut pas être vide.")
        if not ville or not ville.strip():
            raise DonneesInvalidesError("La ville du site ne peut pas être vide.")
        self.nom: str = nom.strip()
        self.ville: str = ville.strip()
        self._equipements: List[EquipementBase] = []

    def ajouter_equipement(self, equipement: EquipementBase) -> None:
        """Ajoute un équipement existant au site (agrégation).

        Args:
            equipement: Instance déjà créée d'une sous-classe d'EquipementBase.

        Raises:
            DonneesInvalidesError: Si l'objet n'est pas un EquipementBase
                ou si un équipement de même nom existe déjà sur le site.
        """
        if not isinstance(equipement, EquipementBase):
            raise DonneesInvalidesError("L'objet ajouté doit être un EquipementBase.")
        if any(e.nom == equipement.nom for e in self._equipements):
            raise DonneesInvalidesError(
                f"Un équipement nommé '{equipement.nom}' existe déjà sur le site {self.nom}."
            )
        self._equipements.append(equipement)

    def retirer_equipement(self, nom_equipement: str) -> None:
        """Retire un équipement du site par son nom.

        Raises:
            EquipementIntrouvableError: Si aucun équipement ne porte ce nom.
        """
        equipement = self.trouver_equipement(nom_equipement)
        self._equipements.remove(equipement)

    def trouver_equipement(self, nom_equipement: str) -> EquipementBase:
        """Recherche un équipement par son nom.

        Raises:
            EquipementIntrouvableError: Si aucun équipement ne porte ce nom.
        """
        for equipement in self._equipements:
            if equipement.nom == nom_equipement:
                return equipement
        raise EquipementIntrouvableError(nom_equipement)

    def equipements(self) -> List[EquipementBase]:
        """Retourne une copie de la liste des équipements du site."""
        return list(self._equipements)

    def equipements_en_panne(self) -> List[EquipementBase]:
        """Retourne les équipements actuellement en panne sur ce site."""
        return [e for e in self._equipements if e.etat is EtatEquipement.EN_PANNE]

    def equipements_actifs(self) -> List[EquipementBase]:
        """Retourne les équipements actuellement actifs sur ce site."""
        return [e for e in self._equipements if e.etat is EtatEquipement.ACTIF]

    def to_dict(self) -> dict:
        """Sérialise le site et ses équipements en dictionnaire JSON."""
        return {
            "nom": self.nom,
            "ville": self.ville,
            "equipements": [e.to_dict() for e in self._equipements],
        }

    def __repr__(self) -> str:
        return f"Site(nom={self.nom!r}, ville={self.ville!r}, nb_equipements={len(self._equipements)})"
