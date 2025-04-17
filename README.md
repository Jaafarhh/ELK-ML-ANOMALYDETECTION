# Real Time Logs Anomaly Detection using an ELK stack
This repository explains the implementation of a logs anomaly detection architecture using ElasticSearch and Kibana, as well as a machine learning model. The purpose of this architecture is to analyze anomalies and suspicious behavior in a cluster of machines in near real time.

Nota bene : This repository does not deals with the set up of the cluster of machines, but focus more on the development of the machine learning model and its usage in production. 

Therefore, the following explainations will be articulated in 3 main points : 
* Code structure and workflow behaviour.
* Justification of the choosen machine learning model.
* Relevancy of the predictions obtained.

Before diving into the details, the diagrams below illustrates the overall architecture : 
![image](https://github.com/user-attachments/assets/fbd0ca65-0769-463a-a6e7-21f3d6836c4b)


# 1. Code structure and workflow behaviour.

Each nodes of the cluster has a script (see logs_exportation folder) which is executed periodiacally (every minutes) and does the following actions :
* **Log File Check**: Ensures the specified log files exist before processing.
* **Log Parsing**: Extracts structured data (date, hostname, process, etc.) from log lines using regex.
* **Data Structuring**: Reads log files, parses valid lines, and stores them in a list of dictionaries.
* **Elasticsearch Connection**: Connects to an Elasticsearch instance via a defined URL.
* **Data Indexing**: Sends structured log data to an Elasticsearch index which is node's specific.
* **Verification**: Queries the index to ensure logs were successfully added and displays the first five entries.

Once new logs arrived in the elastic search cluster, the master node download the most recent logs them before processing the new logs and predicting anomalies on those last (see logs_downloading). In a nutshell it does the following actions : 
* **Elasticsearch Connection**: Connects to an Elasticsearch cluster at a specified host.
* **Log Retrieval**: Fetches all logs from the Elasticsearch indices using a match_all query, with optional fields and a default batch size of 1000. Scroll API is used for retrieving large datasets.
* **CSV Export**: Writes the retrieved logs to a CSV file (all_logs.csv), ensuring all specified fields are included. Missing fields are filled with empty values.

After downloading the most recent logs of all cluster nodes, those lasts will be processed (encoding, null values check, etc...) to be in the expected shape for the machine learning model. Finally, the dataset is given to the machine learnijg model to predict potential anomalies/suspicious logs. If any anomalies or suspicious logs are found, an email is sent to the cluster manager (sysadmin) to keep him updated on the cluster health. This whole process is described in the logs_process_and_prediction folder and it basically consists of : 
* **Applied one hot encoding** : the new logs read from a csv are transformed into a pandas dataframe and one hot encoding is applied on object variables.
* **Model loading** : The prediction model is loaded into the execution environment to be executed on the encoded data.
* **Model Prediction** : Predictions are obtained thanks to the model.
* **Alerting** : if any suspicious logs or logs that may reflect anomalies are unveiled, an email is send to the cluster manager (sysadmin) with the logs description : message, node name, PID.

# 2. Justification of the choosen machine learning model.

The choice of the Isolation Forest algorithm for predicting potential anomalies in logs is supported by several key factors:

**Unsupervised Nature**:
Isolation Forest operates without the need for labeled data, making it particularly suited for anomaly detection in logs where labeled examples of anomalies are rare or nonexistent.

**Scalability**:
With a linear time complexity, the algorithm efficiently handles large datasets. Its sub-sampling approach ensures scalability even when dealing with extensive log files.

**High-Dimensional Data Robustness**:
After applying one-hot encoding, our dataset exhibits high dimensionality. Isolation Forest is inherently robust in such scenarios, maintaining its effectiveness without a significant performance drop.

**Anomaly Detection Efficiency**:
The algorithm's core principle is that anomalies are easier to isolate than normal observations. This unique approach makes it highly effective at identifying outliers in complex datasets like log files.

These attributes make Isolation Forest an optimal choice for anomaly detection in log data, balancing performance, scalability, and robustness in high-dimensional contexts.

# 3. Relevance of the Predictions Obtained
To evaluate the relevance of the predictions made by the model, I compared the results between two datasets: one without any anomalies (anomaly-free) and another containing deliberately introduced anomalies.

The image below illustrates the number of anomalies detected in the anomaly-free dataset. As expected, the model correctly identified zero anomalies, confirming its reliability in handling normal data.
![image](https://github.com/user-attachments/assets/b830143e-33b2-43f8-a3fa-55fe9e316b6e)

Next, I employed various techniques to generate suspicious logs (anomalies) and create a dataset containing abnormal behavior. These techniques included:

* **SSH Unauthorized Authentication**: I intentionally used incorrect credentials when attempting to SSH into the cluster nodes. This generated warning logs indicating unauthorized access attempts.
* **FTP Server**: I logged into the FTP server using dummy credentials, producing logs that flagged suspicious activities on the node.
* **Flask Application**: Leveraging a Flask application developed by a colleague, I generated custom logs simulating unusual or abnormal events.
The model was then tested on the newly created dataset containing these anomalies. The results are shown below:
![image](https://github.com/user-attachments/assets/78476a08-8b1e-4a74-b410-13abffae15d4)

