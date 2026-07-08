"""Export CSV de la liste des incidents, avec filtrage par période."""

from __future__ import annotations

import csv
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from exceptions import DonneesInvalidesError
from models.site import Site

logger = logging.getLogger(__name__)

_ENTETES = [
    "site", "equipement", "type_equipement", "incident_id",
    "description", "statut", "date_creation", "date_resolution",
]


def exporter_incidents_csv(
    sites: List[Site],
    chemin: str | Path,
    date_debut: Optional[datetime] = None,
    date_fin: Optional[datetime] = None,
) -> int:
    """Exporte au format CSV les incidents de tous les sites, avec filtrage optionnel.

    Args:
        sites: Liste des sites dont on veut exporter les incidents.
        chemin: Chemin du fichier CSV de destination.
        date_debut: Si fourni, ne garde que les incidents créés à partir de cette date.
        date_fin: Si fourni, ne garde que les incidents créés avant cette date.

    Returns:
        Le nombre de lignes (incidents) exportées.

    Raises:
        DonneesInvalidesError: Si date_debut est postérieure à date_fin.
    """
    if date_debut and date_fin and date_debut > date_fin:
        raise DonneesInvalidesError("date_debut doit être antérieure à date_fin.")

    lignes = []
    for site in sites:
        for equipement in site.equipements():
            for incident in equipement.incidents():
                if date_debut and incident.date_creation < date_debut:
                    continue
                if date_fin and incident.date_creation > date_fin:
                    continue
                lignes.append([
                    site.nom,
                    equipement.nom,
                    equipement.type_equipement.name,
                    incident.id,
                    incident.description,
                    incident.statut.name,
                    incident.date_creation.isoformat(),
                    incident.date_resolution.isoformat() if incident.date_resolution else "",
                ])

    with open(chemin, mode="w", newline="", encoding="utf-8") as fichier:
        ecrivain = csv.writer(fichier)
        ecrivain.writerow(_ENTETES)
        ecrivain.writerows(lignes)

    logger.info("Export CSV des incidents terminé : %d ligne(s) vers %s.", len(lignes), chemin)
    return len(lignes)
