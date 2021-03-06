# Config
$alert_days = 14
$smtp_server = "10.0.90.30"

#New-EventLog -LogName "Password Management" -Source "Password Expiry"
#New-EventLog -LogName "Password Management" -Source "Password Expiry Email"

# Import Active Directory module
Import-Module ActiveDirectory

# Get date for today
$today = Get-Date -UFormat %m/%d/%Y

# Get password expiry dates for all users
$users_expire = Get-ADUser -filter {Enabled -eq $True -and PasswordNeverExpires -eq $False} -Properties "DisplayName", "EmailAddress","msDS-UserPasswordExpiryTimeComputed" | select-Object -Property "Displayname","EmailAddress",@{Name="ExpiryDate";Expression={[datetime]::FromFileTime($_."msDS-UserPasswordExpiryTimeComputed")}}

# Find users that are $alert_days away from password expiry
foreach ($user in $users_expire) {
    $displayname = $user.DisplayName
    $firstname = $user.DisplayName -split " "
    $firstname = $firstname[0]
    $emailaddress = $user.EmailAddress
    $expirydate = $user.ExpiryDate -split " "
    $expirydate = $expirydate[0] -split "/"
    $expiryday = $expirydate[1]
    $expirymonth = $expirydate[0]
    $expiryyear = $expirydate[2]
    
    $expire_limit = Get-Date -UFormat %m/%d/%Y (Get-Date -Day $expiryday -Month $expirymonth -Year $expiryyear).AddDays(-$alert_days)
    if ($expire_limit -eq $today) {
        Write-Output "Password for user $displayname will expire in $alert_days days."
        Write-EventLog -LogName "Password Management" -Source "Password Expiry" -EventID 100 -Message "Password for user $displayname will expire in $alert_days days." -EntryType Information
        if ($emailaddress -like "*@*") {
            Write-Output "Sending password expiry email to $emailaddress."
            
            $email = 
@"
Hi $firstname,

Your password will expire in $alert_days days.

Regards,
[Company Name]
"@
            
            Send-MailMessage -To "$emailaddress" -From "noreply@example.com" -Subject "Your password will expire in $alert_days days!" -Body "$email" -Priority High -SmtpServer $smtp_server
            Write-EventLog -LogName "Password Management" -Source "Password Expiry Email" -EventID 200 -Message "Email sent: $email" -EntryType Information
        }
    }
}
