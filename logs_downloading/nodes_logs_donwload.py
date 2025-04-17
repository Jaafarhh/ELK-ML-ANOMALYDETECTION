from elasticsearch import Elasticsearch
import csv

# Configuration Elasticsearch
ELASTICSEARCH_HOST = "http://10.78.104.59:9200"  # Adresse du cluster Elasticsearch
FIELDS = [
    "Date",
    "Hostname",
    "Process",
    "IdProcess",
    "Message",
]

# Connexion à Elasticsearch
es = Elasticsearch(ELASTICSEARCH_HOST)


# Fonction pour récupérer les logs
def fetch_logs(index_pattern="*", fields=None, size=1000):
    """
    Récupère les logs de tous les index Elasticsearch.
    :param index_pattern: Modèle d'index à interroger (par défaut tous les index avec '*')
    :param fields: Liste des champs à inclure (None pour tous les champs)
    :param size: Nombre maximum de documents à récupérer par requête
    :return: Liste de documents
    """
    query = {
        "_source": fields,
        "query": {"match_all": {}},  # Récupère tous les documents
        "size": size,
    }

    response = es.search(index=index_pattern, body=query, scroll="1m")
    scroll_id = response["_scroll_id"]
    hits = response["hits"]["hits"]

    documents = []
    while hits:
        documents.extend(
            [
                hit["_source"] | {"_index": hit["_index"], "_id": hit["_id"]}
                for hit in hits
            ]
        )
        response = es.scroll(scroll_id=scroll_id, scroll="1m")
        hits = response["hits"]["hits"]

    return documents


# Fonction pour écrire les logs dans un fichier CSV
def write_to_csv(file_name, documents, fields):
    """
    Écrit les logs dans un fichier CSV.
    :param file_name: Nom du fichier CSV
    :param documents: Liste des documents à écrire
    :param fields: Champs à inclure dans le fichier CSV
    """
    with open(file_name, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fields)
        writer.writeheader()

        for doc in documents:
            # Compléter avec des valeurs vides si un champ est manquant
            row = {field: doc.get(field, "") for field in fields}
            writer.writerow(row)


# Exécution principale
if __name__ == "__main__":
    print("Fetching logs from all Elasticsearch indices...")
    logs = fetch_logs(fields=FIELDS)
    print(f"Fetched {len(logs)} logs.")

    print("Writing logs to CSV...")
    write_to_csv("all_logs.csv", logs, FIELDS)
    print("Logs written to all_logs.csv.")
