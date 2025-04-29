import os
import re
import sys
from datetime import datetime

# prénom > sexe
import csv
import tkinter as tk
from tkinter import simpledialog, messagebox
from _ast import If

'''

Ce script est utilisé pour analyser des fichiers de généalogie structurés et en extraire des informations spécifiques basées sur des balises prédéfinies.

### Fonctionnalités principales

1. Définitions et configurations initiales :
    - **Importations** : Le script importe les modules nécessaires, comme `os`, `re`, et `datetime`.
    - **Chemin du fichier** : Le chemin du fichier texte à analyser est spécifié (`textePath`).
    - **Patterns** : Les expressions régulières sont définies pour extraire différentes sections du texte, telles que les prénoms, les décès, les naissances, etc.
    - **Mappings** : Un dictionnaire de mappage des mois en français est défini (`month_mapping`).

2. Fonctions utilitaires :
    - **`contient_balise`** : Vérifie si une ligne contient une des balises spécifiées.
    - **`normalize_spaces`** : Normalise les espaces dans une chaîne.
    - **`convert_date_format`** : Convertit une date au format `dd-mm-yyyy` en un format lisible avec le nom du mois en français.
    - **`remove_balises`** : Supprime les balises d une ligne donnée.
    - **`est_date_valide`** : Vérifie si une chaîne est une date valide selon un format spécifié.
    - **`extraire_nom`** et **`extraire_prenom`** : Extraient respectivement les noms et prénoms d une chaîne donnée.
'''

# Chemin du fichier texte
texteDir = r"C:\Users\et\eclipse-workspace\Genealogie\source"
texteFile = "HERVY.txt"
textePath = os.path.join(texteDir, texteFile)

# Modèle de correspondance pour différentes sections avec condition de chaîne vide ajoutée
patterns = {
    'prenom': r'^(.*?)(?=\s*(?:D\s*:|N\s*:|Pa\s*:|T\s*:|M\s*:|M\d+\s*:|\d+[a-z]\s*:|\s*$))',
    'deces': r'D\s*:\s*(.*?)(?=\s*(?:N\s*:|Ma\s*:|Pa\s*:|T\s*:|M\s*:|M\d+\s*:|\d+[a-z]\s*:|\s*$))',
    'naissance': r'N\s*:\s*(.*?)(?=\s*(?:D\s*:|Ma\s*:|Pa\s*:|T\s*:|M\s*:|M\d+\s*:|\d+[a-z]\s*:|\s*$))',    
    'parrain': r'Pa\s*:\s*([^;,]+(?:\([^)]*\))?[^;,]*)(?=[;,]|\s*$)',
    'marraine': r'Ma\s*:\s*(.*?)(?=\s*(?:D\s*:|N\s*:|Pa\s*:|T\s*:|M\s*:|M\d+\s*:|\d+[a-z]\s*:|\s*$))',
    'temoindeces': r'D :.*?(?=T : )(T : )?(.*?)(?=(T :|$|\s*$))',    
    #'union': r'(M\s*:.*?|M\d+\s*:.*?)(.*?)(?=\s*(?:D\s*:|N\s*:|Pa\s*:|T\s*:|M\s*:|M\d+\s*:|\d+[a-z]\s*:|\s*$))',
    'union': r'(M\s*:|M\d+\s*:)(.*?)(?=\s*(?:D\s*:|N\s*:|Pa\s*:|T\s*:|M\s*:|M\d+\s*:|\d+[a-z]\s*:|\s*$))',
    'prenomenfant': r'^(1[a-l]|2[a-l]|3[a-l])\s*:\s*(.*?)(?=\s*(?:N\s*:|Ma\s*:|Pa\s*:|D\s*:|T\s*:|M\s*:|M\d+\s*:|\d+[a-z]\s*:|\s*$))',
    'reperefratrie': r'^(1[a-l])\s*:\s*(.*?)' 
}

'''
# balise sans : pour M1 et plus
'N :', 'Ma :', 'Pa :', 'D :', 'T :', 'M :', 'M1', 'M2', 'M3', 'M4', 'M5',
'''
# Définition des balises
balises = {
    'N :', 'Ma :', 'Pa :', 'D :', 'T :', 'M :', 'M1 :', 'M2 :', 'M3 :', 'M4 :', 'M5 :',
    '1a', '1b', '1c', '1d', '1e', '1f', '1g', '1h', '1i', '1j', '1k', '1l',
    '2a', '2b', '2c', '2d', '2e', '2f', '2g', '2h', '2i', '2j', '2k', '2l',
    '3a', '3b', '3c', '3d', '3e', '3f', '3g', '3h', '3i', '3j', '3k', '3l'
}

# Définition des balises pour les enfants
balises_enfant = {
    '1a', '1b', '1c', '1d', '1e', '1f', '1g', '1h', '1i', '1j', '1k', '1l',
    '2a', '2b', '2c', '2d', '2e', '2f', '2g', '2h', '2i', '2j', '2k', '2l',
    '3a', '3b', '3c', '3d', '3e', '3f', '3g', '3h', '3i', '3j', '3k', '3l'
}

# Définition des balises pour les unions
balises_union = {
    'M', 'M1', 'M2', 'M3', 'M4', 'M5'
}

# Mappage des numéros de mois aux noms de mois en français
month_mapping = {
    '01': 'JAN', '02': 'FEV', '03': 'MAR', '04': 'AVR', '05': 'MAI', '06': 'JUN',
    '07': 'JUL', '08': 'AOU', '09': 'SEP', '10': 'OCT', '11': 'NOV', '12': 'DEC'
}

class GenealogyInfo:
    def __init__(self):
        self.indi_id = None
        self.indi_nom = None
        self.indi_prenom = None
        self.indi_sexe = None
        self.indi_info = None
        self.indi_naissance_date = None
        self.indi_naissance_lieu_abr = None
        self.indi_naissance_info = None
        self.parrain_nom = None
        self.parrain_prenom = None        
        self.parrain_lieu_abr = None
        self.parrain_info = None
        self.marraine_nom = None
        self.marraine_prenom = None        
        self.marraine_lieu_abr = None
        self.marraine_info = None
        self.indi_deces_date = None
        self.indi_deces_lieu_abr = None
        self.indi_deces_info = None
        self.deces_temoin_liste = []
        self.enfant_prenom = None
        self.enfant_info = None
        self.union_date = None
        self.union_lieu_abr = None
        self.union_conjoint = None
        self.conjoint_nom = None
        self.conjoint_prenom = None
        self.conjoint_lieu_abr = None
        self.union_temoin_liste = []
        self.parent = []
        self.couple = []
        


def contient_balise(ligne, balises):
    return any(balise in ligne for balise in balises)

def normalize_spaces(s):
    return s.replace('\u00A0', ' ').strip()

def convert_date_format(date_str):
    try:
        date_obj = datetime.strptime(date_str, '%d-%m-%Y')
        return date_obj.strftime(f'%d {month_mapping[date_obj.strftime("%m")]} %Y')
    except ValueError:
        return date_str

def remove_balises(ligne, balises):
    pattern = re.compile('|'.join(re.escape(balise) for balise in balises))
    return pattern.sub('', ligne)

def extraire_nom(chaine):
    matches = re.findall(r'[A-ZÉÀÂÄÈÉÊËÎÏÔÖÙÛÜÇ]{2,}(?:\s*-\s*[A-ZÉÀÂÄÈÉÊËÎÏÔÖÙÛÜÇ]+)*', chaine)
    cleaned_matches = [re.sub(r'\s*-\s*', '-', match) for match in matches]
    return cleaned_matches

def extraire_prenom(chaine):
    matches = re.findall(r'\b(?:[A-Z]?[a-zéàâäèéêëîïôöùûüç]+(?:-[A-Z]?[a-zéàâäèéêëîïôöùûüç]+)*)\b', chaine)
    cleaned_matches = [re.sub(r'\s*-\s*', '-', match) for match in matches]
    result = ' '.join(cleaned_matches)
    return result

def extract_t_between_m_and_d(ligne, union_temoin_liste):
    pattern_m_d = r'(M\s*:|M\d+\s*:).*?(?=\s*D\s*:)'
    match_m_d = re.search(pattern_m_d, ligne)

    if match_m_d:
        content_between_m_d = match_m_d.group(0)
        pattern_t = r'T\s*:\s*(.*?)(?=\s*$)'
        match_t = re.search(pattern_t, content_between_m_d)

        if match_t:
            chainetemoinunion = match_t.group(1)
            temoinsunion = chainetemoinunion.split(';')
            for temoinunion in temoinsunion:
                temoin_parts = temoinunion.strip().split(',', 1)
                nomprenom = temoin_parts[0].strip()
                temoin_nom = extraire_nom(nomprenom)[0] if extraire_nom(nomprenom) else None
                temoin_prenom = extraire_prenom(nomprenom) if extraire_prenom(nomprenom) else None

                temoin_lieu_abr = None
                if '(' in nomprenom and ')' in nomprenom:
                    nomprenom = nomprenom.split('(', 1)[0].strip()
                if '(' in chainetemoinunion and ')' in chainetemoinunion:
                    temoin_lieu_abr = chainetemoinunion.split('(', 1)[1].split(')', 1)[0].strip()
                info = temoin_parts[1].strip() if len(temoin_parts) > 1 else None
                union_temoin_liste.append((temoin_nom, temoin_prenom, temoin_lieu_abr, info))

    return union_temoin_liste

def est_date_valide(date_str, format="%d-%m-%Y"):
    try:
        datetime.strptime(date_str, format)
        return True
    except ValueError:
        return False

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
    if match:
        #print(f"\n {normalize_spaces(match.group(0))}")
        chaineunion = normalize_spaces(match.group(2))
        chaineunion = re.sub(r'[;,]', '', chaineunion)  # Suppression des virgules et points-virgules avec regex
        chaineunion_ori = chaineunion
        
        #------------------------------------------------
        # première partie > CONJOINT
        #------------------------------------------------
        match = re.search(nom_pos1_pattern, chaineunion)
        if match:
            group1_result = match.group(1).strip()  # On retire les espaces superflus
            
            #print(f"\nchaineunion : {chaineunion}")
            #print("Nom avant ou sans date : " + group1_result)
            
            if group1_result:
                
                nomprenom = match.group(1).strip() if match.group(1) else None
                conjoint_nom = extraire_nom(nomprenom)[0] if extraire_nom(nomprenom) else None
                conjoint_prenom = extraire_prenom(nomprenom) if extraire_prenom(nomprenom) else None
                
                conjoint_lieu_abr = match.group(2).strip() if match.group(2) else None

                a_supprimer = f"{match.group(0).strip()}"
                rest = chaineunion[len(a_supprimer):].strip()

                rest_match = re.match(rest_date_pattern, rest)
                if rest_match:
                    date_part = rest_match.group(1).strip()

                    if est_date_valide(date_part):
                        union_date = convert_date_format(date_part)
                    else:
                        match = re.search(r'\d{4}', date_part)
                        if match:
                            union_date = match.group(0) if match.group(0) else None

                    union_lieu_abr = rest_match.group(2).strip() if rest_match.group(2) else None

        else:
        #------------------------------------------------
        # première partie > DATE UNION
        #------------------------------------------------   
            chaineunion = chaineunion_ori
            #print(f"chaineunion : {chaineunion}")

            match = re.match(rest_date_pattern, chaineunion)
            
            if match:
                date_part = match.group(1).strip()

                if est_date_valide(date_part):
                    union_date = convert_date_format(date_part)
                else:
                    match1 = re.search(r'\d{4}', date_part)
                    if match1:
                        union_date = match1.group(0) if match1.group(0) else None

                union_lieu_abr = match.group(2).strip() if match.group(2) else None

                a_supprimer = f"{match.group(0).strip()}"
                rest = chaineunion[len(a_supprimer):].strip()

                #match = re.search(date_pos1_pattern, rest)
                match = re.search(nom_pos1_pattern, rest)
                
                if match:
                    nomprenom = match.group(1).strip() if match.group(1) else None
                    conjoint_nom = extraire_nom(nomprenom)[0] if extraire_nom(nomprenom) else None
                    conjoint_prenom = extraire_prenom(nomprenom) if extraire_prenom(nomprenom) else None
                    conjoint_lieu_abr = match.group(2).strip() if match.group(2) else None



    match = re.search(patterns['union'], ligne)
    if match:       
        test_union = re.search(r'(?:^|\s)(M[1-5]?)\s*:', normalize_spaces(match.group(0)))
        if test_union:
            # Nettoyage du résultat avec strip()
            balise_test_union = test_union.group(1).strip()
            print(f"{balise_test_union}")  # Formatage sans espace superflu
    
    return union_conjoint, conjoint_nom, conjoint_prenom, conjoint_lieu_abr, union_date, union_lieu_abr

def ajouter_info(texte, nouveau_contenu):
    if texte is not None and texte.strip():
        texte += "\n" + nouveau_contenu
    else:
        texte = nouveau_contenu
    return texte

def parse_line(ligne, indi_id, famille_nom, couple):
    info = GenealogyInfo()
    info.indi_id = indi_id
    
    #print(f"ligne : {ligne}")

    # Informations sur la famille
    nom_famille = None

    # Informations sur l'individu
    info.indi_nom = famille_nom

    match = re.search(patterns['prenom'], ligne)
    if match:
        chaineprenom = normalize_spaces(match.group(1)).strip(',')
        #print(f"chaineprenom : {chaineprenom}")
        
        if ',' in chaineprenom:
            parts = chaineprenom.split(',', 1)
            info.indi_prenom = parts[0].strip().strip(';, ')
            info.indi_info = parts[1].strip() if parts[1] else None
        else:
            info.indi_prenom = chaineprenom.strip().strip(';, ')

    if not info.indi_prenom:
        info.indi_prenom = None

    # extraction des données du conjoint
    info.union_conjoint, info.conjoint_nom, info.conjoint_prenom, info.conjoint_lieu_abr, info.union_date, info.union_lieu_abr = extract_union_info(ligne)
    info.union_temoin_liste = extract_t_between_m_and_d(normalize_spaces(ligne), info.union_temoin_liste)
    
    '''
    ---------------------------------------------------------
        affecter NOM et prénom du conjoint aux variables individu
    '''
    '''
    if info.conjoint_nom:
        
        info.indi_nom = info.conjoint_nom
        #info.conjoint_nom = None
        info.indi_prenom = info.conjoint_prenom
        #info.conjoint_prenom = None
    '''
    '''
    ---------------------------------------------------------
    '''    
     

    match = re.search(patterns['prenomenfant'], ligne)
    if match:
        chaineenfant = normalize_spaces(match.group(2)).strip(',')
        if ',' in chaineenfant:
            parts = chaineenfant.split(',', 1)
            info.enfant_prenom = parts[0].strip()
            info.enfant_info = parts[1].strip() if parts[1] else None
        else:
            info.enfant_prenom = chaineenfant

    if not info.enfant_prenom:
        info.enfant_prenom = None

    match = re.search(patterns['reperefratrie'], ligne)
    if match:
        chainefratrie = normalize_spaces(match.group(0))
        match = re.match(r'^(1)[a-l]\s*:', chainefratrie)

        if match:
            desc_fratrie = match.group(1)
            if info.enfant_prenom is not None and famille_nom is not None:
                info.indi_nom = famille_nom

    match = re.search(patterns['naissance'], ligne)
    if match:
        chainenaissance = normalize_spaces(match.group(1))

        date_match = re.search(r'\b(\d{1,2}-\d{1,2}-\d{2,4}|\d{1,2}-\d{4}|\d{4})(?:\s*\(([^)]+)\))?', chainenaissance)
        if date_match:
            date_part = date_match.group(1).strip()

            if est_date_valide(date_part):
                info.indi_naissance_date = convert_date_format(date_part)
            else:
                match = re.search(r'\d{4}', date_part)
                if match:
                    info.indi_naissance_date = match.group(0) if match.group(0) else None

                    nouveau_contenu = "date incomplète: " + date_part
                    info.indi_naissance_info = ajouter_info(info.indi_naissance_info, nouveau_contenu)

        if '(' in chainenaissance and ')' in chainenaissance:
            info.indi_naissance_lieu_abr = chainenaissance.split('(', 1)[1].split(')', 1)[0].strip()

            nouveau_contenu = chainenaissance.split(')', 1)[1].strip(';,').strip()
            info.indi_naissance_info = ajouter_info(info.indi_naissance_info, nouveau_contenu)

    match = re.search(patterns['parrain'], ligne)
    if match:
        chaineparrain = normalize_spaces(match.group(1))
        parrain_parts = chaineparrain.strip().split(',', 1)
        nomprenom = parrain_parts[0].strip()
        if '(' in nomprenom and ')' in nomprenom:
            nomprenom = nomprenom.split('(', 1)[0].strip()
        if '(' in chaineparrain and ')' in chaineparrain:
            info.parrain_lieu_abr = chaineparrain.split('(', 1)[1].split(')', 1)[0].strip()
        info.parrain_nom = extraire_nom(nomprenom)[0] if extraire_nom(nomprenom) else None
        info.parrain_prenom = extraire_prenom(nomprenom) if extraire_prenom(nomprenom) else None
        info.parrain_info = parrain_parts[1].strip() if len(parrain_parts) > 1 else None

        if not info.parrain_info:
            info.parrain_info = None

    match = re.search(patterns['marraine'], ligne)
    if match:
        chainemarraine = normalize_spaces(match.group(1))
        marraine_parts = re.split(r'[;,]', chainemarraine.strip(), 1)
        nomprenom = marraine_parts[0].strip().rstrip(';,')
        if '(' in nomprenom and ')' in nomprenom:
            nomprenom = nomprenom.split('(', 1)[0].strip()
        if '(' in chainemarraine and ')' in chainemarraine:
            info.marraine_lieu_abr = chainemarraine.split('(', 1)[1].split(')', 1)[0].strip()

        info.marraine_nom = extraire_nom(nomprenom)[0] if extraire_nom(nomprenom) else None
        info.marraine_prenom = extraire_prenom(nomprenom) if extraire_prenom(nomprenom) else None
        info.marraine_info = marraine_parts[1].strip().rstrip(';,') if len(marraine_parts) > 1 else None

        if not info.marraine_info:
            info.marraine_info = None

    match = re.search(patterns['deces'], ligne)
    if match:
        chainedeces = normalize_spaces(match.group(1))

        date_match = re.search(r'\b(\d{1,2}-\d{1,2}-\d{2,4}|\d{1,2}-\d{4}|\d{4})(?:\s*\(([^)]+)\))?', chainedeces)
        
        if date_match:
            date_part = normalize_spaces(date_match.group(1).strip())

            if est_date_valide(date_part):
                info.indi_deces_date = convert_date_format(date_part)
            else:
                match = re.search(r'\d{4}', date_part)
                if match:
                    info.indi_deces_date = match.group(0) if match.group(0) else None

                    nouveau_contenu = "date incomplète: " + date_part
                    info.indi_deces_info = ajouter_info(info.indi_deces_info, nouveau_contenu)

        if '(' in chainedeces and ')' in chainedeces:
            info.indi_deces_lieu_abr = chainedeces.split('(', 1)[1].split(')', 1)[0].strip()

            nouveau_contenu = chainedeces.split(')', 1)[1].strip(';,').strip()
            info.indi_deces_info = ajouter_info(info.indi_deces_info, nouveau_contenu)

    # *************************************************************
    # Extraction des TÉMOINS DE DÉCÈS

    match = re.search(patterns['temoindeces'], normalize_spaces(ligne))
    if match:
        chainetemoindeces = normalize_spaces(match.group(2))  # Les témoins de décès sont dans le groupe 2
        #print(f"match.group(2) : {match.group(2)}")
    
        if 'M :' in chainetemoindeces:
            temoinsdeces = chainetemoindeces.split('M :')[0].split(';')  # Ne pas extraire après 'M :'
        else:
            temoinsdeces = chainetemoindeces.split(';')
    
        for temoindeces in temoinsdeces:
            if 'M :' in temoindeces:
                continue  # Ne pas ajouter l'enregistrement si 'M :' est présent
    
            temoin_parts = temoindeces.strip().split(',', 1)
            nomprenom = temoin_parts[0].strip()
            temoin_nom = extraire_nom(nomprenom)[0] if extraire_nom(nomprenom) else None
            temoin_prenom = extraire_prenom(nomprenom) if extraire_prenom(nomprenom) else None
    
            temoin_lieu_abr = None  # Initialiser la variable
            if '(' in nomprenom and ')' in nomprenom:
                nomprenom = nomprenom.split('(', 1)[0].strip()
            if '(' in chainetemoindeces and ')' in chainetemoindeces:
                temoin_lieu_abr = chainetemoindeces.split('(', 1)[1].split(')', 1)[0].strip()
            temoin_info = temoin_parts[1].strip() if len(temoin_parts) > 1 else None
    
            # Ajouter une condition pour vérifier que les valeurs ne sont pas None avant d'ajouter à la liste
            if temoin_nom is not None or temoin_prenom is not None or temoin_lieu_abr is not None or temoin_info is not None:
                info.deces_temoin_liste.append((temoin_nom, temoin_prenom, temoin_lieu_abr, temoin_info))
                
            #print("chaine témoins décès: "+ chainetemoindeces)

    return info

# Chemin du fichier CSV
csv_file_path = r"C:\Users\et\eclipse-workspace\Genealogie\prenom_sexe\prenom-sexe.csv"

# Fonction pour rechercher un prénom dans le fichier CSV
def search_prenom(prenom):
    if prenom is None:
        return None

    # Si prenom comporte plusieurs chaines, prenom = la première partie
    prenom = prenom.split()[0]
        
    with open(csv_file_path, mode='r', newline='', encoding='latin-1') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0].lower() == prenom.lower():
                return row[1]
    return None

# Fonction pour ajouter un prénom au fichier CSV
def add_prenom(prenom, sexe):
    rows = []
    with open(csv_file_path, mode='r', newline='', encoding='latin-1') as file:
        reader = csv.reader(file)
        rows = list(reader)
    
    rows.append([prenom, sexe])
    rows = sorted(rows, key=lambda x: x[0].lower())
    
    with open(csv_file_path, mode='w', newline='', encoding='latin-1') as file:
        writer = csv.writer(file)
        writer.writerows(rows)

# Fonction pour demander l'ajout d'un prénom
def prompt_add_prenom(prenom):
    root = tk.Tk()
    root.withdraw()  # Cacher la fenêtre principale
    root.attributes('-topmost', True)  # Placer la fenêtre devant les autres
    root.after(0, root.focus_force)  # Forcer le focus sur la fenêtre

    sexe = simpledialog.askstring("Ajouter un prénom", f"Le prénom '{prenom}' n'existe pas. Entrez le sexe (m, f, ou mf) :")
    if sexe and sexe.lower() in ['m', 'f', 'mf']:
        add_prenom(prenom, sexe.lower())
        messagebox.showinfo("Succès", f"Le prénom '{prenom}' a été ajouté avec le sexe '{sexe}'.", parent=root)
    else:
        messagebox.showerror("Erreur", "Sexe invalide. L'ajout a été annulé.", parent=root)

    root.destroy()  # Détruire la fenêtre Tkinter après utilisation
    
def sexe(prenom):
    sexe = search_prenom(prenom)
    
    if sexe:
        print("\n" + f"Le prénom '{prenom}' existe avec le sexe '{sexe}'")
    else:
        print(f"Le prénom '{prenom}' n'existe pas.")
        prompt_add_prenom(prenom)
        
    return sexe

def traitement_sexe(indiprenom):
    
    indisexe = None  # Initialisation par défaut de indisexe
    if indiprenom is not None:
        indisexe = sexe(indiprenom)
        #print("\n+++" + f"sexe individu : {indisexe}")
        
    return indisexe

def traitement_lien_familial(indi_id):
    """
    Incrémente l'ID si la ligne contient des balises d'union ou d'enfant
    Retourne le nouvel ID (ou l'original si aucune action)
    """
    '''
    balises_union = ["MARR", "DIV", "FAMS"]  # À adapter selon vos besoins
    balises_enfant = ["CHIL", "FAMC"]        # À adapter
    '''
    
    indi_id += 1
    return indi_id



def traitement_conjoint(indiprenom, indinom, conjointnom, conjointprenom):
    
    indiprenom = None  # Initialisation par défaut
    indinom = None 
    
'''
    # affecter NOM et prénom du conjoint aux variables individu
    if conjointnom:
        indi_nom = conjointnom
        indi_prenom = conjointprenom    
'''
    #print("\n+++" + f"prénom individu : {info.indi_prenom}")
    #if info.indi_prenom is not None:
    #    info.indi_sexe = sexe(info.indi_prenom)
    #    print("\n+++" + f"sexe individu : {info.indi_sexe}")

def print_info(info):
    print("\n" + "\n".join(f"{key}: {value}" for key, value in {
        "indi_id": info.indi_id,
        "indi_nom": info.indi_nom,
        "indi_prenom": info.indi_prenom,
        "indi_sexe": info.indi_sexe,
        "enfant_prenom": info.enfant_prenom,        
        "indi_info": info.indi_info,
        "indi_naissance_date": info.indi_naissance_date,
        "indi_naissance_lieu_abr": info.indi_naissance_lieu_abr,
        "indi_naissance_info": info.indi_naissance_info,
        "parrain_nom": info.parrain_nom,
        "parrain_prenom": info.parrain_prenom,
        "parrain_lieu_abr": info.parrain_lieu_abr,
        "parrain_info": info.parrain_info,
        "marraine_nom": info.marraine_nom,
        "marraine_prenom": info.marraine_prenom,
        "marraine_lieu_abr": info.marraine_lieu_abr,
        "marraine_info": info.marraine_info,
        "indi_deces_date": info.indi_deces_date,
        "indi_deces_lieu_abr": info.indi_deces_lieu_abr,
        "indi_deces_info": info.indi_deces_info,
        "deces_temoin_liste": info.deces_temoin_liste if info.deces_temoin_liste else None,
        "enfant_info": info.enfant_info,
        "union_date": info.union_date,
        "union_lieu_abr": info.union_lieu_abr,
        "union_conjoint": info.union_conjoint,
        "conjoint_nom": info.conjoint_nom,
        "conjoint_prenom": info.conjoint_prenom,
        "conjoint_lieu_abr": info.conjoint_lieu_abr,
        "union_temoin_liste": info.union_temoin_liste if info.union_temoin_liste else None,
    }.items() if value not in [None, []]))  # les variables = "None" et les listes vides ne sont pas affichées
    
def main():
    
    test_union = None     
    union = 0
    #balise_test_union = None
    # Lire le fichier et traiter les lignes
    with open(textePath, 'r', encoding='utf-8') as file:
        lines = [line.strip() for line in file]

    indi_id = 1  # ID initial de la personne
    mem_indi_id = indi_id   # mémoriser l'id du conjoint

    # Traiter le reste du fichier en tant que paragraphes
    paragraphs = "\n".join(lines[0:]).split("\n\n")  # Débuter à la ligne 1 nom de famille

    for paragraph in paragraphs:
        paragraph_lines = paragraph.split('\n')
        combined_line = ""
        i = 0

        # Lire le nom de famille
        if i <= 1:
            ligne = paragraph_lines[i]
            famille_nom = ligne

        i = 1  # Le nom de famille est lu, débuter le traitement du texte à la ligne suivante

        while i < len(paragraph_lines):
            ligne = paragraph_lines[i]          
            
            # Ne pas concaténer si la ligne commence par M seul, ou M1 à M5
            if re.match(r'^M[1-5]?\s*:', ligne):  # Détection directe sur la ligne
                if combined_line:  # Traiter la ligne combinée existante
                    info = parse_line(combined_line, indi_id, famille_nom, couple)
                    info.indi_sexe = traitement_sexe(info.indi_prenom)
                    print_info(info)
                    combined_line = ""

                # Traiter la ligne "M :" comme nouvelle entrée
                combined_line = ligne

                indi_id = traitement_lien_familial(indi_id)                
                union += 1
                print (f"\nunion: {union}")
                
                
                if re.match(r'^M[1-5]\s*:', ligne):  # Détection M1 à M5
                    if info.indi_sexe == "m":
                        couple = [mem_indi_id, indi_id]
                    elif info.indi_sexe == "f":
                        couple = [indi_id, mem_indi_id]
                elif re.match(r'^M\s*:', ligne):  # Détection M seul 
                    if info.indi_sexe == "m":
                        couple = [indi_id - 1, indi_id]
                    elif info.indi_sexe == "f":
                        couple = [indi_id, indi_id - 1]
                    

                
                
                print (f"couple: {couple}")
                                
                                
                i += 1
                continue  # Passer directement à l'itération suivante
           
            # Vérifier si la ligne suivante commence par 'D :'
            if  i + 1 < len(paragraph_lines) and paragraph_lines[i + 1].startswith('D :'):
                ligne += ' ' + paragraph_lines[i + 1].strip()
                i += 1  # Sauter la ligne suivante

            if contient_balise(ligne, balises):
                
                if combined_line:
                    #print(f"\nligne individu (combinée) : {combined_line}")
                    info = parse_line(combined_line, indi_id, famille_nom)
                    
                    ''' sub traitement complémentaire
                    '''
                    info.indi_sexe = traitement_sexe(info.indi_prenom)

                    print_info(info)  # Afficher les informations extraites
                    combined_line = ""
                
                indi_id = traitement_lien_familial(indi_id)
               
                combined_line = ligne
                
                
            else:

                if not combined_line.endswith(';'):
                    combined_line += ';'
                combined_line += ' ' + ligne.strip()
            i += 1
            
        if combined_line:
            
            info = parse_line(combined_line, indi_id, famille_nom, couple)

            print_info(info)  # Afficher les informations extraites

if __name__ == "__main__":
    main()