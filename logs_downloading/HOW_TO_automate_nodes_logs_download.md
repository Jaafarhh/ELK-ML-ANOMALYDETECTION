#### Il faut commencer par rendre le script éxécutable

chmod +x logs_donwload_script.sh

#### Ensuite il faut ouvrir l'éditeur cron via la console.

crontab -e

# Il faut ensuite ajouter la ligne suivant epour que le script s'éxécute toute les minutes.

"\* \* \* \* \* /home/elastic/silver_logs/logs_download_script.sh >> /home/elastic/silver_logs/logs_download_execution.log 2>&1"

- > > /chemin/vers/logs_download_execution.log : Redirige la sortie vers un fichier log pour suivre l'exécution.
- 2>&1 : Redirige également les erreurs vers le même fichier log
