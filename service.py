from bot import Bot_runner
from os import path, chdir

if __name__=="__main__":
    self_path = path.dirname(path.realpath(__file__))
    chdir(self_path)
    bot = Bot_runner(log_folder="/var/log")
    bot.start(try_restart=False)