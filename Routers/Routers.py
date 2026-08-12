from fastapi import APIRouter

from Services.newsService import recuperer_articles_cote_ivoire, extraire_textes_articles
from Services.ClaudeRequettesService import requete_analyse_villes
from Services.firebaseService import FirebaseService
from Services.filtreEvenement import filtrer_articles_pertinents, trier_articles_par_score
import Services.GestionsDesRequettesServices as gestion_requetes

router = APIRouter()

firebase_service = FirebaseService()  # lit tout depuis .env automatiquement


@router.post("/evenements/analyser")
def analyser_actualite(mot_cle: str = ""):
    """Récupère les articles, filtre les pertinents, analyse avec Claude (sans enregistrer)."""
    articles = recuperer_articles_cote_ivoire(mot_cle)
    textes = extraire_textes_articles(articles)

    textes_pertinents = filtrer_articles_pertinents(textes, seuil=6.0)

    resultats = []
    for texte in textes_pertinents:
        villes = requete_analyse_villes(texte)
        resultats.extend(villes)

    return {
        "articles_recuperes": len(textes),
        "articles_pertinents": len(textes_pertinents),
        "villes_detectees": resultats
    }


@router.get("/evenements/scores")
def debug_scores(mot_cle: str = ""):
    """Voir le score de pertinence de chaque article avant filtrage."""
    articles = recuperer_articles_cote_ivoire(mot_cle)
    textes = extraire_textes_articles(articles)
    return trier_articles_par_score(textes)


@router.post("/evenements/enregistrer")
def analyser_et_enregistrer(mot_cle: str = ""):
    """
    Pipeline complet automatique : récupère les articles depuis NewsAPI,
    filtre les pertinents, analyse avec Claude, et enregistre dans Firebase.
    """
    articles = recuperer_articles_cote_ivoire(mot_cle)
    textes = extraire_textes_articles(articles)
    textes_pertinents = filtrer_articles_pertinents(textes, seuil=6.0)

    resultats = []
    for texte in textes_pertinents:
        villes = requete_analyse_villes(texte)
        resultats.extend(villes)

    if resultats:
        firebase_service.enregistrer_plusieurs_villes(resultats)

    return {
        "articles_recuperes": len(textes),
        "articles_pertinents": len(textes_pertinents),
        "villes_enregistrees": len(resultats),
        "villes_detectees": resultats
    }


@router.get("/sante")
def salutation():
    """Vérifie que l'API répond correctement."""
    return {"message": "Hello World"}


@router.get("/requetes/statut")
def calcul():
    """Vérifie si plus de 24h se sont écoulées depuis la dernière requête."""
    return {"valide": gestion_requetes.requete_valider()}


@router.post("/claude/test")
def test_claude():
    """Route de test : vérifie que Claude structure bien les données sur un texte connu."""
    texte_test = (
        "Route coupée à Bouaké suite à de fortes inondations ce mardi. "
        "La circulation est totalement paralysée sur l'axe principal, "
        "plusieurs quartiers sont difficiles d'accès. Les autorités locales "
        "appellent à la prudence, la situation devrait durer environ 6 heures."
    )
    villes = requete_analyse_villes(texte_test)
    return {"villes_detectees": villes}