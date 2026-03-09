$ErrorActionPreference = 'Stop'

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot

if (-not (Test-Path ".venv")) {
    python -m venv .venv
}

& .\.venv\Scripts\python -m pip install --upgrade pip
& .\.venv\Scripts\python -m pip install -r requirements.txt

& .\.venv\Scripts\python manage.py makemigrations
& .\.venv\Scripts\python manage.py migrate
& .\.venv\Scripts\python manage.py runserver
