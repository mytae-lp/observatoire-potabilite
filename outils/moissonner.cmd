@echo off
setlocal enabledelayedexpansion
rem ---------------------------------------------------------------------------
rem  Moisson de plusieurs departements, reprenable apres un arret machine.
rem
rem      outils\moissonner.cmd 69,71,01
rem      outils\moissonner.cmd 69,71,01 6        (6 ouvriers au lieu de 4)
rem
rem  Difference avec reprendre_collecte.cmd : celui-ci n'ouvre JAMAIS la base.
rem  Il remplit le cache brut (le tampon), et rien d'autre. La base reste donc
rem  disponible pendant toute la moisson - c'est tout l'objet du decoupage.
rem
rem  Verser le tampon dans la base est un geste SEPARE, a lancer quand on veut
rem  bien immobiliser la base quelques minutes :
rem
rem      py -X utf8 src\ingerer.py --depts 69,71,01
rem
rem  Ce script :
rem    1. demande a moisson.py si tous les departements sont deja moissonnes ;
rem    2. si non, relance la moisson - qui reprend seule sur son journal, et ne
rem       redemande a Hub'Eau aucun bulletin deja au cache brut ;
rem    3. quand tout est moissonne, RETIRE le lanceur du dossier Demarrage.
rem
rem  Le lanceur est supprime par CE script, jamais par lui-meme : un fichier
rem  .cmd qui s'efface pendant que cmd.exe le lit encore se termine mal.
rem
rem  Pas d'accents dans ce fichier : la page de codes d'une console Windows au
rem  demarrage n'est pas garantie, et un caractere mal decode casse un chemin.
rem ---------------------------------------------------------------------------

set "DEPTS=%~1"
if "%DEPTS%"=="" (
  echo usage : outils\moissonner.cmd 69,71,01 [ouvriers]
  exit /b 2
)
set "OUVRIERS=%~2"
if "%OUVRIERS%"=="" set "OUVRIERS=4"

set "REPO=%~dp0.."
cd /d "%REPO%" || exit /b 1

set "ETIQUETTE=%DEPTS:,=-%"
set "LOG=data\journal\moisson_%ETIQUETTE%.log"
set "LANCEUR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\observatoire-moisson-%ETIQUETTE%.cmd"

if not exist "data\journal" mkdir "data\journal"

py -X utf8 src\moisson.py --depts %DEPTS% --termine >nul 2>&1
if not errorlevel 1 goto :fini

echo. >> "%LOG%"
echo ===== moisson le %date% a %time% (%OUVRIERS% ouvriers) ===== >> "%LOG%"
py -X utf8 src\moisson.py --depts %DEPTS% --tous --ouvriers %OUVRIERS% >> "%LOG%" 2>&1

py -X utf8 src\moisson.py --depts %DEPTS% --termine >nul 2>&1
if errorlevel 1 (
  echo ===== interrompu, une nouvelle session reprendra >> "%LOG%"
  exit /b 1
)

:fini
echo ===== moisson de %DEPTS% terminee le %date% a %time% >> "%LOG%"
echo ===== rien n'est en base : py -X utf8 src\ingerer.py --depts %DEPTS% >> "%LOG%"
if exist "%LANCEUR%" (
  del "%LANCEUR%" >nul 2>&1
  echo ===== lanceur retire du demarrage automatique >> "%LOG%"
)
exit /b 0
