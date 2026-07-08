"""Script de démonstration du projet 'Gestion de parc informatique réseau'.

Exécute les scénarios principaux exigés par le sujet A :
1. Création de sites avec équipements mixtes.
2. Enregistrement d'incidents (création, prise en charge, résolution).
3. Rapport d'état du parc par site.
4. Export/rechargement JSON.
5. Export CSV des incidents.
6. Persistance et requêtes SQLite.
7. Bonus : alerte sur seuil d'incidents.
"""

from __future__ import annotations

import logging
from pathlib import Path

from exceptions import ParcError
from models.firewall import Firewall
from models.point_acces import PointAcces
from models.routeur import Routeur
from models.site import Site
from models.switch import Switch
from persistence.csv_manager import exporter_incidents_csv
from persistence.db_manager import GestionnaireBaseDonnees
from persistence.json_manager import exporter_parc, importer_parc
from services.parc_service import ParcService

DOSSIER_DATA = Path(__file__).parent / "data"
DOSSIER_EXPORTS = Path(__file__).parent / "exports"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("main")


def construire_parc_demo() -> ParcService:
    """Construit un parc de démonstration avec 2 sites et des équipements mixtes."""
    service = ParcService()

    site_dakar = Site("Siège Dakar", "Dakar")
    site_thies = Site("Agence Thiès", "Thiès")

    # Site Dakar : au moins 3 équipements
    routeur_dakar = Routeur("RT-DKR-01", "10.0.0.1", table_routage_taille=12)
    switch_dakar = Switch("SW-DKR-01", "10.0.0.2", nombre_ports=48)
    firewall_dakar = Firewall("FW-DKR-01", "10.0.0.3", regles=["deny all", "allow 443"])
    site_dakar.ajouter_equipement(routeur_dakar)
    site_dakar.ajouter_equipement(switch_dakar)
    site_dakar.ajouter_equipement(firewall_dakar)

    # Site Thiès : au moins 3 équipements, types mixtes
    routeur_thies = Routeur("RT-THS-01", "10.1.0.1", table_routage_taille=6)
    point_acces_thies = PointAcces("AP-THS-01", "10.1.0.4", canal=11, ssid="ISI-THIES")
    switch_thies = Switch("SW-THS-01", "10.1.0.2", nombre_ports=24)
    site_thies.ajouter_equipement(routeur_thies)
    site_thies.ajouter_equipement(point_acces_thies)
    site_thies.ajouter_equipement(switch_thies)

    service.ajouter_site(site_dakar)
    service.ajouter_site(site_thies)

    # Cycle de vie complet de quelques incidents
    incident_1 = switch_dakar.signaler_incident("Port 12 ne transmet plus de données.")
    incident_1.prendre_en_charge()
    incident_1.resoudre()

    incident_2 = firewall_dakar.signaler_incident("Règle NAT mal appliquée après reboot.")
    incident_2.prendre_en_charge()

    switch_dakar.signaler_incident("Redémarrage intempestif du switch.")
    routeur_thies.signaler_incident("Perte de connectivité WAN intermittente.")

    return service


def afficher_rapport(service: ParcService) -> None:
    """Affiche le rapport d'état du parc par site (couche affichage)."""
    print("\n=== Rapport d'état du parc ===")
    for nom_site, stats in service.rapport_etat_parc().items():
        print(f"- {nom_site} : {stats['actifs']} actif(s), "
              f"{stats['en_panne']} en panne / {stats['total']} au total")


def main() -> None:
    """Point d'entrée du script de démonstration."""
    DOSSIER_DATA.mkdir(exist_ok=True)
    DOSSIER_EXPORTS.mkdir(exist_ok=True)

    try:
        service = construire_parc_demo()
        afficher_rapport(service)

        # 4. Export puis rechargement JSON
        chemin_json = DOSSIER_DATA / "parc.json"
        exporter_parc(service.sites(), chemin_json)
        sites_recharges = importer_parc(chemin_json)
        print(f"\nParc rechargé depuis JSON : {len(sites_recharges)} site(s), "
              f"{sum(len(s.equipements()) for s in sites_recharges)} équipement(s).")

        # 5. Export CSV des incidents
        chemin_csv = DOSSIER_EXPORTS / "incidents.csv"
        nb_lignes = exporter_incidents_csv(service.sites(), chemin_csv)
        print(f"Export CSV : {nb_lignes} incident(s) écrits dans {chemin_csv.name}.")

        # 6. Persistance SQLite + requêtes métier
        chemin_db = DOSSIER_DATA / "parc.db"
        bdd = GestionnaireBaseDonnees(chemin_db)
        bdd.creer_tables()
        bdd.synchroniser_depuis_sites(service.sites())

        print("\n=== Historique de l'équipement SW-DKR-01 ===")
        for ligne in bdd.historique_par_equipement("SW-DKR-01"):
            print(dict(ligne))

        print("\n=== Équipements en panne par site ===")
        for ligne in bdd.equipements_en_panne_par_site():
            print(dict(ligne))

        print("\n=== Durée moyenne de résolution par type d'équipement (heures) ===")
        for ligne in bdd.duree_moyenne_resolution():
            print(dict(ligne))

        # 7. Bonus : alerte sur seuil d'incidents
        print("\n=== Équipements à surveiller (seuil = 2 incidents) ===")
        for equipement in service.equipements_a_alerter(seuil_incidents=2):
            print(f"- {equipement.nom} : {len(equipement.incidents())} incident(s)")

    except ParcError as erreur:
        logger.error("Erreur métier : %s", erreur)
    except (FileNotFoundError, OSError) as erreur:
        logger.error("Erreur fichier : %s", erreur)


if __name__ == "__main__":
    main()
