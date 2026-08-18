@echo off
cd /d "%~dp0"
echo QCM cardio — http://127.0.0.1:8765/
echo Ferme cette fenetre pour arreter le serveur.
start "" "http://127.0.0.1:8765/"
python -m http.server 8765
pause
