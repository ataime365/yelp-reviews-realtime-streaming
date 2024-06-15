import json
import socket
import time
import pandas as pd

def handle_date(obj):
    """To serialize the date"""
    if isinstance(obj, pd.Timestamp):
        return obj.strftime('%Y-%m-%d %H:%M:%S')
    raise TypeError("Object of type '%s' is not JSON serializable" % type(obj).__name__)

def send_data_over_socket(file_path, host='spark-master', port=9999, chunk_size=2):
    """server: sending data and client: receiving data"""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen(1)
    print(f"Listening for connections on {host}:{port}")
    

    
    last_sent_index = 0 #100
    
    while True:
        conn, addr = s.accept()
        print(f"Connection from {addr}")
        try:
            with open(file_path, 'r') as file:
                # Skipping the lines that were already sent using index  #bookmarks
                for _ in range(last_sent_index):
                    next(file)
                    
                #For the ones that have not been sent already
                records = []
                for line in file:
                    records.append(json.loads(line))
                    if(len(records)) == chunk_size: #2 , printing at each chunk
                        chunk = pd.DataFrame(records)
                        print(chunk)
                        for record in chunk.to_dict(orient='records'):
                            serialized_data = json.dumps(record, default=handle_date).encode('utf-8') #dict to json #then encode is for dict to json also
                            conn.send(serialized_data + b'\n')
                            time.sleep(5)
                            last_sent_index += 1
                            
                        records = [] #resetting the records
                        
        except (BrokenPipeError, ConnectionResetError):
            print("Client disconnected.")
        finally:
            conn.close()
            print("Connection closed")
                    

if __name__ == "__main__":
    send_data_over_socket("datasets/yelp_academic_dataset_review.json")
    
    
