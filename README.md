# Gestion de parc informatique réseau

Projet de fin de semestre — Module **POO & Persistance des données**
ISI Dakar — Licence 2 Réseaux Informatiques — Année 2025-2026
Formateur : M. HAMANE — Sujet A

## Description

Ce projet modélise la gestion du parc informatique réseau d'une entreprise multi-sites. Un
service informatique gère plusieurs **sites** géographiques, chaque site hébergeant des
**équipements réseau** de natures différentes (routeurs, switchs, firewalls, points d'accès
Wi-Fi). Chaque équipement conserve son propre historique d'**incidents** techniques, de leur
création à leur résolution.

Le projet couvre :

- une architecture orientée objet avec classe abstraite, héritage, Enum, agrégation et
  composition ;
- la persistance des données sous trois formes : JSON, CSV et base de données SQLite ;
- une gestion rigoureuse des exceptions, du logging et des bonnes pratiques Python (PEP8,
  type hints, docstrings).

### Fonctionnalités

1. Création de plusieurs sites avec des équipements mixtes (au moins 3 par site).
2. Cycle de vie complet d'un incident : signalement, prise en charge, résolution.
3. Rapport d'état du parc par site (équipements actifs / en panne).
4. Export et rechargement complet de l'état du parc au format JSON.
5. Export CSV des incidents, avec filtrage par période.
6. Persistance relationnelle SQLite avec requêtes métier (historique par équipement,
   pannes par site, durée moyenne de résolution).
7. **Bonus** : alerte automatique sur les équipements dépassant un seuil d'incidents.

## Architecture orientée objet

```
EquipementBase (ABC)
├── ping()          [abstraite]
├── configurer()    [abstraite]
├── Routeur
├── Switch
├── Firewall
└── PointAcces
```

- **Enum** : `TypeEquipement`, `EtatEquipement` (ACTIF, INACTIF, EN_PANNE, MAINTENANCE),
  `StatutIncident` (OUVERT, EN_COURS, RESOLU).
- **Agrégation** : `Site` reçoit des objets `Equipement` créés en dehors de lui, via
  `ajouter_equipement()`. Le cycle de vie de l'équipement ne dépend pas du site.
- **Composition** : chaque `Equipement` crée et possède ses propres objets `Incident` via
  `signaler_incident()`. Un incident n'existe pas sans son équipement.

## Structure du projet

```
sujet_A_parc_reseau/
├── main.py                     # Script de démonstration (point d'entrée)
├── exceptions.py                # Exceptions métier personnalisées
├── models/
│   ├── enums.py                 # TypeEquipement, EtatEquipement, StatutIncident
│   ├── equipement.py            # Classe abstraite EquipementBase
│   ├── routeur.py                # Sous-classe Routeur
│   ├── switch.py                 # Sous-classe Switch
│   ├── firewall.py               # Sous-classe Firewall
│   ├── point_acces.py            # Sous-classe PointAcces
│   ├── incident.py               # Modèle Incident (composition)
│   └── site.py                   # Modèle Site (agrégation)
├── services/
│   └── parc_service.py          # Logique métier (rapports, alertes)
├── persistence/
│   ├── json_manager.py          # Export/import JSON
│   ├── csv_manager.py           # Export CSV des incidents
│   └── db_manager.py            # Persistance SQLite + requêtes métier
├── data/                         # Fichiers générés : parc.json, parc.db
├── exports/                      # Fichiers générés : incidents.csv
├── requirements.txt
├── CONTRIBUTIONS.md
└── README.md
```

## Installation

Prérequis : **Python 3.10+** (aucune dépendance externe : le projet n'utilise que la
bibliothèque standard).

```bash
git clone <url_du_depot>
cd sujet_A_parc_reseau
pip install -r requirements.txt
```

## Utilisation

Lancer le script de démonstration, qui exécute l'ensemble des scénarios attendus (création
du parc, incidents, rapports, exports JSON/CSV, requêtes SQLite, alertes) :

```bash
python3 main.py
```

À l'exécution, le script :

- affiche le rapport d'état du parc par site ;
- exporte l'état complet du parc dans `data/parc.json`, puis le recharge pour vérifier
  l'intégrité de la sérialisation ;
- exporte les incidents dans `exports/incidents.csv` ;
- crée/synchronise la base `data/parc.db` et affiche le résultat de plusieurs requêtes
  métier (historique par équipement, pannes par site, durée moyenne de résolution,
  équipements à surveiller).

## Auteurs

Voir [CONTRIBUTIONS.md](./CONTRIBUTIONS.md) pour la répartition détaillée du travail entre
les membres du groupe.
