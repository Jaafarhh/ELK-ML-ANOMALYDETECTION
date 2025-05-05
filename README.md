# Détection des Menaces Avancées dans les Logs par l'IA avec ELK (elk-ml-anomalydetection)

Ce dépôt contient le code source et les configurations pour le projet de fin d'année intitulé "Détection des Menaces Avancées dans les Logs de Sécurité par l'Intelligence Artificielle".

**Auteurs:** Salim Wissal, Jalat Salma, Korichi Badr, Alioui Jaafar
**Encadrante:** Prof. El Hassani Sanae
**Institution:** ENSA El Jadida, Université Chouaib Doukkali
**Année Universitaire:** 2024/2025

## Lien vers le Rapport

Pour une compréhension détaillée du contexte, de la méthodologie, de l'analyse des besoins, de la conception, de l'implémentation et de l'évaluation de ce projet, veuillez consulter le rapport complet :

**[Lien vers le Rapport PDF - À METTRE À JOUR LORSQUE DISPONIBLE]**

## Description du Projet

Ce projet implémente un système de détection d'anomalies dans les logs système et applicatifs en combinant :

1.  La **Stack ELK** (Elasticsearch, Logstash, Kibana) pour la collecte, le stockage centralisé et la visualisation des logs.
2.  Des **Règles de Détection Traditionnelles** implémentées dans Logstash pour identifier des motifs de menaces connus.
3.  Un modèle d'**Intelligence Artificielle (Machine Learning)**, spécifiquement **Isolation Forest**, pour détecter des comportements statistiquement anormaux et potentiellement inconnus.
4.  Un **Service Web Flask** pour servir les prédictions du modèle ML et s'intégrer facilement au pipeline Logstash.
5.  **Filebeat** comme agent léger pour collecter les logs sur les machines sources.
6.  **Docker et Docker Compose** pour un déploiement et une gestion facilités de l'ensemble de l'infrastructure.

L'objectif est d'analyser les anomalies et les comportements suspects dans un cluster de machines en temps quasi réel.

*Nota bene : Ce dépôt se concentre sur le modèle d'apprentissage automatique, son intégration dans la stack ELK et son déploiement, plutôt que sur la mise en place initiale du cluster de machines sources.*

## Architecture

Le flux de données général implémenté dans ce projet est le suivant :

`Filebeat (Sources)` -> `Logstash (Port 5044)` -> `[Parsing Grok]` -> `[Appel HTTP au Service ML (Flask)]` -> `[Application Règles Traditionnelles]` -> `[Nettoyage/Formatage Final]` -> `Elasticsearch (Indexation)` -> `Kibana (Visualisation)`

Le service ML (`ml_inference`) s'exécute comme un conteneur distinct et est appelé par Logstash via une requête HTTP pour chaque log pertinent.

Le diagramme ci-dessous illustre l'architecture globale visée :
![Diagramme d'Architecture](https://github.com/user-attachments/assets/fbd0ca65-0769-463a-a6e7-21f3d6836c4b)

## Choix du Modèle (Isolation Forest)

Le choix de l'algorithme Isolation Forest pour prédire les anomalies potentielles dans les logs est soutenu par plusieurs facteurs clés :

*   **Nature Non Supervisée**: Isolation Forest fonctionne sans nécessiter de données étiquetées, ce qui le rend particulièrement adapté à la détection d'anomalies dans les logs où les exemples étiquetés d'anomalies sont rares ou inexistants.
*   **Scalabilité**: Avec une complexité temporelle linéaire, l'algorithme gère efficacement les grands jeux de données. Son approche par sous-échantillonnage assure la scalabilité même avec des fichiers de logs volumineux.
*   **Robustesse en Haute Dimension**: Après l'application de l'encodage One-Hot (et CountVectorizer), notre jeu de données présente une dimensionnalité élevée. Isolation Forest est intrinsèquement robuste dans de tels scénarios, maintenant son efficacité sans baisse significative de performance.
*   **Efficacité de Détection d'Anomalies**: Le principe fondamental de l'algorithme est que les anomalies sont plus faciles à "isoler" que les observations normales. Cette approche unique le rend très efficace pour identifier les outliers dans des jeux de données complexes comme les fichiers de logs.

Ces attributs font d'Isolation Forest un choix optimal pour la détection d'anomalies dans les données de logs, équilibrant performance, scalabilité et robustesse dans des contextes de haute dimension.

## Évaluation du Modèle / Résultats

Pour évaluer la pertinence des prédictions faites par le modèle, les résultats ont été comparés entre un jeu de données sans anomalies connues et un autre contenant des anomalies délibérément introduites (voir notebook `logs_processing_and_predicting/`).

**Test sur Données Normales (Sans Anomalies Connues) :**
Le modèle a été testé sur un jeu de données considéré comme représentatif du fonctionnement normal (similaire à `all_logs.csv` utilisé pour l'entraînement initial, mais potentiellement avec de nouvelles données). L'image ci-dessous (issue d'une exécution du notebook) illustre le nombre d'anomalies détectées. Idéalement, ce nombre devrait être très faible, indiquant un faible taux de faux positifs.
*(Note: L'image originale montrait 0 anomalies détectées sur un jeu de données spécifique "anomaly-free" analysé hors ligne dans le notebook)*
![Résultats - Sans Anomalies (Exemple)](https://github.com/user-attachments/assets/b830143e-33b2-43f8-a3fa-55fe9e316b6e)

**Test sur Données avec Anomalies Introduites :**
Ensuite, des anomalies ont été introduites délibérément pour tester la capacité de détection. Les techniques utilisées pour générer ces logs suspects comprenaient :
*   **SSH Unauthorized Authentication**: Tentatives de connexion SSH avec des identifiants incorrects.
*   **FTP Server**: Connexions au serveur FTP avec des identifiants fictifs.
*   **Flask Application**: Utilisation d'une application Flask pour générer des logs personnalisés simulant des événements inhabituels.

Le modèle a ensuite été testé (via le notebook) sur le jeu de données contenant ces anomalies. Les résultats (illustrés ci-dessous par une exécution du notebook) montrent la capacité du modèle à identifier un nombre significatif de ces logs anormaux.
![Résultats - Avec Anomalies (Exemple)](https://github.com/user-attachments/assets/78476a08-8b1e-4a74-b410-13abffae15d4)

Ces tests (réalisés principalement via le notebook Jupyter) démontrent la capacité de l'Isolation Forest à distinguer les comportements normaux des comportements anormaux introduits. L'évaluation dans le rapport final se base sur l'observation du *pipeline complet* (ELK + ML Service) via Kibana.

## Structure du Dépôt

*   `README.md`: Ce fichier.
*   `docker-compose.yml`: Définit et orchestre les services ELK (Elasticsearch, Logstash, Kibana), Filebeat (pour test), et le service d'inférence ML.
*   `filebeat/`: Contient `filebeat.yml`, un exemple de configuration pour l'agent Filebeat à déployer sur les machines sources.
*   `logstash/pipeline/`: Contient `logstash.conf`, la configuration principale du pipeline Logstash (input, filtres Grok, http, règles, mutate, output Elasticsearch).
*   `ml_inference/`: Contient le code du service Flask (`predict_service.py`), le `Dockerfile` pour le construire, `requirements.txt`, et les fichiers `.pkl` du modèle Isolation Forest et des transformateurs (OneHotEncoder, CountVectorizer) pré-entraînés.
*   `logs_processing_and_predicting/`: Contient le notebook Jupyter (`anomalies_detections_model_training_predictions.ipynb`) utilisé pour l'exploration des données, le prétraitement, l'entraînement du modèle Isolation Forest, et la sauvegarde des modèles/transformateurs (`.pkl`). Inclut également des fichiers `.csv` d'exemples de logs (normaux, corrompus, anomalies connues).
*   `simulator/`: (Optionnel) Un simple script Python et Dockerfile pour simuler l'envoi de logs à Logstash (utile pour tester le pipeline sans Filebeat réel).
*   `logs_downloading/` & `logs_export/`: Scripts utilitaires pour la collecte et l'exportation de logs (contextuels au développement initial du projet, non requis pour l'exécution du pipeline principal Dockerisé).

## Prérequis

*   Docker ([https://www.docker.com/](https://www.docker.com/))
*   Docker Compose ([https://docs.docker.com/compose/install/](https://docs.docker.com/compose/install/))

## Installation et Lancement

1.  Clonez ce dépôt :
    ```bash
    git clone https://github.com/jaafarhh/elk-ml-anomalydetection.git
    cd elk-ml-anomalydetection
    ```
2.  Lancez l'ensemble des services avec Docker Compose :
    ```bash
    docker-compose up -d
    ```
    Cela construira l'image du service `ml_inference` si elle n'existe pas localement et démarrera tous les conteneurs (Elasticsearch, Logstash, Kibana, ml_inference, et Filebeat si non commenté).

## Utilisation

1.  **Collecte des Logs :**
    *   Installez Filebeat sur les machines dont vous souhaitez collecter les logs.
    *   Configurez `/etc/filebeat/filebeat.yml` sur ces machines en vous inspirant de `filebeat/filebeat.yml` dans ce dépôt (notamment les `paths` à surveiller).
    *   Assurez-vous que `output.logstash.hosts` pointe vers l'adresse IP/nom d'hôte de la machine exécutant Docker et le port `5044` (ex: `hosts: ["192.168.1.100:5044"]`).
    *   Démarrez le service Filebeat sur les machines sources (`sudo service filebeat start`).

2.  **Traitement :**
    *   Logstash (lancé via `docker-compose`) écoute sur le port `5044` (input `beats`). Il reçoit les logs de Filebeat, les parse, appelle le service `ml_inference` pour obtenir une prédiction (`ml_anomaly_prediction`: -1 pour anomalie, 1 pour normal), applique les règles traditionnelles (ajoutant des `tags`), et indexe le tout dans Elasticsearch (index `linux-logs-*`).

3.  **Visualisation :**
    *   Accédez à Kibana via votre navigateur : `http://<docker_host_ip>:5601` (ou `http://localhost:5601` si exécuté localement).
    *   Configurez un "Index Pattern" dans Kibana (Stack Management -> Kibana -> Index Patterns -> Create index pattern) en utilisant `linux-logs-*` et `@timestamp` comme champ temporel.
    *   Explorez les logs enrichis dans "Discover". Vous pouvez filtrer sur :
        *   `ml_anomaly_prediction: -1` (Anomalies détectées par l'IA)
        *   `tags: "traditional_alert"` (Alertes déclenchées par les règles)
        *   `ml_anomaly_prediction: -1 AND tags: "traditional_alert"` (Événements détectés par les deux méthodes)
    *   Référez-vous au rapport pour des exemples de visualisations et de tableaux de bord Kibana. Des objets peuvent être importés via Stack Management -> Kibana -> Saved Objects -> Import (si un fichier `export.ndjson` est fourni).

## Entraînement du Modèle

Le modèle Isolation Forest et les transformateurs de prétraitement (OneHotEncoder, CountVectorizer) ont été entraînés à l'aide du notebook `logs_processing_and_predicting/anomalies_detections_model_training_predictions.ipynb`. Les objets résultants (`.pkl`) sont stockés dans `ml_inference/` et `logs_processing_and_predicting/` et sont utilisés par le service d'inférence. Pour ré-entraîner le modèle, exécutez le notebook après avoir fourni des données d'entraînement appropriées (par exemple, en générant un nouveau `all_logs.csv`).
