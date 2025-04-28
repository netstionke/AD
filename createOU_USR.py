
from dotenv import load_dotenv
import os
import csv
from ad_functions import connect_to_ad, check_create_ou, create_user
# Charger les variables d'environnement
load_dotenv()
# récup les variables d'environnement
ou_name = os.getenv("OU_NAME")
ou_path = os.getenv("OU_PATH")
ad_base_dn = os.getenv("AD_BASE_DN")

def main():
    # connection a l'ad
    conn = connect_to_ad()
    if conn is None:
        print("Impossible de se connecter à Active Directory. Arrêt du programme.")
        return
    
    # verif & creation de l'OU
    if not check_create_ou(conn, ou_path, ou_name):
        print(f"Impossible de vérifier/créer l'OU '{ou_name}'. Arrêt du programme.")
        conn.unbind()
        return
    
    # lecture des users dans le fichier CSV
    csv_file = 'users.csv'
    
    try:
        with open(csv_file, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                create_user(conn, row, ou_path, ad_base_dn)
    except FileNotFoundError:
        print(f"Le fichier CSV '{csv_file}' n'a pas été trouvé.")
    except Exception as e:
        print(f"Erreur lors du traitement du fichier CSV: {e}")
    
    # deconnexion
    conn.unbind()
    print("Programme terminé.")

if __name__ == "__main__":
    main()