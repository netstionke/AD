from ldap3 import Server, Connection, ALL, SUBTREE, MODIFY_REPLACE
import datetime
from dotenv import load_dotenv  
import os

def main():
    # Chargement des variables d'environnement depuis .env
    load_dotenv()

    ou_path     = os.getenv("OU_PATH")
    ad_user     = os.getenv("AD_USER")
    ad_password = os.getenv("AD_PASSWORD")

    #con active directory
    server = Server('localhost', get_info=ALL)
    conn   = Connection(server, user=ad_user, password=ad_password)
    if not conn.bind():
        print("Erreur de connexion :", conn.result)
        exit(1)

    # liste de recherche 
    conn.search(
        search_base=ou_path,
        search_filter='(objectClass=user)',
        search_scope=SUBTREE,
        attributes=['cn', 'lastLogonTimestamp']
    )

    # boucle pour chaque utilisateur
    for entry in conn.entries:
        cn = entry.cn.value
        lastlogon_raw = entry.lastLogonTimestamp.value

        if lastlogon_raw is None:
            print(f"Utilisateur {cn} : pas de lastLogonTimestamp défini, impossible de calculer l'inactivité.")
            continue

        # Conversion du Windows FileTime (100-ns depuis 1601) en datetime UTC
        if isinstance(lastlogon_raw, datetime.datetime):
            lastlogon_date = lastlogon_raw
        else:
            lastlogon_date = datetime.datetime(1601, 1, 1, tzinfo=datetime.timezone.utc) + \
                            datetime.timedelta(seconds=lastlogon_raw / 1e7)

        # Calcul du nombre de jours depuis le dernier logon
        now = datetime.datetime.now(datetime.timezone.utc)
        days_since_logon = (now - lastlogon_date).days

        print(f"Utilisateur {cn} : dernier logon il y a {days_since_logon} jours.")

        # Blocage si inactivité > 7 jours
        if days_since_logon > 7:
            print(f"-> {cn} n'a pas connecté depuis {days_since_logon} jours (> 7), blocage du compte…")
            # userAccountControl = 512 => compte actif
            # userAccountControl = 514 => compte désactivé
            success = conn.modify(
                entry.entry_dn,
                {'userAccountControl': [(MODIFY_REPLACE, [514])]}
            )
            if success:
                print(f"{cn} bloqué avec succès.")
            else:
                print(f"Échec du blocage pour {cn} : {conn.result}")
        else:
            print(f"-> {cn} reste actif (inactivité de {days_since_logon} jours).")

    # Nettoyage
    conn.unbind()

if __name__ == "__main__":
    main()