# consequencesEvenement.py
#
# Déduit une conséquence probable et une suggestion pratique (contournement,
# anticipation, etc.) à partir du texte d'un événement, en se basant sur des
# catégories de mots-clés (même esprit que evenement.py / KEYWORDS_WEIGHTS).
#
# Sert de filet de sécurité quand Claude n'a pas rempli "consequence" /
# "suggestion" (ou n'a pas été appelé du tout, cas de la saisie manuelle
# depuis le dashboard).

import unicodedata


def _normaliser(texte: str) -> str:
    texte = unicodedata.normalize("NFKD", texte or "")
    texte = "".join(c for c in texte if not unicodedata.combining(c))
    return texte.lower()


# Chaque entrée : mots-clés déclencheurs -> (conséquence type, suggestion type)
# Ordonné du plus spécifique au plus générique ; le premier match l'emporte.
REGLES_CONSEQUENCE = [
    (
        ["inondation", "route inondee", "voie submergee", "montee des eaux",
         "crue", "quartier sous les eaux", "pluie diluvienne"],
        "Voie(s) submergée(s) ou impraticable(s) : ralentissement fort à "
        "blocage total selon le niveau d'eau.",
        "Privilégier un itinéraire sur les axes en hauteur ou goudronnés "
        "récemment ; prévoir une marge de temps importante avant la reprise "
        "du trafic normal.",
    ),
    (
        ["eboulement", "glissement de terrain", "ravinement", "crevasse",
         "effondrement de chaussee", "pont effondre"],
        "Chaussée endommagée ou coupée : passage dangereux ou impossible "
        "sur le tronçon concerné.",
        "Éviter totalement le tronçon jusqu'à confirmation de la réouverture ; "
        "informer les livreurs/chauffeurs d'un itinéraire de délestage avant "
        "leur départ.",
    ),
    (
        ["route coupee", "voie barree", "circulation coupee",
         "trafic interrompu", "circulation paralysee", "pont effondre"],
        "Circulation totalement bloquée sur l'axe concerné.",
        "Rediriger vers un axe secondaire parallèle ; avertir les clients "
        "d'un délai supplémentaire sur cette commune.",
    ),
    (
        ["carambolage", "collision", "accident", "choc frontal",
         "camion renverse", "poids lourd bloque", "moto fauchee"],
        "Ralentissement ou blocage ponctuel le temps de l'intervention des "
        "secours et du dégagement de la voie.",
        "Vérifier l'état de la voie avant de s'y engager ; prévoir un "
        "itinéraire de repli si l'accident bloque un axe à sens unique.",
    ),
    (
        ["manifestation", "emeute", "affrontement", "soulevement",
         "marche de protestation", "protestation", "sit-in",
         "marche de l'opposition", "vandalisme"],
        "Fermeture probable de la voie principale traversée par le "
        "rassemblement, avec risque de tension aux abords.",
        "Contourner le centre-ville / l'axe concerné par les voies "
        "secondaires ; éviter les créneaux de fin de journée où les "
        "rassemblements s'intensifient souvent.",
    ),
    (
        ["greve", "greve des transporteurs", "syndicat en colere",
         "syndicat de transport"],
        "Offre de transport public/collectif réduite ou absente sur la "
        "zone.",
        "Anticiper avec un moyen de transport alternatif (véhicule propre, "
        "covoiturage) et prévoir une marge sur les délais de livraison.",
    ),
    (
        ["barrage", "barrage de pneus", "blocus", "controle policier",
         "operation de police", "rafle", "embuscade"],
        "Points de contrôle ou barrages filtrants ralentissant fortement la "
        "circulation.",
        "Prévoir un temps de trajet allongé et les documents de circulation "
        "à jour ; se renseigner sur un itinéraire alternatif si le barrage "
        "persiste.",
    ),
    (
        ["deguerpissement"],
        "Perturbation locale de la circulation et de l'accès aux commerces "
        "riverains pendant l'opération.",
        "Éviter la zone pendant l'opération ; privilégier les livraisons "
        "avant ou après le créneau annoncé.",
    ),
    (
        ["travaux routiers", "deviation", "bitumage", "chantier naval",
         "reprofilage", "goudronnage", "rehabilitation de la route",
         "echangeur en chantier", "fermeture temporaire",
         "travaux d'assainissement"],
        "Voie réduite ou déviée : ralentissement prévisible sur toute la "
        "durée du chantier.",
        "Utiliser la déviation signalée si disponible ; éviter les heures "
        "de pointe sur ce tronçon tant que les travaux durent.",
    ),
    (
        ["deuil national", "paquinou", "obseques", "hommage national",
         "funerailles", "pelerinage", "inhumation", "tabaski",
         "enterrement", "ramadan", "korite", "fete du mouton", "noel",
         "reveillon", "saint-sylvestre", "nouvel an", "fete des ignames",
         "dipri", "veillee funebre", "levee de corps", "maouloud", "eid"],
        "Forte affluence et convois ponctuels : ralentissements par vagues "
        "plutôt qu'un blocage continu.",
        "Décaler les trajets non urgents en dehors des pics d'affluence "
        "(matinée et fin de journée) liés à la cérémonie.",
    ),
    (
        ["can", "festival", "carnaval", "concert", "stade", "match",
         "spectacle", "femua", "popo carnaval", "abissa", "fete de la musique",
         "foire", "meeting", "defile militaire", "fete de l'independance"],
        "Affluence importante et stationnement saturé aux abords du site de "
        "l'événement, avec pics avant/après.",
        "Prévoir un accès par un axe éloigné du site et un créneau hors des "
        "horaires d'entrée/sortie du public.",
    ),
    (
        ["embouteillage", "bouchon", "circulation alternee", "trafic dense",
         "ralentissement", "voie saturee", "embouteillage monstre",
         "stationnement anarchique", "heure de pointe"],
        "Ralentissement du trafic aux heures concernées, sans blocage total.",
        "Décaler le trajet en dehors des heures de pointe si possible, ou "
        "prévoir une marge de temps supplémentaire.",
    ),
    (
        ["arbre tombe", "poteau electrique abattu"],
        "Obstacle ponctuel sur la chaussée en attente de dégagement.",
        "Ralentir à l'approche et prévoir un léger détour si la voie est "
        "totalement bloquée par l'obstacle.",
    ),
]

CONSEQUENCE_PAR_DEFAUT = (
    "Impact sur la mobilité non catégorisé précisément — se référer à la "
    "description de l'événement.",
    "Vérifier la situation localement avant de s'engager sur la zone "
    "concernée et prévoir une marge de temps par précaution.",
)


def analyser_consequence(evenement_texte: str) -> dict:
    """Retourne {'consequence': str, 'suggestion': str} déduits du texte de
    l'événement. Renvoie un message générique si aucun mot-clé ne matche."""
    texte_normalise = _normaliser(evenement_texte)

    for mots_cles, consequence, suggestion in REGLES_CONSEQUENCE:
        if any(mot in texte_normalise for mot in mots_cles):
            return {"consequence": consequence, "suggestion": suggestion}

    consequence, suggestion = CONSEQUENCE_PAR_DEFAUT
    return {"consequence": consequence, "suggestion": suggestion}
