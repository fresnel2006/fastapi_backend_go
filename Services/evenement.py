# evenement.py

# 📊 DICTIONNAIRE SÉMANTIQUE XXL ÉTENDU (140+ MOTS-CLÉS - CÔTE D'IVOIRE & CRITICITÉ ROUTIÈRE)
KEYWORDS_WEIGHTS = {
    # --- 1. MÉTÉO EXTÊME & INONDATIONS (Poids : 7.0 à 9.5) ---
    "inondation": 9.0, "pluie diluvienne": 8.5, "éboulement": 8.0, "glissement de terrain": 8.5,
    "montée des eaux": 7.5, "crue": 7.5, "orage violent": 7.0, "averse torrentielle": 7.5,
    "tornade": 8.0, "intempéries": 6.5, "route inondée": 9.0, "voie submergée": 9.0,
    "quartier sous les eaux": 8.5, "canaux bouchés": 6.0, "ravinement": 7.0,

    # --- 2. ACCIDENTS & INCIDENTS LOGISTIQUES TRÈS GRAVES (Poids : 6.0 à 9.5) ---
    "route coupée": 9.5, "voie barrée": 8.0, "carambolage": 8.5, "camion renversé": 7.5,
    "citerne": 7.5, "accident": 6.5, "collision": 7.0, "accident mortel": 9.0,
    "drame routier": 8.5, "choc frontal": 8.0, "poids lourd bloqué": 7.0, "remorque en panne": 6.5,
    "badjan renversé": 7.5, "maka renversé": 7.5, "gbaka en détresse": 6.5, "moto fauchée": 6.0,
    "piste impraticable": 7.5, "pont effondré": 9.5, "effondrement de chaussée": 9.0,
    "crevasse": 6.0, "arbre tombé": 7.0, "poteau électrique abattu": 7.0,

    # --- 3. TRAVAUX ROUTIERS & CHANTIERS MAJEURS (Poids : 4.0 à 7.5) ---
    "travaux routiers": 6.5, "chantier naval": 4.5, "bitumage": 5.5, "déviation": 7.0,
    "travaux d'assainissement": 6.0, "reprofilage": 5.0, "fermeture temporaire": 7.5,
    "goudronnage": 5.0, "réhabilitation de la route": 6.0, "échangeur en chantier": 6.5,

    # --- 4. CRISES SOCIALES, MANIFESTATIONS & GRÈVES (Poids : 6.0 à 9.5) ---
    "émeute": 9.5, "manifestation": 8.5, "affrontement": 9.0, "grève": 8.0,
    "barrage": 8.5, "déguerpissement": 8.0, "marche de protestation": 7.5, "protestation": 7.0,
    "sit-in": 6.5, "opération de police": 6.5, "barrage de pneus": 8.5, "pneus brûlés": 8.5,
    "blocus": 9.0, "vandalisme": 8.0, "marche de l'opposition": 8.0, "soulèvement": 9.0,
    "grève des transporteurs": 9.5, "syndicat en colère": 7.5, "contrôle policier": 5.5,
    "rafle": 6.0, "embuscade": 8.5,

    # --- 5. FÊTES RELIGIEUSES, COUTUMES & TRADITIONS (Poids : 6.0 à 9.5) ---
    "deuil national": 9.5, "paquinou": 9.5, "obsèques": 8.5, "hommage national": 8.5,
    "funérailles": 8.0, "pèlerinage": 8.5, "inhumation": 7.5, "tabaski": 9.0,
    "enterrement": 7.0, "pèlerin": 7.0, "ramadan": 7.5, "pâques": 8.0,
    "maouloud": 8.5, "eid": 8.0, "korité": 9.0, "fête du mouton": 9.0,
    "carême": 6.0, "pentecôte": 7.0, "ascension": 7.0, "toussaint": 7.5,
    "noël": 8.5, "réveillon": 8.0, "saint-sylvestre": 8.5, "nouvel an": 8.5,
    "fête des générations": 7.5, "fête des ignames": 8.0, "dipri": 8.5,
    "veillée funèbre": 7.5, "levée de corps": 8.0,

    # --- 6. ÉVÉNEMENTS SPORTIQUES, CULTURELS & FESTIVALS (Poids : 5.0 à 9.0) ---
    "can2023": 9.0, "can": 8.5, "festival": 7.5, "carnaval": 7.5,
    "concert": 6.5, "stade": 6.5, "match": 6.0, "spectacle": 5.5,
    "fiesta": 5.5, "maracana": 5.0, "tournoi de football": 6.0, "anoumabo": 7.0,
    "femua": 8.5, "popo carnaval": 8.5, "abissa": 9.0, "calao": 6.0,
    "fête de la musique": 6.5, "foire": 6.0, "exposition": 5.0, "meeting": 7.5,

    # --- 7. IMPACT TRAFIC & RALENTISSEMENTS DU QUOTIDIEN (Poids : 4.0 à 7.5) ---
    "embouteillage": 6.0, "bouchon": 5.5, "circulation alternée": 6.5, "trafic dense": 5.0,
    "ralentissement": 4.5, "circulation paralysée": 8.5, "voie saturée": 7.0, "embouteillage monstre": 8.0,
    "blocage": 7.0, "ralentissement majeur": 6.0, "trafic interrompu": 9.0, "circulation coupée": 9.0,
    "file d'attente": 5.0, "heure de pointe": 5.5, "stationnement anarchique": 5.5,
    "vitesse réduite": 4.0,

    # --- 8. SYLLEPSES ET EXPRESSIONS IVOIRIENNES DU TRANSPORT (Poids : 5.0 à 8.0) ---
    "gnambro": 7.5, "syndicat de transport": 7.0, "gare routière": 6.5, "quai d'embarquement": 5.5,
    "convoi": 6.5, "cortège officiel": 7.5, "cortège funèbre": 7.0, "chargement hors normes": 6.0,
    "surcharge": 5.5, "visite technique": 5.0,

    # --- 9. COMMÉMORATIONS ET JOURS FÉRIÉS CIVIQUES (Poids : 6.0 à 9.0) ---
    "fête de l'indépendance": 9.0, "7 août": 8.5, "défilé militaire": 8.0, "fête du travail": 7.5,
    "1er mai": 7.0, "journée de la paix": 7.0, "commémoration": 6.5
}