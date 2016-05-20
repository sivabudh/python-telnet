import telnetlib
import re

"""
Connect
For each command
    Send command
    Receive output
"""

commands = [
    "",
    "",
    "screen-length 0 temporary",
    "system-view",
    "interface GigabitEthernet0/0/1",
    "display this | i traffic-policy",
    "undo traffic-policy inbound",
    "quit",
    "traffic behavior 12345",
    "car cir 10500 cbs 77500",
    "quit",
    "interface GigabitEthernet0/0/1",
    "traffic-policy EPL inbound",
    "return",
    "save",
    "y",
    "display traffic behavior user-defined 12345",
    "quit",
]

PROMPT = '<18B-S2300>'
REGEX_PROMPT = '18B-S2300'


class HuaweiCommunicator:
    def __init__(self):
        self.connection = None

    def connect(self, hostname: str, port_number: int = 23, timeout: int = 30):
        self.connection = telnetlib.Telnet(hostname, port_number, timeout)

        self.find("Username:")
        self.send_without_read("test18b")

        self.find("Password:")
        self.send_without_read("test_18b")

        # must handle incorrect username / password here
        # for example, ..

        # Must do an extra read here to "clear the buffer"
        expected_regex = r'[\<|\[]{}.*?[\>|\]]'.format(REGEX_PROMPT)
        index, regex_obj, output = self.connection.expect([bytes(expected_regex, encoding="ascii")], timeout=1)
        if index < 0:
            print("Incorrect username password. Try again, bro.")
            return False
        else:
            return True

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
        print("----")
        print("$ ", command_to_send)
        self.connection.write(bytes(command_to_send, encoding="ascii"))

        print(expected_regex)
        index, regex_obj, output = self.connection.expect([bytes(expected_regex, encoding="ascii")])
        final_output = output.decode("ascii").replace(command, "")  # removed echo from telnet
        print("````")
        print(final_output, end="")
        print("\n````")
        print("\n----")
        return output


comm = HuaweiCommunicator()
able_to_login = False
for _ in range(3):
    if comm.connect("192.168.1.1"):
        able_to_login = True
        break

if not able_to_login:
    print("Shit man, you cannot login. I'm quittin'.")
    quit()

print("*************")
for command in commands:
    if command is "save":
        prompt = re.escape("[Y/N]")
        comm.sendx(command, expected_regex=prompt)
    else:
        comm.sendx(command)

comm.sendx("quit")

"""
Problem we are running into now:
(+) 1) The output echoes what we typed -> need to remove this  --> yeah, we can just save the command we send and remove
(+) 2) Certain commands don't need to expect such as quit
(+) 3) Handling incorrect username/password ...
4) Handling delays ..I'm guess I don't need to delay?
5) Must read base_prompt
"""
