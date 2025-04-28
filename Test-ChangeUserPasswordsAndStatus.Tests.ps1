Import-Module Pester

$global:ou = "OU=disabledUser,DC=ynov,DC=local"
$global:logFile = "$PSScriptRoot\log_users.txt"

Describe "Test de modification des comptes utilisateurs dans AD" {
    BeforeAll {
        $global:fakeUsers = @(
            [pscustomobject]@{ SamAccountName = "user1"; Enabled = $false },
            [pscustomobject]@{ SamAccountName = "user2"; Enabled = $false }
        )
        Mock -CommandName Get-ADUser -MockWith {
            param($SearchBase, $Filter, $Properties)
            return $global:fakeUsers
        }
        Mock -CommandName Set-ADAccountPassword -MockWith {
            param($Identity, $Reset, $NewPassword)
        }
        Mock -CommandName Enable-ADAccount -MockWith {
            param($Identity)
            $user = $global:fakeUsers | Where-Object { $_.SamAccountName -eq $Identity.SamAccountName }
            if ($user) {
                $user.Enabled = $true
            }
        }
    }
    Context "Avant l'execution du script" {
        It "Tous les utilisateurs doivent etre desactives" {
            $usersBefore = Get-ADUser -SearchBase $global:ou -Filter * -Properties Enabled
            foreach ($user in $usersBefore) {
                $user.Enabled | Should -BeFalse
            }
        }
    }
    Context "Après l'exécution du script" {
        BeforeAll {
            . "$PSScriptRoot\ActivateUsers.ps1"
        }
        It "Le fichier log_users.txt doit exister" {
            Test-Path -Path $global:logFile | Should -BeTrue
            $logContent = Get-Content -Path $global:logFile
            $logContent.Count | Should -BeGreaterThan 0
        }
    }
}
