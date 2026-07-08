"""Persistance de l'état complet du parc au format JSON."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import List

from exceptions import DonneesInvalidesError
from models.enums import EtatEquipement, TypeEquipement
from models.equipement import EquipementBase
from models.firewall import Firewall
from models.incident import Incident
from models.point_acces import PointAcces
from models.routeur import Routeur
from models.site import Site
from models.switch import Switch

logger = logging.getLogger(__name__)

_CLASSES_PAR_TYPE = {
    TypeEquipement.ROUTEUR: Routeur,
    TypeEquipement.SWITCH: Switch,
    TypeEquipement.FIREWALL: Firewall,
    TypeEquipement.POINT_ACCES: PointAcces,
}


def exporter_parc(sites: List[Site], chemin: str | Path) -> None:
    """Exporte l'état complet du parc (sites + équipements) en JSON.

    Args:
        sites: Liste des sites à exporter.
        chemin: Chemin du fichier JSON de destination.
    """
    donnees = {"sites": [site.to_dict() for site in sites]}
    with open(chemin, mode="w", encoding="utf-8") as fichier:
        json.dump(donnees, fichier, ensure_ascii=False, indent=2)
    logger.info("Parc exporté en JSON vers %s (%d site(s)).", chemin, len(sites))


def _reconstruire_equipement(data: dict) -> EquipementBase:
    """Reconstruit un équipement concret à partir de son dictionnaire JSON."""
    try:
        type_eq = TypeEquipement[data["type_equipement"]]
    except KeyError as erreur:
        raise DonneesInvalidesError(
            f"Type d'équipement inconnu dans le fichier JSON : {data.get('type_equipement')}"
        ) from erreur

    classe = _CLASSES_PAR_TYPE[type_eq]

    if classe is Routeur:
        equipement = Routeur(data["nom"], data["ip"], data.get("table_routage_taille", 0))
    elif classe is Switch:
        equipement = Switch(data["nom"], data["ip"], data.get("nombre_ports", 24))
        equipement.ports_actifs = data.get("ports_actifs", 0)
    elif classe is Firewall:
        equipement = Firewall(data["nom"], data["ip"], data.get("regles", []))
    else:  # PointAcces
        equipement = PointAcces(
            data["nom"], data["ip"], data.get("canal", 6), data.get("ssid", "ISI-DAKAR")
        )
        equipement.clients_connectes = data.get("clients_connectes", 0)

    equipement.etat = EtatEquipement[data["etat"]]
    for incident_data in data.get("incidents", []):
        equipement._incidents.append(Incident.from_dict(incident_data))
    return equipement


def importer_parc(chemin: str | Path) -> List[Site]:
    """Recharge l'état complet du parc depuis un fichier JSON.

    Args:
        chemin: Chemin du fichier JSON source.

    Returns:
        Liste des sites reconstruits avec leurs équipements et incidents.

    Raises:
        FileNotFoundError: Si le fichier n'existe pas.
        DonneesInvalidesError: Si le contenu JSON est invalide.
    """
    chemin_fichier = Path(chemin)
    if not chemin_fichier.exists():
        raise FileNotFoundError(f"Fichier JSON introuvable : {chemin_fichier}")

    with open(chemin_fichier, mode="r", encoding="utf-8") as fichier:
        try:
            donnees = json.load(fichier)
        except json.JSONDecodeError as erreur:
            raise DonneesInvalidesError(f"Fichier JSON mal formé : {erreur}") from erreur

    sites: List[Site] = []
    for site_data in donnees.get("sites", []):
        site = Site(site_data["nom"], site_data["ville"])
        for equipement_data in site_data.get("equipements", []):
            site.ajouter_equipement(_reconstruire_equipement(equipement_data))
        sites.append(site)

    logger.info("Parc importé depuis %s (%d site(s)).", chemin_fichier, len(sites))
    return sites
