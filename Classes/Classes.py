from typing import List
from pydantic import BaseModel, Field, field_validator


class VilleCommune(BaseModel):
    chef_lieu: str
    commune: str
    departement: str
    duree: str
    evenement: str
    flux_entrant_avant_evenement: bool = Field(alias="flux_entrant_avant_événement")
    flux_sortant_apres_evenement: bool = Field(alias="flux_sortant_apres_événement")
    impact_mobilite: str
    region: str
    score_confidence: int
    score_importance: int
    source: str
    sous_prefecture: str
    titre: str
    # Conséquence probable sur la mobilité + suggestion de contournement.
    # Remplis par Claude si possible, sinon complétés côté backend via
    # Services/consequencesEvenement.py (voir firebaseService.enregistrer_ville).
    consequence: str = ""
    suggestion: str = ""
    # Communes/départements voisins susceptibles d'être impactés par
    # ricochet (trafic dévié, affluence reportée, etc.).
    villes_voisines_impactees: List[str] = Field(default_factory=list)

    class Config:
        populate_by_name = True

    @field_validator("flux_entrant_avant_evenement", "flux_sortant_apres_evenement", mode="before")
    @classmethod
    def convertir_str_en_bool(cls, valeur):
        if isinstance(valeur, str):
            return valeur.lower() == "true"
        return valeur

    @field_validator("consequence", "suggestion", mode="before")
    @classmethod
    def nettoyer_texte_libre(cls, valeur):
        """Claude renvoie parfois 'aucune'/'aucun' quand il ne sait pas :
        on normalise ça en chaîne vide pour laisser place au fallback."""
        if isinstance(valeur, str) and valeur.strip().lower() in ("aucune", "aucun", ""):
            return ""
        return valeur or ""

    @field_validator("villes_voisines_impactees", mode="before")
    @classmethod
    def parser_villes_voisines(cls, valeur):
        """Claude peut renvoyer une liste, une chaîne séparée par des
        virgules, ou 'aucune' : on normalise en liste de noms propres."""
        if valeur is None:
            return []
        if isinstance(valeur, str):
            if valeur.strip().lower() in ("aucune", "aucun", ""):
                return []
            return [v.strip() for v in valeur.split(",") if v.strip()]
        if isinstance(valeur, list):
            return [str(v).strip() for v in valeur if str(v).strip()]
        return []