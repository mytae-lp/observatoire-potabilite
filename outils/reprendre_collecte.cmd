@echo off
setlocal enabledelayedexpansion
rem ---------------------------------------------------------------------------
rem  Reprise autonome d'une collecte departementale, apres un arret machine.
rem
rem      outils\reprendre_collecte.cmd 81
rem
rem  Ce script est concu pour etre appele au demarrage de la session Windows,
rem  par un petit lanceur depose dans le dossier Demarrage. Il :
rem
rem    1. demande a fetch_departement.py si le departement est deja termine ;
rem    2. si non, relance la collecte - qui reprend seule sur son journal, et
rem       ne redemande a Hub'Eau aucun bulletin deja au cache brut ;
rem    3. quand tout est traite, RETIRE le lanceur du dossier Demarrage, pour
rem       que la machine ne relance pas une collecte terminee a chaque session.
rem
rem  Le lanceur est supprime par CE script, jamais par lui-meme : un fichier
rem  .cmd qui s'efface pendant que cmd.exe le lit encore se termine mal.
rem
rem  Pas d'accents dans ce fichier : la page de codes d'une console Windows au
rem  demarrage n'est pas garantie, et un caractere mal decode casse un chemin.
rem ---------------------------------------------------------------------------

set "DEPT=%~1"
if "%DEPT%"=="" set "DEPT=81"

set "REPO=%~dp0.."
cd /d "%REPO%" || exit /b 1

set "LOG=data\journal\collecte_%DEPT%.log"
set "LANCEUR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\observatoire-collecte-%DEPT%.cmd"

if not exist "data\journal" mkdir "data\journal"

py -X utf8 src\fetch_departement.py --dept %DEPT% --termine >nul 2>&1
if not errorlevel 1 goto :fini

echo. >> "%LOG%"
echo ===== reprise automatique le %date% a %time% ===== >> "%LOG%"
py -X utf8 src\fetch_departement.py --dept %DEPT% --tous >> "%LOG%" 2>&1

py -X utf8 src\fetch_departement.py --dept %DEPT% --termine >nul 2>&1
if errorlevel 1 (
  echo ===== interrompu, une nouvelle session reprendra >> "%LOG%"
  exit /b 1
)

:fini
echo ===== departement %DEPT% termine le %date% a %time% ===== >> "%LOG%"
if exist "%LANCEUR%" (
  del "%LANCEUR%" >nul 2>&1
  echo ===== lanceur retire du demarrage automatique >> "%LOG%"
)
exit /b 0
