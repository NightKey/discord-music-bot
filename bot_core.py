from typing import Tuple
from tools import Downloader
from logger import logger_class
import smdb_api, os, updater

class Bot:
    
    def __init__(self) -> None:
        self.downloader = Downloader()
        self.urls = []
        self.api = smdb_api.API("YTDownloader", "1fc1323c684c0bb53628dda39514f659c0cbe2911aad525d416bb7ca8f8297bd", update_function=self.update)
        self.logger = logger_class("DMB.log", level="DEBUG", log_to_console=True, use_file_names=False)

    def send_command(self, command):
        with open(command, "w") as f: pass

    def update(self):
        if updater.main():
            self.api.close("update")
            self.send_command("restart")

    def download(self, url: str, cach: bool, video: bool) -> Tuple[str, str]:
        self.logger.debug("Download started.")
        name = self.downloader.download(url, cach, video)
        if name is None: return [None, None]
        abs_path = os.path.abspath(os.path.join(os.path.curdir, Downloader.TARGET_FOLDER if cach else "", name))
        return [name, abs_path]

    def send_back(self, message: smdb_api.Message) -> None:
        url = message.content.replace('video', '').strip()
        if url in self.urls: 
            self.logger.warning("Same url detected")
            self.api.send_message("This url was previously added to be downloaded!", message.sender)
            return
        self.urls.append(url)        
        name, abs_path = self.download(url, False, "video" in message.content)
        if name is None:
            self.urls.remove(url)
            return
        size_mb = (os.path.getsize(abs_path)/1024)/1024
        self.logger.info(f"The downloaded file size is {size_mb:.2f}MB.")
        if self.api.send_message("Download finished", message.sender, abs_path):
            self.delete_file(name, url)
            
    def delete_file(self, name, url):
        self.logger.info(f"Removing the file '{name}'")
        self.downloader.remove(name)
        self.urls.remove(url)

    def save(self, message: smdb_api.Message) -> None:
        url = message.content.replace('audio', '').strip()
        if url in self.urls: 
            self.logger.warning("Same url detected")
            self.api.send_message("This url was previously added to be saved!", message.sender)
            return
        self.urls.append(url)
        name, _ = self.download(url, True, "audio" not in message.content)
        if name is None:
            self.urls.remove(url)
            self.api.send_message("Download failed", message.sender)
            return
        self.api.send_message("Download finished", message.sender)
        self.urls.remove(url)

    def start(self) -> None:
        self.api.validate()
        self.api.create_function("YTDownload", "Downloads an audio or a video file from youtube\nUsage: &YTDownload [video] <URL>\nCategory: NETWORK", self.send_back)
        self.api.create_function("YTSave", "Downloads and saves a video or an audio file from youtube\nUsage: &YTSave [audio] <URL>\nCategory: NETWORK", self.send_back)

    #TODO Play music in discord voice using the download function


def main() -> None:
    bot = Bot()
    bot.update()
    bot.start()

if  __name__ == "__main__":
    main()