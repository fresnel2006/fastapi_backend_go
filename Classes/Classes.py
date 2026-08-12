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

    class Config:
        populate_by_name = True

    @field_validator("flux_entrant_avant_evenement", "flux_sortant_apres_evenement", mode="before")
    @classmethod
    def convertir_str_en_bool(cls, valeur):
        if isinstance(valeur, str):
            return valeur.lower() == "true"
        return valeur