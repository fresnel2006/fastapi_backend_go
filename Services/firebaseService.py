import os
import json
from typing import List
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, db
from Classes.Classes import VilleCommune

load_dotenv()


class FirebaseService:
    def __init__(self):
        credentials_json = os.getenv("FIREBASE_CREDENTIALS_JSON")
        credentials_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
        database_url = os.getenv("FIREBASE_DATABASE_URL")

        if not database_url:
            raise ValueError("FIREBASE_DATABASE_URL doit être défini")

        if not firebase_admin._apps:  # évite de réinitialiser si déjà fait
            if credentials_json:
                # Cas Vercel : le contenu du fichier de credentials est stocké
                # directement dans une variable d'environnement (chaîne JSON).
                cred_dict = json.loads(credentials_json)
                cred = credentials.Certificate(cred_dict)
            elif credentials_path:
                # Cas local : on lit le fichier .json sur le disque.
                cred = credentials.Certificate(credentials_path)
            else:
                raise ValueError(
                    "FIREBASE_CREDENTIALS_JSON (Vercel) ou FIREBASE_CREDENTIALS_PATH (local) "
                    "doit être défini"
                )
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