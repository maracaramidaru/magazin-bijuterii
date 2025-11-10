@echo off
REM === Script backup baza de date Django ===
REM Creează un fișier .sql cu toate datele din tabelele definite în models.py

echo === Creare backup pentru baza de date ===
set DATE=%DATE:~6,4%-%DATE:~3,2%-%DATE:~0,2%
set BACKUP_FILE=backup_%DATE%.sql

echo Generare comenzilor INSERT...
python manage.py dumpdata magazin_de_bijuterii --indent 4 > backups\%BACKUP_FILE%

echo Backup completat: backups\%BACKUP_FILE%
pause
