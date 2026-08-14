from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

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
    return {"message": "Hello World"}


@router.get("/requetes/statut")
def calcul():
    return {"valide": gestion_requetes.requete_valider()}


@router.post("/claude/test")
def test_claude():
    texte_test = (
        "Route coupée à Bouaké suite à de fortes inondations ce mardi. "
        "La circulation est totalement paralysée sur l'axe principal, "
        "plusieurs quartiers sont difficiles d'accès. Les autorités locales "
        "appellent à la prudence, la situation devrait durer environ 6 heures."
    )
    villes = requete_analyse_villes(texte_test)
    return {"villes_detectees": villes}


class TexteLibreRequest(BaseModel):
    texte: str
    utiliser_web: bool = False


@router.post("/claude/test-texte")
def test_claude_texte_libre(payload: TexteLibreRequest):
    """Endpoint de test manuel : colle ton propre texte d'événement (article,
    description, etc.) et Claude l'analyse. Rien n'est enregistré dans Firebase,
    ça sert juste à vérifier le JSON que Claude renverrait (durée incluse)."""
    if not payload.texte.strip():
        raise HTTPException(status_code=400, detail="Le champ 'texte' est vide.")

    villes = requete_analyse_villes(payload.texte, utiliser_web=payload.utiliser_web)
    return {
        "nombre_evenements_detectes": len(villes),
        "villes_detectees": villes
    }


# ----------------------------------------------------------------------
# Routes consommées par le dashboard React GvipRiskDashboard
# ----------------------------------------------------------------------

@router.get("/api/referentiel/statut")
def referentiel_statut():
    """Format attendu par le frontend : { tracked_zones, total_impacted_zones_firebase }."""
    return firebase_service.referentiel_statut()


class SaisieManuelleRequest(BaseModel):
    ville_ou_commune: str
    evenement: str
    duree: str | None = None
    score_importance: int
    expire_at: str | None = None


@router.post("/api/evenements/manuel")
def enregistrer_evenement_manuel(payload: SaisieManuelleRequest):
    """Saisie manuelle d'un événement pour une commune, depuis le dashboard."""
    if not (0 <= payload.score_importance <= 100):
        raise HTTPException(status_code=400, detail="Le score doit être entre 0 et 100.")

    firebase_service.enregistrer_evenement_manuel(
        commune=payload.ville_ou_commune,
        evenement=payload.evenement,
        duree=payload.duree,
        score_importance=payload.score_importance,
        expire_at=payload.expire_at,
    )
    return {"message": "Événement enregistré", "commune": payload.ville_ou_commune}


class TexteLibreRequest(BaseModel):
    texte: str
    utiliser_web: bool = False


@router.post("/api/evenements/texte-libre")
def analyser_et_enregistrer_texte_libre(payload: TexteLibreRequest):
    """Saisie libre depuis le dashboard : l'utilisateur colle un texte
    d'événement (article, description...), Claude l'analyse (une ou
    plusieurs communes possibles, durée incluse) et le résultat est
    enregistré direct dans Firebase, comme le pipeline automatique."""
    if not payload.texte.strip():
        raise HTTPException(status_code=400, detail="Le champ 'texte' est vide.")

    villes = requete_analyse_villes(payload.texte, utiliser_web=payload.utiliser_web)

    if not villes:
        return {
            "message": "Aucun événement lié à la mobilité détecté dans ce texte.",
            "nombre_evenements_detectes": 0,
            "villes_detectees": []
        }

    firebase_service.enregistrer_plusieurs_villes(villes)

    return {
        "message": "Événement(s) analysé(s) et enregistré(s).",
        "nombre_evenements_detectes": len(villes),
        "villes_detectees": villes
    }