from typing import Union, List
import atexit
from tools import Downloader
from smdb_logger import Logger, LEVEL
import smdb_api, os
from time import sleep

class Bot:
    def __init__(self, log_folder="logs") -> None:
        self.downloader = Downloader.from_cofnig(os.path.join(os.path.dirname(__file__), "config.cfg"))
        self.finished = {}
        self.api = smdb_api.API("YTDownloader", "1fc1323c684c0bb53628dda39514f659c0cbe2911aad525d416bb7ca8f8297bd")
        self.logger = Logger("DMB.log", log_folder=log_folder, level=LEVEL.DEBUG, use_file_names=False)
        self.downloader.init_logger(log_folder, LEVEL.DEBUG, True)
        self.downloader.add_finish_hook(self.finish_hook)

    def send_command(self, command):
        with open(command, "w") as f: pass

    def finish_hook(self, url: str, success: bool, reason: str) -> None:
        self.finished[url] = [success, reason]

    def save(self, message: smdb_api.Message) -> None:
        url = message.content.strip()
        results = self.downloader.add_to_queue(url)
        for result in self.await_results(results, url):
            self.api.send_message(result, message.sender)
    
    def await_results(self, resulting_urls: Union[bool, List[str]], original_url: str) -> List[str]:
        if (resulting_urls == False or (isinstance(resulting_urls, list) and len(resulting_urls) == 0)): 
            return ["Either already on the download list, or the list was private or deleted."]
        
        results = []
        if (isinstance(resulting_urls, bool)):
            resulting_urls = [original_url]
        for url in resulting_urls:
            result = None
            while (result := self.finished.pop(url, None)) is None:
                sleep(.1)
            results.append(result[1])
        return results

    def start(self) -> None:
        self.api.validate()
        self.api.create_function("YTDownload", "Downloads an audio from youtube.\nUsage: &YTDownload <URL>\nCategory: NETWORK", self.save, privilege=smdb_api.Privilege.OnlyAdmin, needs_arguments=True)
        self.downloader.start()
    
    def stop(self) -> None:
        self.downloader.stop()

def main() -> None:
    bot = Bot()
    bot.update()
    bot.start()
    atexit.register(bot.stop)

if  __name__ == "__main__":
    main()
