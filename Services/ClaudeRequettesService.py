import os
import json
from typing import List
from dotenv import load_dotenv
import anthropic
from Classes.Classes import VilleCommune

load_dotenv()

client = anthropic.Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

SYSTEM_PROMPT = """Analyse l'impact d'événements sur la mobilité en Côte d'Ivoire.
Réponds UNIQUEMENT en JSON valide (tableau), sans texte autour, sans balises markdown.
Si l'article ne concerne AUCUN événement lié à la mobilité en Côte d'Ivoire, réponds exactement : []

Format exact si un événement est détecté :
{"chef_lieu":"","commune":"","departement":"","duree":"","evenement":"",
"flux_entrant_avant_événement":"True/False","flux_sortant_apres_événement":"True/False",
"impact_mobilite":"low/medium/high","region":"","score_confidence":0-100,
"score_importance":0-100,"source":"","sous_prefecture":"","titre":""}
Si inconnu pour un champ : "aucune"/"aucun"."""


def requete_analyse_villes(description: str, utiliser_web: bool = False) -> List[VilleCommune]:
    parametres = {
        "model": "claude-sonnet-5",
        "max_tokens": 2048,
        "system": SYSTEM_PROMPT,
        "messages": [{"role": "user", "content": description}]
    }

    if utiliser_web:
        parametres["tools"] = [{"type": "web_search_20250305", "name": "web_search"}]

    message = client.messages.create(**parametres)

    reponse_brute = "".join(
        bloc.text for bloc in message.content if bloc.type == "text"
    )

    # Nettoyage : enlève les balises markdown ```json ... ``` si Claude les ajoute quand même
    reponse_nettoyee = reponse_brute.strip()
    if reponse_nettoyee.startswith("```"):
        reponse_nettoyee = reponse_nettoyee.strip("`")
        if reponse_nettoyee.startswith("json"):
            reponse_nettoyee = reponse_nettoyee[4:]
        reponse_nettoyee = reponse_nettoyee.strip()

    if not reponse_nettoyee:
        print("Réponse vide de Claude, on ignore cet article")
        return []

    try:
        donnees_json = json.loads(reponse_nettoyee)
    except json.JSONDecodeError as e:
        print(f"JSON invalide reçu de Claude : {e}")
        print(f"Contenu reçu : {reponse_nettoyee}")
        return []

    return [VilleCommune(**item) for item in donnees_json]

def obtenir_noms_communes(villes: List[VilleCommune]) -> List[str]:
    """Extrait uniquement les noms des communes concernées."""
    return [ville.commune for ville in villes]