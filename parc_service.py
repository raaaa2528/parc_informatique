"""Couche service : logique métier du parc, indépendante de l'affichage."""

from __future__ import annotations

import logging
from typing import Dict, List

from exceptions import SiteIntrouvableError
from models.equipement import EquipementBase
from models.site import Site

logger = logging.getLogger(__name__)


class ParcService:
    """Regroupe la logique métier appliquée à l'ensemble du parc (tous sites)."""

    def __init__(self) -> None:
        self._sites: List[Site] = []

    def ajouter_site(self, site: Site) -> None:
        """Ajoute un site déjà construit au parc."""
        self._sites.append(site)
        logger.info("Site ajouté au parc : %s.", site.nom)

    def sites(self) -> List[Site]:
        """Retourne une copie de la liste des sites du parc."""
        return list(self._sites)

    def trouver_site(self, nom_site: str) -> Site:
        """Recherche un site par son nom.

        Raises:
            SiteIntrouvableError: Si aucun site ne porte ce nom.
        """
        for site in self._sites:
            if site.nom == nom_site:
                return site
        raise SiteIntrouvableError(nom_site)

    def rapport_etat_parc(self) -> Dict[str, Dict[str, int]]:
        """Génère un rapport d'état du parc par site.

        Returns:
            Un dictionnaire {nom_site: {"actifs": n, "en_panne": n, "total": n}}.
        """
        rapport: Dict[str, Dict[str, int]] = {}
        for site in self._sites:
            rapport[site.nom] = {
                "actifs": len(site.equipements_actifs()),
                "en_panne": len(site.equipements_en_panne()),
                "total": len(site.equipements()),
            }
        return rapport

    def equipements_a_alerter(self, seuil_incidents: int) -> List[EquipementBase]:
        """Bonus : retourne les équipements dépassant un seuil d'incidents.

        Args:
            seuil_incidents: Nombre d'incidents (tous statuts confondus)
                à partir duquel un équipement doit être signalé.

        Returns:
            La liste des équipements concernés, tous sites confondus.
        """
        equipements_critiques = []
        for site in self._sites:
            for equipement in site.equipements():
                if len(equipement.incidents()) >= seuil_incidents:
                    equipements_critiques.append(equipement)
        return equipements_critiques
