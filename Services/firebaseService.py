import os
import json
from typing import List
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, db
from Classes.Classes import VilleCommune

load_dotenv()


def score_vers_impact(score: int) -> str:
    """Mêmes seuils que le frontend (severityFromScore côté React)."""
    if score >= 80:
        return "CRITICAL"
    if score >= 50:
        return "MEDIUM"
    return "LOW"


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
        donnees = ville.model_dump(by_alias=True)
        self.ref.child(ville.commune).set(donnees)

    def enregistrer_plusieurs_villes(self, villes: List[VilleCommune]) -> None:
        for ville in villes:
            self.enregistrer_ville(ville)

    def lire_ville(self, nom_commune: str) -> dict:
        return self.ref.child(nom_commune).get()

    def lire_toutes_les_villes(self) -> dict:
        return self.ref.get()

    # ------------------------------------------------------------------
    # Nouveau : support du dashboard GVIP (référentiel + saisie manuelle)
    # ------------------------------------------------------------------

    def referentiel_statut(self) -> dict:
        """Formate toutes les zones Firebase au format attendu par le frontend
        GvipRiskDashboard (tracked_zones + total_impacted_zones_firebase)."""
        toutes_les_villes = self.lire_toutes_les_villes() or {}

        tracked_zones = []
        for commune_key, data in toutes_les_villes.items():
            if not isinstance(data, dict):
                continue
            score = int(data.get("score_importance") or 0)
            tracked_zones.append({
                "commune": data.get("commune", commune_key),
                "region": data.get("region", "INCONNUE"),
                "evenement_actif": data.get("evenement", "—"),
                "duree": data.get("duree"),
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
        """Mise à jour PARTIELLE (update, pas set) : ne remplace pas les
        champs déjà enregistrés par le pipeline automatique pour cette
        commune (chef_lieu, region, etc.) s'ils existent déjà."""
        donnees = {
            "commune": commune,
            "evenement": evenement,
            "duree": duree or "",
            "score_importance": score_importance,
            "impact_mobilite": score_vers_impact(score_importance),
        }
        if expire_at:
            donnees["expire_at"] = expire_at

        self.ref.child(commune).update(donnees)