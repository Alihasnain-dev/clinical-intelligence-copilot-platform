param(
    [string]$EnvFile = ".env"
)

if (!(Test-Path $EnvFile)) {
    throw "Environment file '$EnvFile' not found."
}

Get-Content $EnvFile | ForEach-Object {
    if ($_ -match '^[\s]*($|#)') { return }
    $kv    = $_ -split '=', 2
    $name  = ($kv[0] -replace '[^!-~]', '').Trim()
    $value = $kv[1].Trim().Trim('"')
    [Environment]::SetEnvironmentVariable($name, $value, 'Process')
    Write-Host "Loaded $name"
}
