import os
import requests
from typing import List
from dotenv import load_dotenv

load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
NEWS_API_URL = "https://newsapi.org/v2/everything"


def recuperer_articles_cote_ivoire(mot_cle: str = "", nombre_resultats: int = 20) -> List[dict]:
    """
    Récupère les articles de presse récents concernant la Côte d'Ivoire.
    mot_cle : permet d'affiner la recherche (ex: "concert Abidjan", "route", "événement")
    """
    requete = '"Côte d\'Ivoire" OR "Abidjan"'
    if mot_cle:
        requete += f" AND {mot_cle}"

    params = {
        "q": requete,
        "language": "fr",
        "sortBy": "publishedAt",
        "pageSize": nombre_resultats,
        "apiKey": NEWS_API_KEY
    }

    reponse = requests.get(NEWS_API_URL, params=params)
    reponse.raise_for_status()

    donnees = reponse.json()
    return donnees.get("articles", [])


def extraire_textes_articles(articles: List[dict]) -> List[str]:
    """Extrait uniquement titre + description de chaque article, prêt à envoyer à Claude."""
    textes = []
    for article in articles:
        titre = article.get("title", "")
        description = article.get("description", "") or ""
        textes.append(f"{titre}. {description}")
    return textes