from Services.evenement import KEYWORDS_WEIGHTS

# Mots-clés qui, à eux seuls, confirment un impact réel sur la mobilité.
# Un article doit contenir au moins UN de ces mots pour être retenu facilement.
CATEGORIES_FORTES = [
    "inondation", "pluie diluvienne", "éboulement", "glissement de terrain",
    "route inondée", "voie submergée", "route coupée", "voie barrée",
    "carambolage", "pont effondré", "effondrement de chaussée",
    "circulation paralysée", "circulation coupée", "trafic interrompu",
    "barrage", "barrage de pneus", "blocus", "grève des transporteurs",
    "manifestation", "émeute", "affrontement", "déguerpissement",
    "travaux routiers", "déviation", "fermeture temporaire", "embuscade",
    "vandalisme", "soulèvement", "arbre tombé", "poteau électrique abattu"
]


def calculer_score_pertinence(texte: str) -> float:
    """
    Calcule un score de pertinence. Si aucun mot-clé "fort" (impact mobilité
    certain) n'est détecté, on exige un score cumulé bien plus élevé pour
    éviter les faux positifs (ex: articles sport/culture qui contiennent
    juste "match" ou "concert" sans rapport avec la circulation).
    """
    texte_minuscule = texte.lower()
    score = 0.0
    a_un_mot_fort = False

    for mot_cle, poids in KEYWORDS_WEIGHTS.items():
        if mot_cle in texte_minuscule:
            score += poids
            if mot_cle in CATEGORIES_FORTES:
                a_un_mot_fort = True

    if not a_un_mot_fort and score < 15:
        return 0.0

    return score


def filtrer_articles_pertinents(textes: list[str], seuil: float = 6.0) -> list[str]:
    """Ne garde que les textes dont le score dépasse le seuil."""
    return [texte for texte in textes if calculer_score_pertinence(texte) >= seuil]


def trier_articles_par_score(textes: list[str]) -> list[tuple[str, float]]:
    """Retourne les textes avec leur score, triés du plus au moins pertinent (debug)."""
    resultats = [(texte, calculer_score_pertinence(texte)) for texte in textes]
    return sorted(resultats, key=lambda x: x[1], reverse=True)