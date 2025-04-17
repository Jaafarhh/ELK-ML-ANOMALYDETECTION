import os
import re
from elasticsearch import Elasticsearch

# Chemin des fichiers logs
log_files = ["/var/log/user.log", "/var/log/syslog", "/var/log/kern.log"]

# Vérifier que les fichiers existent
for log_file in log_files:
    if not os.path.exists(log_file):
        print(f"Le fichier {log_file} n'existe pas.")
        exit(1)


# Cette Fonction analyse une ligne de log et extrait les informations utiles
def parse_log_line(log_line):
    log_pattern = r"^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+\+\d{2}:\d{2}) (\S+) (\S+?)(?:\[(\d+)\])?: (.+)$"
    match = re.match(log_pattern, log_line)
    if match:
        date, hostname, process, id_process, message = match.groups()
        return {
            "Date": date,
            "Hostname": hostname,
            "Process": process,
            "IdProcess": id_process if id_process else "N/A",
            "Message": message,
        }
    return None


# On lit les fichiers logs et on les structure.
data = []
for log_file in log_files:
    with open(log_file, "r") as file:
        for line in file:
            parsed_line = parse_log_line(line.strip())
            if parsed_line:
                data.append(parsed_line)

# On vérifie les données extraites
if not data:
    print("Aucune donnée n'a été extraite des fichiers logs.")
    exit(1)

# Connexion à Elasticsearch
#################################################
es = Elasticsearch(
    ["http://10.78.104.59:9200/"]
)  # ATTENTION : Ici l'adresse ip du noeuds du cluster est propre à chaque machine. Il faut donc ajuster cette valeur en fonction de la configuration.
#############################################"###
if not es.ping():
    print("Impossible de se connecter à Elasticsearch.")
    exit(1)

# On indexe les données dans Elasticsearch
index_name = "data_hilbert09"  # ATTENTION : Ici le nom de l'index du noeud du cluster est propre à chaque machine. Il faut donc ajuster cette valeur en fonction de la configuration.
for entry in data:
    response = es.index(index=index_name, document=entry)
    if response.get("result") != "created":
        print(f"Erreur lors de l'indexation de la ligne : {entry}")

print(f"Données indexées avec succès dans l'index '{index_name}'.")


# VOn vérifie que les données ont été indexées
try:
    response = es.search(index=index_name, body={"query": {"match_all": {}}})
    hits = response.get("hits", {}).get("hits", [])
    if hits:
        print(f"{len(hits)} documents indexés dans Elasticsearch :")
        for hit in hits[:5]:  # Pour être sûr, on affiche les 5 premiers documents
            print(hit["_source"])
    else:
        print("Aucun document trouvé dans Elasticsearch.")
except Exception as e:
    print(f"Erreur lors de la vérification des données dans Elasticsearch : {e}")
