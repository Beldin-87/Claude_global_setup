# Persoenliches PowerShell-Profil (versionierbar, ausserhalb von OneDrive).
# Geladen vom Stub unter $PROFILE.

# PATH aus der Registry (Machine + User) neu einlesen, damit Tools sofort
# verfuegbar sind, die nach dem Start der Elternanwendung installiert wurden
# (z. B. skillspector aus dem pip --user Scripts-Ordner).
$env:Path = [Environment]::GetEnvironmentVariable('Path','Machine') + ';' + [Environment]::GetEnvironmentVariable('Path','User')
