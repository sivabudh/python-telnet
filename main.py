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

    def find(self, expected):
        output = self.connection.read_until(bytes(expected, encoding="ascii"))
        print(output.decode("ascii"), end="")
        return output

    def send_without_read(self, command: str):
        command_to_send = command + "\n"
        self.connection.write(bytes(command_to_send, encoding="ascii"))

    def send(self, command: str, expected=REGEX_PROMPT) -> str:
        command_to_send = command + "\n"
        self.connection.write(bytes(command_to_send, encoding="ascii"))

        output = self.connection.read_until(bytes(expected, encoding="ascii"), timeout=3)
        print(">> ", output.decode("ascii"))
        return output

    def sendx(self, command: str, expected_regex=r'[\<|\[]{}.*?[\>|\]]'.format(REGEX_PROMPT)) -> str:
        command_to_send = command + "\n"
        self.connection.write(bytes(command_to_send, encoding="ascii"))

        index, regex_obj, output = self.connection.expect([bytes(expected_regex, encoding="ascii")])
        print(output.decode("ascii"), end="")
        return output


comm = HuaweiCommunicator()
comm.connect("192.168.1.1")

for command in commands:
    comm.sendx(command)

comm.sendx("quit")

"""
Problem we are running into now:
1) The output echoes what we typed -> need to remove this
2) Certain commands don't need to expect such as quit
"""
