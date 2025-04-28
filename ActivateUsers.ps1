Import-Module ActiveDirectory

if (-not $PSScriptRoot) {
    $PSScriptRoot = "."
}
if (-not $global:logFile) {
    $global:logFile = "$PSScriptRoot\log_users.txt"
}
$logFile = $global:logFile
function Generate-RandomPassword {
    param(
        [int]$length = 12  # default lenght
    )
    $chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+' # REGEX authorized charset
    $password = ""
    for ($i = 0; $i -lt $length; $i++) {
        $randIndex = Get-Random -Maximum $chars.Length
        $password += $chars[$randIndex]
    }
    return $password
}

"START : $(Get-Date)" | Out-File -FilePath $logFile

# Get utilisateurs dans l'OU "disabledUser"
$users = Get-ADUser -SearchBase "OU=disabledUser,DC=ynov,DC=local" -Filter *
foreach ($user in $users) {
    $newPassword = Generate-RandomPassword -length 12
    try {
        Set-ADAccountPassword -Identity $user -Reset -NewPassword (ConvertTo-SecureString $newPassword -AsPlainText -Force) # changement pwd
        if ($user.Enabled -eq $false) {
            Enable-ADAccount -Identity $user
        } #activation du comtpe
        #logging reussite
        $logEntry = "$(Get-Date) - Good : $($user.SamAccountName) - new pwd : $newPassword"
        Write-Output $logEntry
        $logEntry | Out-File -FilePath $logFile -Append
    }
    catch {
        # catch si fail
        $errMsg = "$(Get-Date) - Erreur pour $($user.SamAccountName) : $_"
        Write-Output $errMsg
        $errMsg | Out-File -FilePath $logFile -Append
    }
}

"END : $(Get-Date)" | Out-File -FilePath $logFile -Append
