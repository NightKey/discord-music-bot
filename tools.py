from typing import Dict, Any, Optional, Callable, List, Union
from yt_dlp import YoutubeDL
import os, json
from time import sleep
from threading import Thread, Event
from smdb_logger import Logger, LEVEL
        
class FuckEasyNoLog:
    def debug(self, _: str):
        pass
    def warning(self, _:str):
        pass
    def error(self, _:str):
        pass

class Downloader:
    stop_event: Event = Event()
    queue: List[str] = []
    finished: Dict[str, str] = {}
    download_thread: Optional[Thread] = None
    ydl_opts = {
        'format': "bestaudio/best",
        'ignoreerrors': True,
        'no_warnings': False,
        'extract_flat': False,
        'writesubtitles': False,
        'writethumbnail': False,
        'writeautomaticsub': False,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'keepvideo': False,
        'clean_infojson': True,
        'retries': 3,
        'fragment_retries': 3,
        'noplaylist': False,
        'logger': FuckEasyNoLog()
    }

    def __init__(self, config: Dict[str, str]) -> None:
        self.ydl_opts['paths'] = config
        self.logger: Optional[Logger] = None

    def init_logger(self, log_folder: str, level: LEVEL, enabled: bool) -> None:
        self.logger = Logger("DMB_TOOLS.log", log_folder=log_folder, level=level, log_disabled=(not enabled))
    
    def add_finish_hook(self, hook: Callable[[str, bool, str], None]) -> None:
        self.finish_hook = hook

    def get_name(self, info: Dict[str, Any]) -> str:
        return f"{info.get('title')} [{info.get('id')}].mp3"

    def start(self) -> None:
        if (self.download_thread is not None): return
        if (self.stop_event.is_set()): self.stop_event.clear()
        self.download_thread = Thread(target=self.download, name="download thread")
        self.download_thread.start()
    
    def stop(self) -> bool:
        if (self.stop_event.is_set()): return self.download_thread.is_alive()
        self.stop_event.set()
        self.download_thread.join(10)
        return self.download_thread.is_alive()

    def is_list(sefl, url: str) -> bool:
        return 'list' in url.split('?')[-1].replace('=', '&').split('&')

    def get_all_entries(self, url: str) -> Optional[List[str]]:
        with YoutubeDL(self.ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if (info is None): return None
            return [x['webpage_url'] for x in info.get("entries")]

    def add_to_queue(self, url: str) -> Union[bool, List[str]]:
        if (url in self.queue): return False
        if (not self.is_list(url)):
            self.queue.append(url)
            return True
        result = self.get_all_entries(url)
        if (result is None or len(result) == 0): return []
        self.queue.extend(result)
        return result

    def download(self) -> None:
        while not self.stop_event.is_set():
            while len(self.queue) == 0:
                sleep(.1)
            url = self.queue.pop(0)
            try:
                with YoutubeDL(self.ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)

                    if (info is None):
                        self.finish_hook(url, False, "Info not found!")
                        break
                    
                    ydl.download([url])

                    self.finish_hook(url, True, f"Downloaded video with title {info.get('title')}")
            except Exception as ex: 
                self.logger.error(ex)
                self.finish_hook(url, False, f"{ex}")
    
    @staticmethod
    def from_cofnig(path: str) -> "Downloader":
        with open(path, 'r') as f:
            return Downloader(json.load(f))
