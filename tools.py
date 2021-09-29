import youtube_dl, os
from time import sleep

class Downloader:
    count = 0
    AUDIO_OPTS = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            "key":"FFmpegExtractAudio",
            "preferredcodec":"mp3",
            "preferredquality":'192',
        }],
        "progress_hooks": [],
    }
    VIDEO_OPTS = {
        'format': 'best ',
        "progress_hooks": [],
    }
    name: str = ""
    TARGET_FOLDER = "downloads"

    def __init__(self, verbose: bool = True) -> None:
        self.AUDIO_OPTS["progress_hooks"].append(self.progress_hook)
        self.VIDEO_OPTS["progress_hooks"].append(self.progress_hook)
        if not os.path.exists(self.TARGET_FOLDER):
            os.mkdir(self.TARGET_FOLDER)
        self.verbose = verbose

    def set_name(self, name) -> None:
        self.name = name

    def progress_hook(self, d: dict) -> None:
        if not self.verbose: return
        if d["status"] == "finished":
            if self.name == "": self.name = d["filename"]
            print("\rDownload finished, converting...")
    
    def search_actual_file(self) -> None:
        self.name = ".".join(self.name.replace(".part", '').split('.')[:-1])
        _, _, files = os.walk("./").__next__()
        for item in files:
            if self.name in item:
                self.name = item
                return

    def move_file(self) -> None:
        os.replace(self.name, os.path.join(self.TARGET_FOLDER, self.name))
    
    def remove(self, name) -> None:
        if "/" in name and "\\" in name:
            raise ValueError("Only name allowed")
        if not os.path.exists(name):
            name = os.path.join(Downloader.TARGET_FOLDER, name)
        os.remove(name)

    def download(self, url, cach: bool = True, video: bool = False) -> str:
        while self.name != "": sleep(1)
        ytdl_opts = self.AUDIO_OPTS if not video else self.VIDEO_OPTS
        try:
            with youtube_dl.YoutubeDL(ytdl_opts) as ydl:
                ydl.download([url])
            if not video: self.search_actual_file()
            if cach: self.move_file()
            name = self.name
            self.name = ""
            return name
        except: return None