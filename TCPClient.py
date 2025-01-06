from socket import *
from threading import Thread
from message import Message

username = ''

def request_report():
    report_request = Message()
    report_request.report_request_flag = 1
    client_socket.send(report_request.to_string().encode())

    response = client_socket.recv(1024).decode()
    message = Message()
    message.from_message(response)

    if message.report_response_flag:
        print("There are " + str(message.number) + " active users in the chatroom.")
        i = 1
        for user_info in message.payload.split('|'):
            if not user_info:
                break
            slash_index = user_info.index('/')
            colon_index = user_info.index(':')
            name = user_info[:slash_index]
            ip = user_info[slash_index + 1:colon_index]
            port = user_info[colon_index + 1:]
            print(str(i) + '. ' + name + ' at IP: ' + ip + ' and port: ' + port)
            i += 1

def request_to_join():
    global username
    username = input("Please enter a username: ")
    join_request = Message()
    join_request.join_request_flag = 1
    join_request.set_username(username)

    client_socket.send(join_request.to_string().encode())

    response = client_socket.recv(1024).decode()
    message = Message()
    message.from_message(response)

    if message.join_reject_flag:
        print(message.payload[:message.payload_length])

    elif message.join_accept_flag:
        print(message.payload[:message.payload_length])
        joined_chatroom()



def receive_message(server_socket):
    while True:
        received_message = server_socket.recv(1024).decode()
        message = Message()
        message.from_message(received_message)
        if message.quit_accept_flag and message.payload[:len(username)] == username:
            break

        elif message.attachment_flag and message.username[:message.username_length] != username:
            sender_name = message.username[:message.username_length]
            file_address = message.filename[:message.filename_length]
            filename = file_address[file_address.rfind('/') + 1:]
            content = message.payload[:message.payload_length]

            file = open('downloads/' + filename, 'w')
            file.write(content)

            print(message.timestamp + ' ' + sender_name + ': ' + content)

        else:
            new_message = message.timestamp + ' '
            new_message += message.username[:message.username_length] + ': '
            new_message += message.payload[:message.payload_length]
            print(new_message)


def joined_chatroom():
    t = Thread(target=receive_message, args=(client_socket,))
    t.daemon = True
    t.start()

    while True:
        to_send = input()
        if to_send.lower() == 'q':
            message = Message()
            message.quit_request_flag = 1
            message.set_username(username)
            client_socket.send(message.to_string().encode())
            break

        elif to_send.lower() == 'a':
            message = Message()
            filename = input("Please enter filename: ")
            file = open(filename, "r")
            contents = file.read()

            message.attachment_flag = 1
            message.set_username(username)
            message.set_filename(filename)
            message.set_payload(contents)
            client_socket.send(message.to_string().encode())

        else:
            message = Message()
            message.set_username(username)
            message.payload_length = len(to_send)
            message.payload = to_send
            client_socket.send(message.to_string().encode())

def prompt_choice():
    print("Please select one of the following options:\n"
          "1. Get a report of the chatroom from the server.\n"
          "2. Request to join the chat room.\n"
          "3. Quit the program.\n")
    choice = int(input())
    match choice:
        case 1:
            request_report()
        case 2:
            request_to_join()
        case 3:
            exit()

server_name = 'localhost'
server_port = 18000
client_socket = socket(AF_INET, SOCK_STREAM)
client_socket.connect((server_name,server_port))

while True:
    try:
        prompt_choice()
    except KeyboardInterrupt:
        client_socket.close()
        break
