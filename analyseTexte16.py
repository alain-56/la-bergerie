'''
ce script :

- distingue  
    deces_temoin_liste qui succède la balise "D :" 
    et union_temoin_liste qui succède balises_union = {'M :', 'M1', 'M2', 'M3', 'M4', 'M5'}
- ajoute dans chaque Patterns d'une condition de chaine vide (None)
- combine deux lignes si la suivante commence par le décès D :
- inclus la recherche de M : s'il est inclus dans la ligne
- gère les infos union écrites de différentes manières
- gère le nom de famille
INUTILISÉ    
    compare la longueur de "ligne" (len_ligne) avec la longueur cumulée des variables extraites de "ligne"  (len_data)

'''

import os
import re
from datetime import datetime
from fontTools.ttLib.tables.E_B_D_T_ import BitAlignedBitmapMixin
from pickle import NONE

# Chemin du fichier texte
texteDir = r"C:\Users\et\eclipse-workspace\Genealogie\source"
#texteFile = "MONTEST.txt"
texteFile = "HERVY.txt"
#texteFile = "EON.txt"
#texteFile = "05  BOUÈRE.txt"

textePath = os.path.join(texteDir, texteFile)

# Patterns for the different sections with added condition for empty string
patterns = {
    'prenom': r'^(.*?)(?=\s*(?:D\s*:|N\s*:|Pa\s*:|T\s*:|M\s*:|M\d+\s*:|\d+[a-z]\s*:|\s*$))',
    'deces': r'D\s*:\s*(.*?)(?=\s*(?:N\s*:|Ma\s*:|Pa\s*:|T\s*:|M\s*:|M\d+\s*:|\d+[a-z]\s*:|\s*$))',
    'naissance': r'N\s*:\s*(.*?)(?=\s*(?:D\s*:|Ma\s*:|Pa\s*:|T\s*:|M\s*:|M\d+\s*:|\d+[a-z]\s*:|\s*$))',    
    'parrain': r'Pa\s*:\s*([^;,]+(?:\([^)]*\))?[^;,]*)(?=[;,]|\s*$)',
    'marraine': r'Ma\s*:\s*(.*?)(?=\s*(?:D\s*:|N\s*:|Pa\s*:|T\s*:|M\s*:|M\d+\s*:|\d+[a-z]\s*:|\s*$))',
    'temoindeces': r'D :.*?(?=T : )(T : )?(.*?)(?=(T :|$|\s*$))',    
    'union': r'(M\s*:.*?|M\d+\s*:.*?)(.*?)(?=\s*(?:D\s*:|N\s*:|Pa\s*:|T\s*:|M\s*:|M\d+\s*:|\d+[a-z]\s*:|\s*$))',
    'prenomenfant': r'^(1[a-l]|2[a-l]|3[a-l])\s*:\s*(.*?)(?=\s*(?:N\s*:|Ma\s*:|Pa\s*:|D\s*:|T\s*:|M\s*:|M\d+\s*:|\d+[a-z]\s*:|\s*$))',
    'reperefratrie': r'^(1[a-l])\s*:\s*(.*?)' 
}

# pattern abandonné
    #'temoinunion': r'(M\s*:.*?|M\d+\s*:.*?)T : (.*?)(?=D :|\s*$)',


# Mapping of month numbers to month names in French
month_mapping = {
    '01': 'JAN', '02': 'FEV', '03': 'MAR', '04': 'AVR', '05': 'MAI', '06': 'JUN',
    '07': 'JUL', '08': 'AOU', '09': 'SEP', '10': 'OCT', '11': 'NOV', '12': 'DEC'
}

def contient_balise(ligne, balises):
    return any(balise in ligne for balise in balises)

balises = {
    'N :', 'Ma :', 'Pa :', 'D :', 'T :', 'M :', 'M1', 'M2', 'M3', 'M4', 'M5',
    '1a', '1b', '1c', '1d', '1e', '1f', '1g', '1h', '1i', '1j', '1k', '1l',
    '2a', '2b', '2c', '2d', '2e', '2f', '2g', '2h', '2i', '2j', '2k', '2l',
    '3a', '3b', '3c', '3d', '3e', '3f', '3g', '3h', '3i', '3j', '3k', '3l'
}

balises_enfant = {
    '1a', '1b', '1c', '1d', '1e', '1f', '1g', '1h', '1i', '1j', '1k', '1l',
    '2a', '2b', '2c', '2d', '2e', '2f', '2g', '2h', '2i', '2j', '2k', '2l',
    '3a', '3b', '3c', '3d', '3e', '3f', '3g', '3h', '3i', '3j', '3k', '3l'
}

balises_union = {
    'M :', 'M1', 'M2', 'M3', 'M4', 'M5'
}

# Function to normalize spaces
def normalize_spaces(s):
    return s.replace('\u00A0', ' ').strip()

# Function to convert date format
def convert_date_format(date_str):
    try:
        date_obj = datetime.strptime(date_str, '%d-%m-%Y')
        return date_obj.strftime(f'%d {month_mapping[date_obj.strftime("%m")]} %Y')
    except ValueError:
        return date_str

# Function to remove balises from the line
def remove_balises(ligne, balises):
    # Create a regex pattern to match all balises
    pattern = re.compile('|'.join(re.escape(balise) for balise in balises))
    # Remove all balises
    return pattern.sub('', ligne)

# TEMOIN UNION
def extract_t_between_m_and_d(ligne, union_temoin_liste):

    # Pattern to capture the content between M1: and D:
    pattern_m_d = r'(M\s*:|M\d+\s*:).*?(?=\s*D\s*:)' # M\d+\s*:.*?(?=\s*D\s*:)
    match_m_d = re.search(pattern_m_d, ligne)
    
    if match_m_d:
        # Extract the content between M1: and D:
        content_between_m_d = match_m_d.group(0)
        # Pattern to capture the content after T:
        pattern_t = r'T\s*:\s*(.*?)(?=\s*$)'
        match_t = re.search(pattern_t, content_between_m_d)
        
        if match_t:
            #return match_t.group(1)
            chainetemoinunion = match_t.group(1)
            temoinsunion = chainetemoinunion.split(';')
            for temoinunion in temoinsunion:
                temoin_parts = temoinunion.strip().split(',', 1)
                nomprenom = temoin_parts[0].strip()
                
                #print(nomprenom)
                temoin_nom = extraire_nom(nomprenom)[0] if extraire_nom(nomprenom) else None
                temoin_prenom = extraire_prenom(nomprenom) if extraire_prenom(nomprenom) else None
                            
                temoin_lieu_abr = None  # Initialize the variable
                if '(' in nomprenom and ')' in nomprenom:
                                                                                          
                    nomprenom = nomprenom.split('(', 1)[0].strip()            
                if '(' in chainetemoinunion and ')' in chainetemoinunion:
                    temoin_lieu_abr = chainetemoinunion.split('(', 1)[1].split(')', 1)[0].strip()
                info = temoin_parts[1].strip() if len(temoin_parts) > 1 else None
                #union_temoin_liste.append((nom_prenom, temoin_lieu_abr, info))        
                union_temoin_liste.append((temoin_nom, temoin_prenom, temoin_lieu_abr, info))
    
    return union_temoin_liste

def est_date_valide(date_str, format="%d-%m-%Y"):
    # Vérifie si une chaîne est une date valide selon le format spécifié.
    # Le format de la date (par défaut "%d-%m-%Y").
    try:
        datetime.strptime(date_str, format)
        return True
    except ValueError:
        return False
    
def extraire_nom(chaine):
    # Utiliser une expression régulière pour extraire les sous-chaînes en majuscules de deux lettres ou plus
    matches = re.findall(r'[A-ZÉÀÂÄÈÉÊËÎÏÔÖÙÛÜÇ]{2,}(?:\s*-\s*[A-ZÉÀÂÄÈÉÊËÎÏÔÖÙÛÜÇ]+)*', chaine)
    # Nettoyer les espaces en trop autour des tirets
    cleaned_matches = [re.sub(r'\s*-\s*', '-', match) for match in matches]
    return cleaned_matches

def extraire_prenom(chaine):
    # Utiliser une expression régulière pour extraire les sous-chaînes qui ne sont pas entièrement en majuscules
    matches = re.findall(r'\b(?:[A-Z]?[a-zéàâäèéêëîïôöùûüç]+(?:-[A-Z]?[a-zéàâäèéêëîïôöùûüç]+)*)\b', chaine)
    # Nettoyer les espaces en trop autour des tirets
    cleaned_matches = [re.sub(r'\s*-\s*', '-', match) for match in matches]
    # Joindre les sous-chaînes par un espace
    result = ' '.join(cleaned_matches)
    return result

def extract_union_info(ligne):
    
    union_date = None
    union_lieu_abr = None
    union_conjoint = None
    conjoint_lieu_abr = None     
    conjoint_nom = None
    conjoint_prenom = None      
    

    
    date_pos1_pattern = r'^(\d{1,2})?-?(\d{1,2})?-?(\d{2,4})?'    # première position > DATE UNION
    nom_pos1_pattern = r'^(?!\d{1,2}-\d{1,2}-\d{2,4})([^\d()]*)(?:\(([^)]+)\))?'    # première position > CONJOINT
    rest_date_pattern = r'\b(\d{1,2}-\d{1,2}-\d{2,4}|\d{1,2}-\d{4}|\d{4})(?:\s*\(([^)]+)\))?'

                           
    match = re.search(patterns['union'], ligne)
    print(match)                                                   
    if match:
        chaineunion = normalize_spaces(match.group(2))
        chaineunion = re.sub(r'[;,]', '', chaineunion)  # Suppression des virgules et points-virgules avec regex
        chaineunion_ori = chaineunion
        #print(f"chaineunion: {chaineunion}")

        #------------------------------------------------
        # première partie > CONJOINT
        #------------------------------------------------
        match = re.search(nom_pos1_pattern, chaineunion)   
        if match:  
            group1_result = match.group(1).strip()  # On retire les espaces superflus
            if group1_result:
                #print("position 1 > NOM Prénom")
                
                # Extraction des différentes parties
                #union_conjoint = match.group(1).strip() if match.group(1) else None
                nomprenom = match.group(1).strip() if match.group(1) else None
                conjoint_nom = extraire_nom(nomprenom)[0] if extraire_nom(nomprenom) else None
                conjoint_prenom = extraire_prenom(nomprenom) if extraire_prenom(nomprenom) else None
                
                conjoint_lieu_abr = match.group(2).strip() if match.group(2) else None
    
                # sous-chaînes à supprimer
                a_supprimer = f"{match.group(0).strip()}"
                rest = chaineunion[len(a_supprimer):].strip()
               
                rest_match = re.match(rest_date_pattern, rest)
                if rest_match:
                    
                    # Extraction des différentes parties
                    date_part = rest_match.group(1).strip()
                    
                    if est_date_valide(date_part):
                        # gedcom    1 DATE 15 JAN 2025                   
                        union_date = convert_date_format(date_part)
                    else:
                        # gedcom    2 DATE ABT 1674
                        match = re.search(r'\d{4}', date_part)
                        if match:
                            union_date = match.group(0) if match.group(0) else None                     
                    
                    union_lieu_abr = rest_match.group(2).strip() if rest_match.group(2) else None

        #------------------------------------------------
        # première partie > DATE UNION
        #------------------------------------------------            
        else:            
            # initialise chaineunion
            chaineunion = chaineunion_ori
             
            #print("position 1 > DATE")
            #print(chaineunion)
            
            match = re.match(rest_date_pattern, chaineunion)
            if match:
                date_part = match.group(1).strip()
                
                if est_date_valide(date_part):
                    # gedcom    1 DATE 15 JAN 2025                   
                    union_date = convert_date_format(date_part)
                else:
                    # gedcom    2 DATE ABT 1674
                    match1 = re.search(r'\d{4}', date_part)
                    if match1:
                        union_date = match1.group(0) if match1.group(0) else None                     
                
                union_lieu_abr = match.group(2).strip() if match.group(2) else None
                
             
                # sous-chaînes à supprimer
                a_supprimer = f"{match.group(0).strip()}"
                #rest = re.sub(re.escape(a_supprimer), '', chaineunion).strip()
                rest = chaineunion[len(a_supprimer):].strip()
                #print(f"rest:{rest}")     

                match = re.search(nom_pos1_pattern, rest) 
                #match = re.match(rest_date_pattern, rest)  
                if match:  
                    #print(f"NOM et Lieu: {match.group(0).strip()}")
                    #union_conjoint = match.group(1).strip() if match.group(1) else None
                    nomprenom = match.group(1).strip() if match.group(1) else None
                    conjoint_nom = extraire_nom(nomprenom)[0] if extraire_nom(nomprenom) else None
                    conjoint_prenom = extraire_prenom(nomprenom) if extraire_prenom(nomprenom) else None                    
                    conjoint_lieu_abr = match.group(2).strip() if match.group(2) else None 
                
                        
    return union_conjoint, conjoint_nom, conjoint_prenom, conjoint_lieu_abr, union_date, union_lieu_abr


def ajouter_info(texte, nouveau_contenu):
    # Vérifier si la variable texte est None ou comporte un contenu
    if texte is not None and texte.strip():
        # Si oui, ajouter le nouveau contenu sur une autre ligne
        texte += "\n" + nouveau_contenu
    else:
        # Si non, écrire le nouveau contenu
        texte = nouveau_contenu
    return texte


# Function to parse the information
def parse_line(ligne, indi_id, parent_id_pere=None, parent_id_mere=None):
    # Ajout des initialisations pour les nouvelles variables parent et couple
    parent = [parent_id_pere, parent_id_mere]
    couple = [couple_id_homme, couple_id_femme]
    
    # Informations sur la famille
    nom_famille = None
    
    # Informations sur l'individu
    indi_nom = None
    indi_prenom = None
    indi_info = None
    nomprenom = []
    
        
    # Informations sur l'enfant
    enfant_prenom = None
    enfant_info = None    
    
    # Informations sur la fratrie
    chainefratrie = None
    
    # Informations sur la naissance
    chainenaissance = None
    indi_naissance_date = None
    indi_naissance_lieu_abr = None
    indi_naissance_info = None
    indi_sexe = None

    # Informations sur le parrain
    chaineparrain = None
    parrain_nom = None
    parrain_prenom = None
    parrain_lieu_abr = None
    parrain_info = None    
    
    # Informations sur la marraine
    chainemarraine = None
    marraine_nom = None
    marraine_prenom = None
    marraine_lieu_abr = None
    marraine_info = None        
    
    # Informations sur le décès
    chainedeces = None
    indi_deces_date = None
    indi_deces_lieu_abr = None
    indi_deces_info = None
    deces_temoin_liste = []
    
    # Informations sur les témoins pour l'union
    chainetemoin = None
    union_temoin_liste = []
    
    # Informations sur le conjoint
    union_date = None
    union_lieu_abr = None
    union_conjoint = None
    
    conjoint_nom = None
    conjoint_prenom = None    
    conjoint_lieu_abr = None    
    
    date_pattern = r'\b(\d{1,2}-\d{1,2}-\d{2,4}|\d{1,2}-\d{4}|\d{4})(?:\s*\(([^)]+)\))?'

    

    # *************************************************************
    # Extracting PRENOM INDIVIDU
    # nom du père
    indi_nom = famille_nom
    
    match = re.search(patterns['prenom'], ligne)
    if match:
        chaineprenom = normalize_spaces(match.group(1)).strip(',')
        if ',' in chaineprenom:
            parts = chaineprenom.split(',', 1)
            indi_prenom = parts[0].strip().strip(';, ')
            indi_info = parts[1].strip() if parts[1] else None
        else:
            indi_prenom = chaineprenom.strip().strip(';, ')    
            
    # Vérifier si indi_prenom est vide, le définir à None
    if not indi_prenom:
        indi_prenom = None        
        
        
    # *************************************************************
    # Extracting UNION
    
    union_conjoint, conjoint_nom, conjoint_prenom, conjoint_lieu_abr, union_date, union_lieu_abr = extract_union_info(ligne)
    
    
    # *************************************************************
    # Extracting TEMOIN UNION
     
    union_temoin_liste = extract_t_between_m_and_d(normalize_spaces(ligne), union_temoin_liste)

    
    # *************************************************************
    # Extracting PRENOM ENFANT
    
    match = re.search(patterns['prenomenfant'], ligne)
    if match:
        chaineenfant = normalize_spaces(match.group(2)).strip(',')
        if ',' in chaineenfant:
            parts = chaineenfant.split(',', 1)
            indi_prenom = parts[0].strip()
            indi_info = parts[1].strip() if parts[1] else None
        else:
            indi_prenom = chaineenfant
            
        #print(f"indi_prenom: {indi_prenom}")
            
    # Vérifier si indi_prenom est vide, le définir à None
    if not indi_prenom:
        indi_prenom = None               
    
    

    # *************************************************************
    # Extracting FRATRIE
    
    match = re.search(patterns['reperefratrie'], ligne)
    if match: 
        chainefratrie = normalize_spaces(match.group(0))  # Utiliser group(0) pour capturer toute la chaîne
        #print(f"chainefratrie: {chainefratrie}")  # Débogage
    
        # Utiliser une expression régulière pour capturer le chiffre avant la lettre
        match = re.match(r'^(1)[a-l]\s*:', chainefratrie)
        
        if match:
            desc_fratrie = match.group(1)
            #print(f"desc_fratrie: {desc_fratrie}")

            # Le nom de famille est attribué à l'enfant seulement si le prénom est fourni
            if indi_prenom is not None and famille_nom is not None:
                indi_nom = famille_nom
                #print(f"indi_nom: {indi_nom}")             
        
    
    # *************************************************************
    # Extracting NAISSANCE
    
    match = re.search(patterns['naissance'], ligne)
    if match:
        chainenaissance = normalize_spaces(match.group(1))    
        #print(chainenaissance)
    
        match = re.search(date_pattern, chainenaissance)
        if match:
            date_part = match.group(1).strip()        
            
            if est_date_valide(date_part):
                # gedcom    1 DATE 15 JAN 2025                   
                indi_naissance_date = convert_date_format(date_part)
            else:
                # gedcom    2 DATE ABT 1674
                match = re.search(r'\d{4}', date_part)
                if match:
                    indi_naissance_date = match.group(0) if match.group(0) else None  
                    
                    nouveau_contenu = "date incomplète: " + date_part
                    # ajouter un nouveau contenu
                    indi_naissance_info = ajouter_info(indi_naissance_info, nouveau_contenu)
                        
        if ('(' in chainenaissance) and (')' in chainenaissance):
            indi_naissance_lieu_abr = chainenaissance.split('(', 1)[1].split(')', 1)[0].strip()
            #print(indi_naissance_lieu_abr)

            nouveau_contenu = chainenaissance.split(')', 1)[1].strip(';,').strip()
            indi_naissance_info = ajouter_info(indi_naissance_info, nouveau_contenu)  
    
   
    # *************************************************************    
    # Extracting PARRAIN
    
    match = re.search(patterns['parrain'], ligne)
    if match:
        chaineparrain = normalize_spaces(match.group(1))
        parrain_parts = chaineparrain.strip().split(',', 1)
        nomprenom = parrain_parts[0].strip()
        if '(' in nomprenom and ')' in nomprenom:
            nomprenom = nomprenom.split('(', 1)[0].strip()
        if '(' in chaineparrain and ')' in chaineparrain:
            parrain_lieu_abr = chaineparrain.split('(', 1)[1].split(')', 1)[0].strip()
        #print(parrain_nom)
        parrain_nom = extraire_nom(nomprenom)[0] if extraire_nom(nomprenom) else None
        parrain_prenom = extraire_prenom(nomprenom) if extraire_prenom(nomprenom) else None
        parrain_info = parrain_parts[1].strip() if len(parrain_parts) > 1 else None
        
        # Vérifier si parrain_info est vide, le définir à None
        if not parrain_info:
            parrain_info = None  
            
       
    # *************************************************************
    # Extracting MARRAINE
    
    match = re.search(patterns['marraine'], ligne)
    if match:
        chainemarraine = normalize_spaces(match.group(1))
        #print(chainemarraine)
        #marraine_parts = chainemarraine.strip().split(';,', 1)
        marraine_parts = re.split(r'[;,]', chainemarraine.strip(), 1)
        #print(marraine_parts)
        nomprenom = marraine_parts[0].strip().rstrip(';,')
        #print(nomprenom)
        if '(' in nomprenom and ')' in nomprenom:
            nomprenom = nomprenom.split('(', 1)[0].strip()
        if '(' in chainemarraine and ')' in chainemarraine:
            marraine_lieu_abr = chainemarraine.split('(', 1)[1].split(')', 1)[0].strip()
            
        marraine_nom = extraire_nom(nomprenom)[0] if extraire_nom(nomprenom) else None
        marraine_prenom = extraire_prenom(nomprenom) if extraire_prenom(nomprenom) else None            
        marraine_info = marraine_parts[1].strip().rstrip(';,') if len(marraine_parts) > 1 else None
        
        # Vérifier si marraine_info est vide, le définir à None
        if not marraine_info:
            marraine_info = None 

    
    # *************************************************************        
    # Extracting DECES
    
    match = re.search(patterns['deces'], ligne)
    if match:
        chainedeces = normalize_spaces(match.group(1))    
    
        match = re.search(date_pattern, chainedeces)
        if match:
            date_part = match.group(1).strip()        
            
            if est_date_valide(date_part):
                # gedcom    1 DATE 15 JAN 2025                   
                indi_deces_date = convert_date_format(date_part)
            else:
                # gedcom    2 DATE ABT 1674
                match = re.search(r'\d{4}', date_part)
                if match:
                    indi_deces_date = match.group(0) if match.group(0) else None  
                    
                    nouveau_contenu = "date incomplète: " + date_part
                    # ajouter un nouveau contenu
                    indi_deces_info = ajouter_info(indi_deces_info, nouveau_contenu)
                        
        if ('(' in chainedeces) and (')' in chainedeces):
            indi_deces_lieu_abr = chainedeces.split('(', 1)[1].split(')', 1)[0].strip()

            nouveau_contenu = chainedeces.split(')', 1)[1].strip(';,').strip()
            indi_deces_info = ajouter_info(indi_deces_info, nouveau_contenu)
                    
    
    # *************************************************************
    # Extracting TEMOIN(S) DE DECES
    
    match = re.search(patterns['temoindeces'], normalize_spaces(ligne))
    if match:
        chainetemoindeces = normalize_spaces(match.group(2))    #les témoins de décès sont dans le groupe 2
        temoinsdeces = chainetemoindeces.split(';')
        for temoindeces in temoinsdeces:
            temoin_parts = temoindeces.strip().split(',', 1)
            nomprenom = temoin_parts[0].strip()
            #print(nomprenom)
            temoin_nom = extraire_nom(nomprenom)[0] if extraire_nom(nomprenom) else None
            temoin_prenom = extraire_prenom(nomprenom) if extraire_prenom(nomprenom) else None
                    
            temoin_lieu_abr = None  # Initialize the variable
            if '(' in nomprenom and ')' in nomprenom:
                nomprenom = nomprenom.split('(', 1)[0].strip()            
            if '(' in chainetemoindeces and ')' in chainetemoindeces:
                temoin_lieu_abr = chainetemoindeces.split('(', 1)[1].split(')', 1)[0].strip()
            info = temoin_parts[1].strip() if len(temoin_parts) > 1 else None
            #deces_temoin_liste.append((nom_prenom, temoin_lieu_abr, info))
            deces_temoin_liste.append((temoin_nom, temoin_prenom, temoin_lieu_abr, info))

    # =============================================================
    # Printing variables
    variables = {
        "indi_id": indi_id,
        "indi_nom": indi_nom,
        "indi_prenom": indi_prenom,
        "indi_info": indi_info,
        "indi_naissance_date": indi_naissance_date,
        "indi_naissance_lieu_abr": indi_naissance_lieu_abr,
        "indi_naissance_info": indi_naissance_info,
        "parrain_nom": parrain_nom,
        "parrain_prenom": parrain_prenom,        
        "parrain_lieu_abr": parrain_lieu_abr,
        "parrain_info": parrain_info,
        "marraine_nom": marraine_nom,
        "marraine_prenom": marraine_prenom,        
        "marraine_lieu_abr": marraine_lieu_abr,
        "marraine_info": marraine_info,
        "indi_deces_date": indi_deces_date,
        "indi_deces_lieu_abr": indi_deces_lieu_abr,
        "indi_deces_info": indi_deces_info,
        "deces_temoin_liste": deces_temoin_liste,
        "enfant_prenom": enfant_prenom,
        "enfant_info": enfant_info,
        "union_date": union_date,
        "union_lieu_abr": union_lieu_abr,
        "union_conjoint": union_conjoint,
        "conjoint_nom": conjoint_nom,
        "conjoint_prenom": conjoint_prenom,
        "conjoint_lieu_abr": conjoint_lieu_abr,
        "union_temoin_liste": union_temoin_liste,
        "parent": parent,
        "couple": couple        
    }

    normalized_ligne = normalize_spaces(ligne)
    len_ligne = len(remove_balises(normalized_ligne, balises))
    len_data = sum(len(str(value)) for key, value in variables.items() if value is not None and value != [])
    chaine_cumulee = ' | '.join(str(value) for key, value in variables.items() if value is not None and value != [])
    
    # Printing the content of the line and extracted variables
    
    for variable_name, variable_value in variables.items():
        if variable_value is not None and variable_value != []:
            print(f"{variable_name}: {variable_value}")
    print('--------------------------')



if __name__ == "__main__":
    # Reading file and processing lines
    with open(textePath, 'r', encoding='utf-8') as file:
        lines = [line.strip() for line in file]
    
    indi_id = 1  # Initial person ID
    
    # Process the rest of the file as paragraphs
    paragraphs = "\n".join(lines[0:]).split("\n\n") # débuter à la ligne 1 nom de famille

    parent_id_pere = None
    parent_id_mere = None    
    couple_id_homme = None
    couple_id_femme = None
    
    for paragraph in paragraphs:
        paragraph_lines = paragraph.split('\n')
        combined_line = ""
        i = 0
        
        # =============================
        # nom de famille
        if i <= 1:
            ligne = paragraph_lines[i]
            famille_nom = ligne

        #print(famille_nom)
        
        i = 1   # le nom de famille est lu, débuter le traitement du texte à la ligne suivante
        
        # =============================
        indi_sexe = 'F'

        while i < len(paragraph_lines):
            ligne = paragraph_lines[i]
            # Check if the next line starts with 'D :'
            if i + 1 < len(paragraph_lines) and paragraph_lines[i + 1].startswith('D :'):
                ligne += ' ' + paragraph_lines[i + 1].strip()
                i += 1  # Skip the next line
            if contient_balise(ligne, balises):
                if combined_line:
                    # Appeler la fonction parse_line avec les identifiants du père et de la mère
                    parse_line(combined_line, indi_id, indi_sexe, parent_id_pere, parent_id_mere, couple_id_homme, couple_id_femme)
                    combined_line = ""
                if contient_balise(ligne, balises_union):
                    if indi_sexe == 'F':
                        parent_id_mere = indi_id  # Mettre à jour l'identifiant de la mère
                        couple_id_femme = indi_id
                    elif indi_sexe == 'M':
                        parent_id_pere = indi_id  # Mettre à jour l'identifiant du père
                        couple_id_homme = indi_id
                    indi_id += 1  # Increment person ID for each new union
                elif contient_balise(ligne, balises_enfant):
                    indi_id += 1  # Increment person ID for each new child
                combined_line = ligne
            else:
                # si témoin, ajout du séparateur ;
                # Combine the line with the previous one, adding a semicolon if not already present
                if not combined_line.endswith(';'):
                    combined_line += ';'
                combined_line += ' ' + ligne.strip()
            i += 1
        if combined_line:
            # Appeler la fonction parse_line avec les identifiants parent et couple
            parse_line(combined_line, indi_id, indi_sexe, parent_id_pere, parent_id_mere, couple_id_homme, couple_id_femme)