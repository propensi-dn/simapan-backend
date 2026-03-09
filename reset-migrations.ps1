$ErrorActionPreference = 'Stop'

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot

$apps = @('users', 'members', 'config', 'notifications', 'savings')

foreach ($app in $apps) {
    Get-ChildItem "$app\migrations" -Filter "*.py" |
        Where-Object { $_.Name -ne '__init__.py' } |
        Remove-Item -Force
}

& .\.venv\Scripts\python manage.py makemigrations $apps
& .\.venv\Scripts\python manage.py migrate

Write-Output 'Migrations reset and reapplied successfully.'
