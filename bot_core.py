from threading import Thread
from typing import Tuple
from tools import Downloader
from logger import logger_class
import smdb_api, os, updater

class Bot:
    
    def __init__(self) -> None:
        self.downloader = Downloader()
        self.urls = []
        self.do_not_remove = {}
        self.api = smdb_api.API("YTDownloader", "1fc1323c684c0bb53628dda39514f659c0cbe2911aad525d416bb7ca8f8297bd", update_function=self.update)
        self.logger = logger_class("DMB.log", level="DEBUG", log_to_console=True, use_file_names=False)

    def send_command(self, command):
        with open(command, "w") as f: pass

    def update(self):
        if updater.main():
            self.api.close("update")
            self.send_command("restart")

    def download(self, url: str, cach: bool, video: bool) -> Tuple[str, str]:
        if self.downloader.is_downloaded(url, video):
            self.logger.debug("File present!")
            name = self.downloader.find_file(url)
            return [name, os.path.abspath(os.path.join(os.path.curdir, Downloader.TARGET_FOLDER, name))]
        self.logger.debug("Download started.")
        name = self.downloader.download(url, cach, video)
        if cach: self.do_not_remove[url] = name
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
        self.api.set_as_hook_for_track_finished(self.track_finished)
        self.api.create_function("YTDownload", "Downloads an audio or a video file from youtube.\nUsage: &YTDownload [video] <URL>\nCategory: NETWORK", self.send_back)
        self.api.create_function("YTSave", "Downloads and saves a video or an audio file from youtube.\nUsage: &YTSave [audio] <URL>\nCategory: NETWORK", self.send_back)
        self.api.create_function("YTPlay", "Plays the selected URL trough the Discord bot.\nUsage: &YTPlay <URL>\nCategory: AUDIO", self.play_Yt)
        self.api.create_function("YTPause", "Pauses the currently playing audio on the Discord bot.\nUsage: &YTPause\nCategory: AUDIO", self.pause)
        self.api.create_function("YTResume", "Resumes the paused audio on the Discord bot.\nUsage: &YTPlay <URL>\nCategory: AUDIO", self.resume)
        self.api.create_function("YTStop", "Stops the currently playing audio on the Discord bot.\nUsage: &YTPlay <URL>\nCategory: AUDIO", self.stop)
        self.api.create_function("YTSkip", "Skips the currently playing audio on the Discord bot.\nUsage: &YTPlay <URL>\nCategory: AUDIO", self.skip)
        self.api.create_function("YTQueue", "Shows the current queue.\nUsage: &YTPlay <URL>\nCategory: AUDIO", self.list_queue)

    def play_Yt(self, message: smdb_api.Message) -> None:
        if message.content is None and len(self.api.get_queue()) > 0: self.api.resume_paused(message.sender)
        if message.content in self.do_not_remove.keys():
            self.api.play_file(self.do_not_remove[message.content], message.sender)
            return
        if self.downloader.is_downloaded(message.content, False) or self.downloader.find_file(message.content) is not None:
            self.logger.debug("File present!")
            name = self.downloader.find_file(message.content)
        else:
            name = self.downloader.download(message.content, True)
        self.api.play_file(os.path.join(os.getcwd(), self.downloader.TARGET_FOLDER, name), message.sender)
        return
    
    def skip(self, message: smdb_api.Message) -> None:
        self.api.skip_currently_playing(message.sender)
    
    def pause(self, message: smdb_api.Message) -> None:
        self.api.pause_currently_playing(message.sender)

    def resume(self, message: smdb_api.Message) -> None:
        self.api.resume_paused(message.sender)

    def list_queue(self, message: smdb_api.Message) -> None:
        queue = self.api.get_queue()
        self.api.send_message("\n".join(f"{i} -> {item}" for i, item in enumerate(queue)) if queue is not None else "Nothing is playing", message.channel)
    
    def stop(self, message: smdb_api.Message) -> None:
        self.api.stop_currently_playing(message.sender)

    def track_finished(self, message: smdb_api.Message) -> None:
        if message.content.split('\\')[-1].split('/')[-1] not in self.do_not_remove.values():
            os.remove(message.content)

    #TODO Play music in discord voice using the download function


def main() -> None:
    bot = Bot()
    bot.update()
    bot.start()

if  __name__ == "__main__":
    main()