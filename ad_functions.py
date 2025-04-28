import os
from ldap3 import Server, Connection, ALL
import csv
from datetime import datetime
from dotenv import load_dotenv

def log_message(message):

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_message = f"[{timestamp}] {message}"
    print(formatted_message)
    log_file = "log_ad_fonctions.txt"
    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(formatted_message + "\n")
    except Exception as e:
        print(f"[{timestamp}] ERREUR: Impossible d'écrire dans le fichier de log: {str(e)}")

def connect_to_ad():
    """AD Connection"""
    log_message("DÉMARRAGE: Tentative de connexion au serveur Active Directory local...")
    try:
        log_message("DÉTAIL: Initialisation du serveur sur localhost...")
        server = Server('localhost', get_info=ALL)
        log_message("DÉTAIL: Serveur initialisé avec succès.")
        ad_user = os.getenv("AD_USER") 
        ad_password = os.getenv("AD_PASSWORD")
        
        log_message(f"DÉTAIL: Création de l'objet de connexion avec l'utilisateur {ad_user}...")
        conn = Connection(server, user=ad_user, password=ad_password)
        log_message("DÉTAIL: Objet de connexion créé.")
        
        log_message("DÉTAIL: Tentative de liaison (bind) au serveur...")
        if not conn.bind():
            log_message(f"ERREUR: Échec de la liaison au serveur. Réponse du serveur: {conn.result}")
            return None
        
        log_message("SUCCÈS: Connexion à Active Directory établie avec succès.")
        log_message(f"DÉTAIL: Informations de connexion: {conn}")
        return conn
    except Exception as e:
        log_message(f"ERREUR CRITIQUE: Exception lors de la connexion à AD: {str(e)}")
        return None

def check_create_ou(conn, ou_path, ou_name):
    """Verif OU existence et création si nécessaire"""
    log_message(f"DÉMARRAGE: Vérification de l'existence de l'OU '{ou_name}' au chemin '{ou_path}'...")
    
    try:
        log_message(f"DÉTAIL: Exécution d'une recherche LDAP pour l'OU...")
        search_result = conn.search(ou_path, '(objectClass=organizationalUnit)')
        
        if not search_result:
            log_message(f"INFORMATION: L'OU '{ou_name}' n'existe pas encore.")
            log_message(f"DÉTAIL: Tentative de création de l'OU '{ou_name}'...")
            
            add_result = conn.add(ou_path, ['organizationalUnit'], {'ou': ou_name})
            
            if add_result:
                log_message(f"SUCCÈS: L'OU '{ou_name}' a été créée avec succès.")
                log_message(f"DÉTAIL: Réponse du serveur: {conn.result}")
            else:
                log_message(f"ERREUR: Échec de la création de l'OU '{ou_name}'.")
                log_message(f"DÉTAIL: Réponse du serveur: {conn.result}")
            
            return add_result
        else:
            log_message(f"INFORMATION: L'OU '{ou_name}' existe déjà, aucune action nécessaire.")
            log_message(f"DÉTAIL: Entrées trouvées: {conn.entries}")
            return True
            
    except Exception as e:
        log_message(f"ERREUR CRITIQUE: Exception lors de la vérification/création de l'OU: {str(e)}")
        return False

def create_user(conn, user_info, ou_path, ad_base_dn):
    """création d'un utilisateur dans l'OU"""
    user_nom = user_info['nom']
    user_prenom = user_info['prenom']
    user_password = user_info['motdepasse']
    
    log_message(f"DÉMARRAGE: Création de l'utilisateur '{user_prenom} {user_nom}'...")
    log_message(f"DÉTAIL: Informations de l'utilisateur: Prénom={user_prenom}, Nom={user_nom}")
    
    try:
        cn = f"{user_prenom} {user_nom}"
        user_dn = f"CN={cn},{ou_path}"
        log_message(f"DÉTAIL: DN de l'utilisateur: {user_dn}")
        
        user_sam = f"{user_prenom.lower()}.{user_nom.lower()}"
        log_message(f"DÉTAIL: sAMAccountName: {user_sam}")
        
        domain = ad_base_dn.replace('DC=', '').replace(',', '.')
        log_message(f"DÉTAIL: Domaine extrait: {domain}")
        
        log_message("DÉTAIL: Préparation des attributs de l'utilisateur...")
        user_attrs = {
            'givenName': user_prenom,
            'sn': user_nom,
            'displayName': cn,
            'userPrincipalName': f"{user_sam}@{domain}",
            'sAMAccountName': user_sam,
            'userAccountControl': 514
        }
        log_message(f"DÉTAIL: Attributs préparés: {user_attrs}")
        log_message("DÉTAIL: Tentative de création de l'utilisateur dans AD...")
        success = conn.add(user_dn, ['top', 'person', 'organizationalPerson', 'user'], user_attrs)
        
        if success:
            log_message(f"SUCCÈS: Utilisateur '{cn}' créé avec succès.")
            log_message(f"DÉTAIL: Réponse du serveur: {conn.result}")
            
            # Configuration du mot de passe
            log_message(f"DÉTAIL: Tentative de définition du mot de passe pour '{cn}'...")
            try:
                pwd_success = conn.extend.microsoft.modify_password(user_dn, user_password)
                
                if pwd_success:
                    log_message(f"SUCCÈS: Mot de passe défini avec succès pour '{cn}'.")
                    log_message(f"DÉTAIL: Réponse du serveur: {conn.result}")
                else:
                    log_message(f"ERREUR: Échec de la définition du mot de passe pour '{cn}'.")
                    log_message(f"DÉTAIL: Réponse du serveur: {conn.result}")
                
                return pwd_success
            except Exception as e:
                log_message(f"ERREUR CRITIQUE: Exception lors de la définition du mot de passe pour '{cn}': {str(e)}")
                return False
        else:
            log_message(f"ERREUR: Échec de la création de l'utilisateur '{cn}'.")
            log_message(f"DÉTAIL: Réponse du serveur: {conn.result}")
            return False
            
    except Exception as e:
        log_message(f"ERREUR CRITIQUE: Exception lors de la création de l'utilisateur '{user_prenom} {user_nom}': {str(e)}")
        return False