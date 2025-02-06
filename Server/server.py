import os
import socket
import threading
import time

SERVER = socket.gethostbyname(socket.gethostname())
PORT = 5050
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
SIZE = 1024

# Path
MENU_PATH = "text.txt"
SERVER_DATA = "Server_Data"

"""
CMD@MSG 
"""

def check_folder(folder_path):
    try:
        # Kiểm tra thư mục có tồn tại không
        if not os.path.exists(folder_path):
            print(f"The folder {folder_path} does not exist.")
            return []

        # Lấy danh sách các tệp tin trong thư mục và dung lượng của chúng
        file_list = []
        for f in os.listdir(folder_path):
            if os.path.isfile(os.path.join(folder_path, f)):
                file_size_bytes = os.path.getsize(os.path.join(folder_path, f))
                file_size_mb = file_size_bytes / (1024 * 1024)
                if file_size_mb > 1024:
                    file_size_gb = file_size_mb / 1024
                    file_list.append(f"{f} {file_size_gb:.2f}GB")
                else:
                    file_list.append(f"{f} {file_size_mb:.2f}MB")

        return file_list
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

def write_text(file_path):
    files = check_folder(SERVER_DATA)

    try:
        with open(file_path, 'w') as file:
            for file_info in files:
                file.write(file_info + '\n')
        print(f"File list written to {file_path}")
    except Exception as e:
        print(f"An error occurred while writing to the file: {e}")

def read_file_list(file_path):
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
            lines = [line.split()[0] for line in lines]
        return lines
    except Exception as e:
        print(f"An error occurred while reading the file list: {e}")
        return []

MENU_LIST = read_file_list(MENU_PATH)

def send_menu(conn, addr):
    try:
        print(f"Sending menu to {addr}.")
        menu_str = ",".join(f for f in MENU_LIST)
        conn.send(menu_str.encode(FORMAT))
    except Exception as e:
        print(f"An error occurred while sending the menu to {addr}: {e}")

def send_file(conn, addr, download_queue):
    try:
        while True:
            if len(download_queue):
                for file_dict in download_queue[:]:  # Lặp qua bản sao của danh sách
                    file_name = file_dict["filename"]
                    file_path = file_dict["filepath"]
                    file_size = file_dict["filesize"]
                    file_priority = file_dict["priority"]

                    if file_priority == "NORMAL":
                        chunk_size = 1024
                    elif file_priority == "HIGH":
                        chunk_size = 4096
                    else:
                        chunk_size = 8192

                    msg_send = f"{file_name}@{chunk_size}@{file_dict['chunk']}@{file_size}"
                    conn.send(msg_send.encode(FORMAT))

                    time.sleep(0.5)

                    with open(file_path, "rb") as file:
                        file.seek(file_dict["chunk"])
                        data = file.read(chunk_size)
                        if not data:
                            continue
                        conn.sendall(data)
                        file_dict["chunk"] += len(data)

                        time.sleep(0.5)

                    if file_dict["chunk"] >= file_size:
                        download_queue.remove(file_dict)
            time.sleep(0.5)
    except Exception as e:
        print(f"An error occurred while sending files to {addr}: {e}")
        conn.close()

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    conn.send("OK@Welcome to the File Server.".encode(FORMAT))
    write_text("text.txt")
    time.sleep(1)
    send_menu(conn, addr)

    download_queue = []

    send_thread = threading.Thread(target=send_file, args=(conn, addr, download_queue))
    send_thread.start()

    while True:
        data = conn.recv(SIZE).decode(FORMAT)
        data = data.split("@")
        cmd = data[0]

        if cmd == "NEW":
            file_name = data[1]
            priority = data[2]

            file_path = os.path.join(SERVER_DATA, file_name)

            if not os.path.exists(file_path):
                print(f"File {file_name} does not exist.")
            else:
                file_size = os.path.getsize(file_path)

                new_dict = {
                    "filename": file_name,
                    "filepath": file_path,
                    "priority": priority,
                    "chunk" : 0,
                    "filesize" : file_size
                }

                download_queue.append(new_dict)

            print(download_queue)

        elif cmd == "EMPTY":
            print("Nothing to send!")

        elif cmd == "DISCONNECT":
            print(f"[{addr}] IS DISCONNECTED")
            conn.close()
            break

def main():
    try:
        print("[STARTING] Server is starting")
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(ADDR)
        server.listen()
        print(f"[LISTENING] Server is listening on {SERVER}")

        while True:
            try:
                conn, addr = server.accept()
                thread = threading.Thread(target=handle_client, args=(conn, addr))
                thread.start()
            except Exception as e:
                print(f"An error occurred while accepting connections: {e}")
    except Exception as e:
        print(f"An error occurred while starting the server: {e}")
    finally:
        server.close()
        print("[SERVER CLOSED]")

if __name__ == "__main__":
    main()
