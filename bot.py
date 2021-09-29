import subprocess, os
from platform import system
from time import sleep

interpreter = 'python' if system() == 'Windows' else 'python3'

class Bot_runner:

    def command_exists(self, name):
        if os.path.exists(name):
            os.remove(name)
            return True
        return False

    def start(self):
        self.server = subprocess.Popen([interpreter, "bot_core.py"])
        self.error = True
        while self.server.poll() is None:
            if self.command_exists("restart"):
                self.server.kill()
                while self.server.poll() is None:
                    pass
                self.server = subprocess.Popen([interpreter, "bot_core.py"])
            elif self.command_exists("stop"):
                self.server.kill()
                self.error = False
            sleep(1)
        if self.error:
            ansv = str(input("Du you want to restart the bot? ([Y]/N)") or "y")
            if ansv.lower() == "y":
                self.start()

if __name__ == "__main__":
    runner = Bot_runner()
    runner.start()