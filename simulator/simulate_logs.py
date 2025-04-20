import socket
import time
import csv
import os
import sys

LOGSTASH_HOST = "logstash"
LOGSTASH_PORT = 5045
CSV_FILE_PATH = "/data/corrupted_logs.csv" # Path inside the simulator container
# --- Simulation Speed ---
# Adjust the delay (in seconds) between sending lines.
# 0.1 = 10 logs/sec (~5.5 hours for 200k logs)
# 1.0 = 1 log/sec (~55 hours for 200k logs)
# 0.01 = 100 logs/sec (~33 mins for 200k logs)
DELAY_BETWEEN_LINES = 0.001

def connect_to_logstash(host, port, max_retries=10, delay=5):
    """Attempts to connect to Logstash with retries."""
    retries = 0
    while retries < max_retries:
        try:
            print(f"Attempting to connect to Logstash at {host}:{port}...")
            sock = socket.create_connection((host, port), timeout=10)
            print("Successfully connected to Logstash.")
            return sock
        except socket.error as e:
            print(f"Connection attempt {retries + 1}/{max_retries} failed: {e}")
            retries += 1
            if retries < max_retries:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print("Max retries reached. Could not connect to Logstash.")
                return None

def send_logs():
    """Reads the CSV and sends logs to Logstash."""
    sock = connect_to_logstash(LOGSTASH_HOST, LOGSTASH_PORT)
    if not sock:
        sys.exit("Exiting: Failed to establish connection with Logstash.")

    line_count = 0
    try:
        with open(CSV_FILE_PATH, 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            header = next(reader) # Skip header row
            print(f"Skipped header: {header}")
            print(f"Starting log simulation with delay: {DELAY_BETWEEN_LINES}s per line...")

            for row in reader:
                try:
                    # Reconstruct the line as it was (Logstash will parse)
                    line = ",".join(row) + '\n'
                    sock.sendall(line.encode('utf-8'))
                    line_count += 1
                    if line_count % 100 == 0: # Print progress every 100 lines
                        print(f"Sent {line_count} lines...")
                    time.sleep(DELAY_BETWEEN_LINES)
                except socket.error as e:
                    print(f"\nSocket error during send: {e}. Attempting to reconnect...")
                    sock.close()
                    sock = connect_to_logstash(LOGSTASH_HOST, LOGSTASH_PORT)
                    if not sock:
                         print("Reconnection failed. Aborting.")
                         break # Exit the loop if reconnection fails
                    else:
                         print("Reconnected. Resuming send...")
                         # Optional: Resend the last failed line? For simplicity, we skip.
                except Exception as e:
                    print(f"\nError processing row: {row}")
                    print(f"Error: {e}")
                    # Decide whether to continue or stop on other errors
                    # continue

    except FileNotFoundError:
        print(f"Error: CSV file not found at {CSV_FILE_PATH}")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
    finally:
        if sock:
            print(f"\nFinished sending logs. Total lines sent: {line_count}")
            print("Closing connection.")
            sock.close()

if __name__ == "__main__":
    # Add a small delay before starting to allow Logstash to be ready
    print("Waiting 15 seconds for Logstash to initialize...")
    time.sleep(15)
    send_logs()