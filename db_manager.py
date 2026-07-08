"""Persistance relationnelle SQLite : tables `equipements` et `interventions`.

Deux tables liées par une clé étrangère (interventions.equipement_id ->
equipements.id) et au moins 4 requêtes métier différentes (pas de simple
SELECT *).
"""

from __future__ import annotations

import logging
import sqlite3
from pathlib import Path
from typing import List

from models.site import Site

logger = logging.getLogger(__name__)


class GestionnaireBaseDonnees:
    """Encapsule toutes les opérations SQLite du parc réseau."""

    def __init__(self, chemin_db: str | Path) -> None:
        """Ouvre (ou crée) le fichier de base de données SQLite.

        Args:
            chemin_db: Chemin du fichier .db.
        """
        self.chemin_db = str(chemin_db)

    def _connexion(self) -> sqlite3.Connection:
        """Crée une nouvelle connexion SQLite avec les clés étrangères activées."""
        connexion = sqlite3.connect(self.chemin_db)
        connexion.execute("PRAGMA foreign_keys = ON;")
        return connexion

    def creer_tables(self) -> None:
        """Crée les tables `equipements` et `interventions` si elles n'existent pas."""
        requete_equipements = """
            CREATE TABLE IF NOT EXISTS equipements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL UNIQUE,
                ip TEXT NOT NULL,
                type_equipement TEXT NOT NULL,
                etat TEXT NOT NULL,
                site TEXT NOT NULL
            );
        """
        requete_interventions = """
            CREATE TABLE IF NOT EXISTS interventions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                equipement_id INTEGER NOT NULL,
                description TEXT NOT NULL,
                statut TEXT NOT NULL,
                date_creation TEXT NOT NULL,
                date_resolution TEXT,
                FOREIGN KEY (equipement_id) REFERENCES equipements (id)
                    ON DELETE CASCADE
            );
        """
        with self._connexion() as connexion:
            connexion.execute(requete_equipements)
            connexion.execute(requete_interventions)
        logger.info("Tables SQLite créées/vérifiées dans %s.", self.chemin_db)

    def synchroniser_depuis_sites(self, sites: List[Site]) -> None:
        """Vide puis recharge les tables à partir de l'état en mémoire des sites.

        Args:
            sites: Liste des sites (avec équipements et incidents) à persister.
        """
        with self._connexion() as connexion:
            connexion.execute("DELETE FROM interventions;")
            connexion.execute("DELETE FROM equipements;")
            for site in sites:
                for equipement in site.equipements():
                    curseur = connexion.execute(
                        """INSERT INTO equipements (nom, ip, type_equipement, etat, site)
                           VALUES (?, ?, ?, ?, ?);""",
                        (
                            equipement.nom, equipement.ip,
                            equipement.type_equipement.name, equipement.etat.name,
                            site.nom,
                        ),
                    )
                    equipement_id = curseur.lastrowid
                    for incident in equipement.incidents():
                        connexion.execute(
                            """INSERT INTO interventions
                               (equipement_id, description, statut, date_creation, date_resolution)
                               VALUES (?, ?, ?, ?, ?);""",
                            (
                                equipement_id, incident.description, incident.statut.name,
                                incident.date_creation.isoformat(),
                                incident.date_resolution.isoformat()
                                if incident.date_resolution else None,
                            ),
                        )
        logger.info("Synchronisation SQLite terminée pour %d site(s).", len(sites))

    # ---- Requêtes métier (au moins 4, aucune ne fait un simple SELECT *) ----

    def historique_par_equipement(self, nom_equipement: str) -> List[sqlite3.Row]:
        """Retourne l'historique complet des interventions d'un équipement donné."""
        requete = """
            SELECT i.id, i.description, i.statut, i.date_creation, i.date_resolution
            FROM interventions AS i
            JOIN equipements AS e ON e.id = i.equipement_id
            WHERE e.nom = ?
            ORDER BY i.date_creation;
        """
        with self._connexion() as connexion:
            connexion.row_factory = sqlite3.Row
            return connexion.execute(requete, (nom_equipement,)).fetchall()

    def equipements_en_panne_par_site(self) -> List[sqlite3.Row]:
        """Compte le nombre d'équipements en panne, groupé par site."""
        requete = """
            SELECT site, COUNT(*) AS nb_en_panne
            FROM equipements
            WHERE etat = 'EN_PANNE'
            GROUP BY site
            ORDER BY nb_en_panne DESC;
        """
        with self._connexion() as connexion:
            connexion.row_factory = sqlite3.Row
            return connexion.execute(requete).fetchall()

    def duree_moyenne_resolution(self) -> List[sqlite3.Row]:
        """Calcule la durée moyenne de résolution (en heures) par type d'équipement."""
        requete = """
            SELECT e.type_equipement,
                   AVG(
                       (julianday(i.date_resolution) - julianday(i.date_creation)) * 24.0
                   ) AS duree_moyenne_heures
            FROM interventions AS i
            JOIN equipements AS e ON e.id = i.equipement_id
            WHERE i.date_resolution IS NOT NULL
            GROUP BY e.type_equipement;
        """
        with self._connexion() as connexion:
            connexion.row_factory = sqlite3.Row
            return connexion.execute(requete).fetchall()

    def equipements_a_surveiller(self, seuil_incidents: int = 3) -> List[sqlite3.Row]:
        """Liste les équipements ayant dépassé un seuil d'incidents (bonus alerte)."""
        requete = """
            SELECT e.nom, e.site, COUNT(i.id) AS nb_incidents
            FROM equipements AS e
            JOIN interventions AS i ON i.equipement_id = e.id
            GROUP BY e.id
            HAVING COUNT(i.id) >= ?
            ORDER BY nb_incidents DESC;
        """
        with self._connexion() as connexion:
            connexion.row_factory = sqlite3.Row
            return connexion.execute(requete, (seuil_incidents,)).fetchall()
