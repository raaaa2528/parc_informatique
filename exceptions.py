"""Exceptions métier personnalisées pour la gestion du parc informatique réseau.

Toutes les exceptions du domaine héritent de ParcError afin de permettre,
si besoin, un traitement générique de toutes les erreurs métier tout en
gardant la possibilité de cibler un type précis.
"""


class ParcError(Exception):
    """Exception racine pour toutes les erreurs métier du parc réseau."""


class EquipementIntrouvableError(ParcError):
    """Levée lorsqu'un équipement recherché n'existe pas dans un site."""

    def __init__(self, identifiant: str) -> None:
        message = f"Aucun équipement trouvé avec l'identifiant/nom '{identifiant}'."
        super().__init__(message)
        self.identifiant = identifiant


class SiteIntrouvableError(ParcError):
    """Levée lorsqu'un site recherché n'existe pas dans le parc."""

    def __init__(self, nom_site: str) -> None:
        message = f"Aucun site trouvé avec le nom '{nom_site}'."
        super().__init__(message)
        self.nom_site = nom_site


class DonneesInvalidesError(ParcError):
    """Levée lorsqu'une donnée fournie par l'utilisateur est invalide.

    Exemple : adresse IP mal formée, nom vide, seuil négatif, etc.
    """


class TransitionEtatInvalideError(ParcError):
    """Levée lorsqu'une transition d'état d'un équipement/incident est incohérente.

    Exemple : tenter de résoudre un incident déjà résolu.
    """
