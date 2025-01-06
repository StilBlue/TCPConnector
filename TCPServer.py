import socket
from threading import Thread
from message import Message

serverPort = 18000
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
host_name = socket.gethostname()
ip = socket.gethostbyname(host_name)

serverSocket.bind(('',serverPort))
serverSocket.listen(10)

print("Socket Bound")
print("Server IP: ", ip, " Server Port: ", serverPort)

active_clients = {}
waiting_clients = []
message_history = []

print ('The server is ready to receive')

def receive_message(connection, address):
    while True:
        data = connection.recv(1024)
        if not data:
            waiting_clients.remove(connection)
            break
        sentence = data.decode()
        message = Message()
        message.from_message(sentence)

        if message.report_request_flag:
            response = Message()
            response.report_response_flag = '1'
            response.number = len(active_clients)
            userinfo = ''
            for username in active_clients:
                userinfo += username + '/'
                userinfo += active_clients[username].getpeername()[0] + ':'
                userinfo += str(active_clients[username].getpeername()[1]) + '|'
                response.payload = userinfo
            connection.send(response.to_string().encode())
        elif message.join_request_flag:
            if len(active_clients) >= 3:
                reject_message = Message()
                reject_message.join_reject_flag = 1
                reject_message.set_payload("The server rejects the join request. The chat has reached its maximum capacity.\n")
                connection.send(reject_message.to_string().encode())
            else:
                client_username = message.username[:message.username_length]
                if client_username in active_clients:
                    reject_message = Message()
                    reject_message.join_reject_flag = 1
                    reject_message.set_payload("The server rejects the join request. Another user is using this username.\n")
                    connection.send(reject_message.to_string().encode())
                else:
                    active_clients[client_username] = connection

                    accept_message = Message()
                    accept_message.join_accept_flag = 1
                    accept_message.set_username(client_username)
                    payload = ''
                    for message in message_history:
                        payload += '\n' + message.timestamp + ' ' + message.username[:message.username_length] + ': ' + message.payload[:message.payload_length]

                    accept_message.set_payload(payload)
                    connection.send(accept_message.to_string().encode())

                    new_user_message = Message()
                    new_user_message.new_user_flag = 1
                    new_user_message.set_username('Server')
                    new_user_message.set_payload(client_username + ' joined the chat.')
                    broadcast(new_user_message)
        elif message.quit_request_flag:
            client_username = message.username[:message.username_length]

            leave_message = Message()
            leave_message.quit_accept_flag = 1
            leave_message.set_username("Server")
            print(client_username)
            leave_message.set_payload(client_username + ' left the chat.')
            broadcast(leave_message)

            del active_clients[client_username]
        elif message.attachment_flag:
            file_address = message.filename[:message.filename_length]
            filename = file_address[file_address.rfind('/') + 1:]
            content = message.payload[:message.payload_length]

            file = open('downloads/' + filename, 'w')
            file.write(content)

            broadcast(message)
        else:
            client_username = message.username[:message.username_length]
            broadcast(message)



def broadcast(mess):
    message_history.append(mess)
    for user in active_clients:
        active_clients[user].send(mess.to_string().encode())
    print(mess.timestamp + ' ' + mess.username[:mess.username_length] + ': ' + mess.payload[:mess.payload_length])

while True:
    try:
        connectionSocket, addr = serverSocket.accept()

        print(addr, " connected!")
        waiting_clients.append(connectionSocket)

        thread = Thread(target=receive_message, args=(connectionSocket, addr))
        thread.daemon = True
        thread.start()
    except KeyboardInterrupt:
        for client in active_clients:
            client.close()
        serverSocket.close()
        break
