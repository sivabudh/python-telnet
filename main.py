import telnetlib

"""
Connect
For each command
    Send command
    Receive output
"""

commands = [
    "screen-length 0 temporary",
    "system-view",
    "interface GigabitEthernet0/0/1",
    "display this | i traffic-policy",
    "quit",
]

PROMPT = '<18B-S2300>'
REGEX_PROMPT = '18B-S2300'


class HuaweiCommunicator:
    def __init__(self):
        self.connection = None

    def connect(self, hostname: str, port_number: int = 23, timeout: int = 8):
        self.connection = telnetlib.Telnet(hostname, port_number, timeout)

        self.find("Username:")
        self.send_without_read("test18b")

        self.find("Password:")
        self.send_without_read("test_18b")

        self.find("<")

    def find(self, expected):
        output = self.connection.read_until(bytes(expected, encoding="ascii"))
        print("find: ", output.decode("ascii"))
        return output

    def send_without_read(self, command: str):
        command_to_send = command + "\n"
        print("sending: ", command)
        self.connection.write(bytes(command_to_send, encoding="ascii"))

    def send(self, command: str) -> str:
        command_to_send = command + "\n"
        print("sending: ", command)
        self.connection.write(bytes(command_to_send, encoding="ascii"))

        output = self.connection.read_until(bytes(PROMPT, encoding="ascii"))
        print("recvd: ", output.decode("ascii"))
        return output

    def sendx(self, command: str) -> str:
        command_to_send = command + "\n"
        print("sending: ", command)
        self.connection.write(bytes(command_to_send, encoding="ascii"))

        regex = r'[\<|\[]{}.*?[\>|\]]'.format(REGEX_PROMPT)
        index, regex_obj, output = self.connection.expect([bytes(regex, encoding="ascii")])
        print("recvd: ", output.decode("ascii"))
        return output


comm = HuaweiCommunicator()
comm.connect("192.168.1.1")
comm.sendx("screen-length 0 temporary")
comm.sendx("display current-configuration")

for command in commands:
    comm.sendx(command)
