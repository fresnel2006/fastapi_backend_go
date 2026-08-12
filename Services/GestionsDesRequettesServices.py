from datetime import datetime, timezone




#Service de verification de la validider de la date

ancienne_requette = datetime.now(timezone.utc)


#Enregistrement l'heure de l'ancienne requette
def heure_derniere_requette():
    global ancienne_requette
    ancienne_requette = datetime.now(timezone.utc)

#Fonction pour verifier si requette a ete envoye y'a 1 jour
def requete_valider() -> bool:
    global ancienne_requette
    valider=False
    nouvelle_requette = datetime.now(timezone.utc)
    difference = nouvelle_requette - ancienne_requette

    if difference.total_seconds() < 24 * 3600:
        print("ancienne requette date : ",ancienne_requette)
        print("nouvelle requette date : ", nouvelle_requette)
        print("Moins d'un jour s'est écoulé")
        return {
            "ancienne requette date : " : ancienne_requette,
            "nouvelle requette date : " : nouvelle_requette,
            "Moins d'un jour s'est écoulé" : difference,
        }
    else:
        heure_derniere_requette()
        valider=True

    return valider




