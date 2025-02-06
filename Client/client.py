import os
import socket
import threading
import time
from tqdm import tqdm

SERVER = socket.gethostbyname(socket.gethostname())
PORT = 5050
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
SIZE = 1024

# Path
INPUT_PATH = "input.txt"
current_directory = os.getcwd()
output_path = os.path.join(current_directory, "output")
OUTPUT_FOLDER = output_path

def read_input(filepath, ofs):
    try:
        with open(filepath, "r") as file:
            file.seek(ofs)
            line = file.readline().strip()
            new_pos = file.tell()
        return line, new_pos
    except Exception as e:
        print(f"An error occurred while reading the input file: {e}")
        return "", ofs

def recv_file(client, file_progress, lock):
    while True:
        try:
            msg = client.recv(SIZE).decode(FORMAT)
            if msg == "DISCONNECT":
                break
            
            file_name, chunk_size, chunk_pos, total_size = msg.split("@")
            chunk_size = int(chunk_size)
            chunk_pos = int(chunk_pos)
            total_size = int(total_size)

            file_path = os.path.join(OUTPUT_FOLDER, file_name)

            with lock:
                # Only create a new progress bar if it doesn't already exist
                if file_name not in file_progress:
                    file_progress[file_name] = {
                        "progress": tqdm(total=total_size, desc=file_name, unit="B", unit_scale=True, leave=True),
                        "received": 0
                    }
                else:
                    # Update the existing progress bar if it exists
                    file_progress[file_name]["progress"].total = total_size
                    file_progress[file_name]["progress"].refresh()

            with open(file_path, "ab") as file:
                file.seek(chunk_pos)
                data = client.recv(chunk_size)
                file.write(data)

            with lock:
                file_progress[file_name]["received"] += len(data)
                file_progress[file_name]["progress"].update(len(data))

                if file_progress[file_name]["received"] >= total_size:
                    file_progress[file_name]["progress"].close()
                    del file_progress[file_name]

        except Exception as e:
            print(f"An error occurred while receiving files: {e}")
            break


def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)

    data = client.recv(SIZE).decode(FORMAT)
    cmd, msg = data.split("@")

    if cmd == "OK":
        print(f"[SERVER] {msg}")

        menu_str = client.recv(SIZE).decode(FORMAT)
        menu_list = menu_str.split(",")

        print(f"[SERVER] Menu list: ")
        for e in menu_list:
            print(f"> {e}")

    file_progress = {}
    lock = threading.Lock()
    recv_thread = threading.Thread(target=recv_file, args=(client, file_progress, lock))
    recv_thread.start()

    pos = 0

    while True:
        time.sleep(2)

        data, pos = read_input(INPUT_PATH, pos)

        send_data = ""

        if data:
            if data == "DISCONNECT":
                send_data = "DISCONNECT@N@N"
                client.send(send_data.encode(FORMAT))
                break
            else:
                file_name, priority = data.split(" ")
                send_data = f"NEW@{file_name}@{priority}"
                client.send(send_data.encode(FORMAT))
                print(f"Request to download file {file_name} has been sent to server.")
        else:
            send_data = "EMPTY@N"
            client.send(send_data.encode(FORMAT))

if __name__ == "__main__":
    main()
