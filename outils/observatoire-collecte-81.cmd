@echo off
title Observatoire - reprise de la collecte du departement 81
rem ---------------------------------------------------------------------------
rem  LANCEUR A DEPOSER DANS LE DOSSIER DEMARRAGE DE WINDOWS.
rem
rem      %APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
rem
rem  Ecrit le 8 aout 2026, chantier C6. Il ne contient aucune logique : il
rem  appelle le script du depot, qui decide s'il reste quelque chose a
rem  collecter. Quand le departement est entierement traite, ce fichier-ci SE
rem  FAIT SUPPRIMER par celui du depot, pour que la machine ne relance pas une
rem  collecte terminee a chaque ouverture de session.
rem
rem  Trois contraintes de forme, apprises en le testant :
rem
rem    - fins de ligne CRLF obligatoires. Avec des fins de ligne Unix, cmd.exe
rem      se desynchronise et mange le debut de chaque ligne (setlocal devient
rem      tlocal) - sans le moindre message d'erreur exploitable ;
rem    - aucun caractere non-ASCII, y compris dans les commentaires ;
rem    - le chemin du depot passe par sa forme COURTE 8.3, parce que le chemin
rem      long contient un accent (qualite de l'eau) et qu'aucun encodage de
rem      fichier .cmd ne le restitue de facon fiable a toutes les pages de
rem      codes. La forme courte est purement ASCII, donc insensible au
rem      probleme. Elle a ete verifiee le 8 aout 2026.
rem
rem  Pour l'arreter a la main : supprimer ce fichier du dossier Demarrage.
rem  Fermer la fenetre de console interrompt la collecte sans rien perdre : le
rem  journal et le cache brut la font reprendre ou elle en etait.
rem ---------------------------------------------------------------------------
call "C:\Users\ymyta\DOCUME~1\EDITIO~1\2-WATE~1\DATA-A~1\CLAUDE~1\OBSERV~1\outils\reprendre_collecte.cmd" 81
