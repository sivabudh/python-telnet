import re
import telnetlib

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


class HuaweiCommunicator:
    PROMPT_REGEX = r'[\<|\[](.*)[\>|\]]'

    def __init__(self):
        self.connection = None
        self.base_prompt = None

    def connect(self, hostname: str, port_number: int = 23, timeout: int = 30):
        self.connection = telnetlib.Telnet(hostname, port_number, timeout)

        self.find("Username:")
        self.send_without_read("test18b")

        self.find("Password:")
        self.send_without_read("test_18b")

        #
        # After a login attempt, try to locate the device's prompt
        #
        expected_regexes = [bytes(HuaweiCommunicator.PROMPT_REGEX, encoding="ascii")]
        index, prompt_regex, output = self.connection.expect(expected_regexes, timeout=3)
        print(output.decode("ascii"))
        if index < 0:
            print("Incorrect username password. Try again, bro.")
            return False
        else:
            self.base_prompt = prompt_regex.group(1).decode("ascii")
            print("Base prompt: ", self.base_prompt)
            return True

    def find(self, expected):
        output = self.connection.read_until(bytes(expected, encoding="ascii"))
        print(output.decode("ascii"), end="")
        return output

    def send_without_read(self, command: str):
        command_to_send = command + "\n"
        self.connection.write(bytes(command_to_send, encoding="ascii"))

    def sendx(self, command: str, expected_regex) -> str:
        command_to_send = command + "\n"
        print("----")
        print("$ ", command_to_send)
        self.connection.write(bytes(command_to_send, encoding="ascii"))

        index, regex_obj, output = self.connection.expect([bytes(expected_regex, encoding="ascii")])
        final_output = output.decode("ascii").replace(command, "")  # removed echo from telnet
        print("````")
        print(final_output, end="")
        print("\n````")
        print("\n----")
        return output

    def expected_regex(self):
        return self.PROMPT_REGEX.format(self.base_prompt)


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
        expected_output_regex = re.escape("[Y/N]")
        comm.sendx(command, expected_regex=expected_output_regex)
    else:
        prompt_regex = comm.expected_regex()
        comm.sendx(command, expected_regex=prompt_regex)

comm.sendx("quit")

"""
Problem we are running into now:
(+) 1) The output echoes what we typed -> need to remove this  --> yeah, we can just save the command we send and remove
(+) 2) Certain commands don't need to expect such as quit
(+) 3) Handling incorrect username/password ...
4) Handling delays ..I'm guess I don't need to delay?
(+) 5) Must read base_prompt
"""
