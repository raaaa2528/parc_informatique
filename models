"""Enumérations utilisées dans le domaine du parc informatique réseau."""

from enum import Enum, auto


class TypeEquipement(Enum):
    """Nature d'un équipement réseau."""

    ROUTEUR = "ROUTEUR"
    SWITCH = "SWITCH"
    FIREWALL = "FIREWALL"
    POINT_ACCES = "POINT_ACCES"


class EtatEquipement(Enum):
    """Etat opérationnel courant d'un équipement réseau."""

    ACTIF = "ACTIF"
    INACTIF = "INACTIF"
    EN_PANNE = "EN_PANNE"
    MAINTENANCE = "MAINTENANCE"


class StatutIncident(Enum):
    """Cycle de vie d'un incident technique déclaré sur un équipement."""

    OUVERT = auto()
    EN_COURS = auto()
    RESOLU = auto()
