import os
from typing import List
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, db
from Classes.Classes import VilleCommune

load_dotenv()


class FirebaseService:
    def __init__(self):
        cle_credentials_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
        database_url = os.getenv("FIREBASE_DATABASE_URL")

        if not cle_credentials_path or not database_url:
            raise ValueError(
                "FIREBASE_CREDENTIALS_PATH et FIREBASE_DATABASE_URL doivent être définis dans le .env"
            )

        if not firebase_admin._apps:  # évite de réinitialiser si déjà fait
            cred = credentials.Certificate(cle_credentials_path)
            firebase_admin.initialize_app(cred, {"databaseURL": database_url})

        self.ref = db.reference("villes_communes")

    def enregistrer_ville(self, ville: VilleCommune) -> None:
        """Enregistre ou met à jour UNE ville, identifiée par son nom de commune."""
        donnees = ville.model_dump(by_alias=True)
        self.ref.child(ville.commune).set(donnees)

    def enregistrer_plusieurs_villes(self, villes: List[VilleCommune]) -> None:
        """Enregistre ou met à jour plusieurs villes en une seule fois."""
        for ville in villes:
            self.enregistrer_ville(ville)

    def lire_ville(self, nom_commune: str) -> dict:
        """Récupère les données d'une commune précise."""
        return self.ref.child(nom_commune).get()

    def lire_toutes_les_villes(self) -> dict:
        """Récupère toutes les villes enregistrées."""
        return self.ref.get()