# Mon projet AD Automation

Un ensemble de scripts pour gérer les unités d'organisation (OU) et les comptes utilisateurs Active Directory, avec tests automatisés Python et PowerShell.

## Table des matières

- [Prérequis](#prérequis)
- [Installation](#installation)
- [Tests Python](#tests-python)
- [Tests PowerShell](#tests-powershell)
- [Exécution des scripts](#exécution-des-scripts)
  - [1. Création de l'OU et des utilisateurs](#1-création-de-lou-et-des-utilisateurs)
  - [2. Activation des utilisateurs](#2-activation-des-utilisateurs)
  - [3. Tests post-activation](#3-tests-post-activation)
  - [4. Désactivation des utilisateurs inactifs](#4-désactivation-des-utilisateurs-inactifs)
- [Licence](#licence)

---

## Prérequis

- Python 3.8+
- Poetry (ou `pip` pour `requirements.txt`)
- PowerShell 5.1+
- Module PowerShell Pester (installé ci-dessous)

## Installation

1. Installer les dépendances Python via Poetry :

   ```bash
   poetry install
   ```

   *ou via `pip` :*

   ```bash
   pip install -r requirements.txt
   ```

## Tests Python

Exécuter les tests unitaires pour les fonctions AD :

```bash
python -m unittest test_ad_functions.py
```

## Tests PowerShell

Avant de lancer les tests Pester, ouvrir PowerShell en administrateur et autoriser les scripts :

```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force
```

Installer Pester (si non déjà présent) :

```powershell
Install-Module -Name Pester -Force -SkipPublisherCheck
```

Lancer les tests :

```powershell
Invoke-Pester -Path .\Test-ChangeUserPasswordsAndStatus.Tests.ps1
```

## Exécution des scripts

### 1. Création de l'OU et des utilisateurs

```bash
python createOU_USR.py
```

> Vérifiez dans Active Directory que l'OU et les 3 comptes utilisateurs ont bien été créés.

### 2. Activation des utilisateurs

```powershell
.\ActivateUsers.ps1
```

> Tous les comptes doivent passer en état « activé ».

### 3. Tests post-activation

Re-lancer les tests Pester pour valider l'activation :

```powershell
Invoke-Pester -Path .\Test-ChangeUserPasswordsAndStatus.Tests.ps1
```

### 4. Désactivation des utilisateurs inactifs

Attendre au moins 24 heures, puis exécuter :

```bash
python lastLogon.py
```

> Les comptes n'ayant pas eu de connexion depuis au moins 1 jour seront désactivés.

## Licence

Ce projet est sous licence MIT. Pour plus de détails, voir le fichier `LICENSE`.

