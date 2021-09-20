from tools import Downloader
import smdb_api, os

class Bot:
    
    def __init__(self) -> None:
        self.downloader = Downloader()
        self.api = smdb_api.API("YTDownloader", "1fc1323c684c0bb53628dda39514f659c0cbe2911aad525d416bb7ca8f8297bd")
        self.api.validate()
        self.api.create_function("YTDownload", "Downloads a video from youtube\nUsage: &YTDownload <URL>\nCategory: NETWORK", self.send_back)

    def download(self, url: str) -> list:
        name = '.'.join(self.downloader.download(url).split('.')[:-1])
        abs_path = os.path.abspath(os.path.join(os.path.curdir, Downloader.TARGET_FOLDER, f"{name}.mp3"))
        return [name, abs_path]

    def send_back(self, message: smdb_api.Message) -> None:
        _, abs_path = self.download(message.content)
        self.api.send_message("Download finished", message.sender, abs_path)

    #TODO Play music in discord voice using the download function


def main() -> None:
    bot = Bot()

if  __name__ == "__main__":
    main()