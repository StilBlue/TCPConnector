from datetime import datetime

class Message:
    def __init__(self):
        self.timestamp = datetime.now().strftime("[%H:%M:%S]")
        self.report_request_flag = 0
        self.report_response_flag = 0
        self.join_request_flag = 0
        self.join_reject_flag = 0
        self.join_accept_flag = 0
        self.new_user_flag = 0
        self.quit_request_flag = 0
        self.quit_accept_flag = 0
        self.attachment_flag = 0
        self.number = 0
        self.username_length = 0
        self.username = ''
        self.filename_length = 0
        self.filename = ''
        self.payload_length = 0
        self.payload = ''
    def from_message(self, message):
        self.report_request_flag = int(message[0])
        self.report_response_flag = int(message[1])
        self.join_request_flag = int(message[2])
        self.join_reject_flag = int(message[3])
        self.join_accept_flag = int(message[4])
        self.new_user_flag = int(message[5])
        self.quit_request_flag = int(message[6])
        self.quit_accept_flag = int(message[7])
        self.attachment_flag = int(message[8])
        self.number = int(message[9])
        self.username_length = int(message[10:12])
        self.username = message[12:27]
        self.filename_length = int(message[27:30])
        self.filename = message[30:286]
        self.payload_length = int(message[286:289])
        self.payload = message[289:]

    def set_username(self, username):
        self.username_length = len(username)
        self.username = username

    def set_filename(self, filename):
        self.filename_length = len(filename)
        self.filename = filename

    def set_payload(self, payload):
        self.payload_length = len(payload)
        self.payload = payload

    def to_string(self):
        message = str(self.report_request_flag)
        message += str(self.report_response_flag)
        message += str(self.join_request_flag)
        message += str(self.join_reject_flag)
        message += str(self.join_accept_flag)
        message += str(self.new_user_flag)
        message += str(self.quit_request_flag)
        message += str(self.quit_accept_flag)
        message += str(self.attachment_flag)
        message += str(self.number)
        message += "{:<2}" .format(str(self.username_length).zfill(2))
        message += "{:<15}" .format(self.username[:25])
        message += "{:<3}"  .format(str(self.filename_length).zfill(3))
        message += "{:<256}".format(self.filename[:256])
        message += "{:<3}"  .format(str(self.payload_length).zfill(3))
        message += self.payload[:735]
        return message