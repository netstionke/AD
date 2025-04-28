Faire un poetry install

pip install -r requirements.txt

python -m unittest test_ad_functions.py

Run le script python "createOU_USR.py", vérifier la création de l'OU et des 3 users,

Avant de run le prochain script, Set-ExecutionPolicy Bypass et le run en admin

Install-Module -Name Pester -Force -SkipPublisherCheck

Invoke-Pester -Path .\Invoke-Pester -Path .\Test-ChangeUserPasswordsAndStatus.Tests.ps1

Run le script ActivateUsers.ps1, les utilisateurs doivent être activés

Puis re-faire Invoke-Pester -Path .\Test-ChangeUserPasswordsAndStatus.Tests.ps1

Une fois le test user validé, attendre un jour pour faire le script lastLogon.py, qui va désactiver les utilisateurs pas connecter depuis au moins 1j
