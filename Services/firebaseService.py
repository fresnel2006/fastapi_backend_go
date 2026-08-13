import os
import json
import re
import unicodedata
from datetime import datetime, timedelta, timezone
from typing import List
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, db
from Classes.Classes import VilleCommune

load_dotenv()


def normaliser_cle_commune(commune: str) -> str:
    """Transforme un nom de commune en clé Firebase stable et unique par ville,
    peu importe la casse, les accents ou les espaces utilisés d'une écriture à
    l'autre (Claude ne renvoie pas toujours exactement la même orthographe pour
    la même ville, ex: 'Bouaké' / 'Bouake' / 'bouaké '). Sans ça, chaque petite
    variation créait un NOUVEAU nœud Firebase au lieu de mettre à jour le bon."""
    if not commune:
        return "inconnue"
    texte = unicodedata.normalize("NFKD", commune.strip())
    texte = "".join(c for c in texte if not unicodedata.combining(c))  # retire les accents
    texte = texte.lower()
    texte = re.sub(r"[^a-z0-9]+", "_", texte).strip("_")
    return texte or "inconnue"


def score_vers_impact(score: int) -> str:
    """Mêmes seuils que le frontend (severityFromScore côté React)."""
    if score >= 80:
        return "CRITICAL"
    if score >= 50:
        return "MEDIUM"
    return "LOW"


_DUREE_PATTERN = re.compile(
    r"(\d+(?:[.,]\d+)?)\s*(minutes?|min|heures?|h|jours?|j|semaines?|sem|mois|ans?|ann[ée]es?)",
    re.IGNORECASE,
)


def _duree_en_ms(duree: str | None):
    """Même logique que parseDureeToMs côté frontend, pour rester cohérent."""
    if not duree:
        return None
    match = _DUREE_PATTERN.search(duree.strip().lower())
    if not match:
        return None
    try:
        valeur = float(match.group(1).replace(",", "."))
    except ValueError:
        return None

    unite = match.group(2)
    MINUTE = 60_000
    HEURE = 60 * MINUTE
    JOUR = 24 * HEURE

    if unite.startswith("min"):
        return valeur * MINUTE
    if unite.startswith("h"):
        return valeur * HEURE
    if unite.startswith("j"):
        return valeur * JOUR
    if unite.startswith("sem"):
        return valeur * 7 * JOUR
    if unite.startswith("mois"):
        return valeur * 30 * JOUR
    if unite.startswith("an"):
        return valeur * 365 * JOUR
    return None


def calculer_expire_at(duree: str | None) -> str | None:
    """Calcule une échéance ISO 8601 (UTC) à partir d'un texte de durée libre
    ('3 jours', '12 heures'...). C'est cette valeur, calculée UNE SEULE FOIS
    côté backend et stockée, qui fait foi — plus aucun recalcul côté client
    à partir du texte, qui pouvait varier légèrement d'une analyse à l'autre
    et donc faire redémarrer le compte à rebours à chaque fois."""
    ms = _duree_en_ms(duree)
    if not ms:
        return None
    return (datetime.now(timezone.utc) + timedelta(milliseconds=ms)).isoformat()


class FirebaseService:
    def __init__(self):
        credentials_json = os.getenv("FIREBASE_CREDENTIALS_JSON")
        credentials_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
        database_url = os.getenv("FIREBASE_DATABASE_URL")

        if not database_url:
            raise ValueError("FIREBASE_DATABASE_URL doit être défini")

        if not firebase_admin._apps:
            if credentials_json:
                cred_dict = json.loads(credentials_json)
                cred = credentials.Certificate(cred_dict)
            elif credentials_path:
                cred = credentials.Certificate(credentials_path)
            else:
                raise ValueError(
                    "FIREBASE_CREDENTIALS_JSON (Vercel) ou FIREBASE_CREDENTIALS_PATH (local) "
                    "doit être défini"
                )
            firebase_admin.initialize_app(cred, {"databaseURL": database_url})

        self.ref = db.reference("villes_communes")

    def enregistrer_ville(self, ville: VilleCommune) -> None:
        """Écrit l'état courant d'une commune (pipeline automatique News+Claude).
        Calcule aussi expire_at à partir de la durée détectée, pour que le
        compte à rebours affiché soit fiable dès la première écriture."""
        donnees = ville.model_dump(by_alias=True)
        expire_at = calculer_expire_at(donnees.get("duree"))
        if expire_at:
            donnees["expire_at"] = expire_at
        donnees["updated_at"] = datetime.now(timezone.utc).isoformat()
        cle_commune = normaliser_cle_commune(ville.commune)
        self.ref.child(cle_commune).set(donnees)

    def enregistrer_plusieurs_villes(self, villes: List[VilleCommune]) -> None:
        for ville in villes:
            self.enregistrer_ville(ville)

    def lire_ville(self, nom_commune: str) -> dict:
        return self.ref.child(nom_commune).get()

    def lire_toutes_les_villes(self) -> dict:
        return self.ref.get()

    # ------------------------------------------------------------------
    # Support du dashboard GVIP (référentiel + saisie manuelle)
    # ------------------------------------------------------------------

    def referentiel_statut(self) -> dict:
        """Formate toutes les zones Firebase au format attendu par le frontend.
        Filtre côté backend les événements dont l'échéance (expire_at) est
        déjà dépassée, pour ne plus jamais renvoyer de "vieille" info."""
        toutes_les_villes = self.lire_toutes_les_villes() or {}

        if isinstance(toutes_les_villes, list):
            items = [(str(i), data) for i, data in enumerate(toutes_les_villes) if data]
        elif isinstance(toutes_les_villes, dict):
            items = list(toutes_les_villes.items())
        else:
            items = []

        maintenant = datetime.now(timezone.utc)
        tracked_zones = []
        for commune_key, data in items:
            if not isinstance(data, dict):
                continue

            expire_at = data.get("expire_at")
            if expire_at:
                try:
                    if datetime.fromisoformat(expire_at) <= maintenant:
                        continue  # événement expiré : on ne l'affiche plus
                except ValueError:
                    pass  # format inattendu : on affiche quand même, au pire

            score = int(data.get("score_importance") or 0)
            tracked_zones.append({
                "commune": data.get("commune", commune_key),
                "region": data.get("region", "INCONNUE"),
                "evenement_actif": data.get("evenement", "—"),
                "duree": data.get("duree"),
                "expire_at": expire_at,
                "score_importance": score,
                "impact_mobilite": data.get("impact_mobilite") or score_vers_impact(score),
            })

        return {
            "tracked_zones": tracked_zones,
            "total_impacted_zones_firebase": len(tracked_zones),
        }

    def enregistrer_evenement_manuel(
        self,
        commune: str,
        evenement: str,
        duree: str | None,
        score_importance: int,
        expire_at: str | None,
    ) -> None:
        """Enregistre une saisie manuelle.

        - Calcule expire_at côté backend si le frontend n'en a pas fourni de
          valide (source de vérité unique, ne dépend plus du texte affiché).
        - Garde un HISTORIQUE (push, jamais écrasé) de chaque saisie faite
          pour cette commune, en plus de la mise à jour de l'état "courant"
          affiché dans le tableau (update partiel, ne touche pas chef_lieu /
          departement / etc. déjà enregistrés par le pipeline automatique).
        """
        expire_at_final = expire_at or calculer_expire_at(duree)
        horodatage = datetime.now(timezone.utc).isoformat()

        donnees_courantes = {
            "commune": commune,
            "evenement": evenement,
            "duree": duree or "",
            "score_importance": score_importance,
            "impact_mobilite": score_vers_impact(score_importance),
            "expire_at": expire_at_final,
            "updated_at": horodatage,
        }

        # Même clé normalisée que le pipeline automatique : une saisie manuelle
        # pour "Bouaké" doit mettre à jour le même nœud que celui déjà créé
        # par l'analyse automatique, pas en créer un nouveau.
        cle_commune = normaliser_cle_commune(commune)

        # Historique : chaque saisie CRÉE une nouvelle entrée, elle ne
        # remplace jamais un événement précédent pour cette commune.
        self.ref.child(cle_commune).child("historique").push({
            **donnees_courantes,
            "created_at": horodatage,
            "source": "manuel",
        })

        # État courant affiché dans le tableau du dashboard.
        self.ref.child(cle_commune).update(donnees_courantes)