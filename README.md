# Socket-Based-File-Download-System-for-Multi-Client-Communication
A Python-based file download system using socket programming. Supports concurrent downloads with file prioritization, dynamic input handling, and real-time progress updates.

1. Communication Protocol Between Client and Server
The server initializes and listens for connections through a TCP/IP socket on a specific IP address and port.
When a client connects, the server sends a list of available files in JSON format.
The client receives the file list, reads the file input.txt to determine the files to be downloaded, and sends requests to download specific file chunks.
The server processes the requests, sends the corresponding data to the client, and the client stores the received data on disk.
After completing the download, the client closes the connection when the user presses Ctrl + C, and the server continues listening for new connections.

2. Message Structure
Header:
Includes the IP address and port numbers of both the server and client.
Payload:
Data: The server sends the list of available files to the client. The client then sends the file name to the server, prompting the server to send the corresponding file data to the client.
Footer:
The client saves the downloaded file to the Output folder.
The client ends the connection by pressing Ctrl + C.


4. Message Data Format
The message data is encoded in utf-8. Requests and responses are transmitted as byte strings and are encoded/decoded using utf-8.

5. Development Environment and Supported Frameworks

6. Development Environment
Programming Language: The project is developed using Python.
Python Version: The code is written for Python 3.x to ensure compatibility with the syntax and features of Python 3.x.


7. Supported Frameworks
The project does not rely on large frameworks but instead uses Python's standard library and a few small third-party libraries.


Standard Libraries:
socket: A standard Python library for network programming, supporting TCP/IP connections.
threading: Used to manage threads, enabling the server to handle multiple client connections concurrently.
os: Provides file and directory management functionality.
signal: Handles signals such as Ctrl+C to interrupt the program.
sys: Allows runtime environment manipulations and performs low-level operations.
time: Used for functions like time.sleep().
Third-Party Libraries:
tqdm: A library for creating progress bars in loops, particularly useful for tracking the progress of long-running tasks.


![image](https://github.com/user-attachments/assets/53c99802-fb17-4a7b-a5b8-1f13fbbc7058)


![image](https://github.com/user-attachments/assets/318498cf-a389-48b9-990c-cd2cc5532bb6)


![image](https://github.com/user-attachments/assets/5d7dc1a7-c377-4708-839a-c5231a5fcd6b)


