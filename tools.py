import youtube_dl, os
from time import sleep

class Downloader:
    count = 0
    YDL_OPTS = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            "key":"FFmpegExtractAudio",
            "preferredcodec":"mp3",
            "preferredquality":'192',
        }],
        "progress_hooks": [],
    }
    name = ""
    TARGET_FOLDER = "downloads"

    def __init__(self, verbose: bool = True) -> None:
        self.YDL_OPTS["progress_hooks"].append(self.progress_hook)
        if not os.path.exists(self.TARGET_FOLDER):
            os.mkdir(self.TARGET_FOLDER)
        self.verbose = verbose

    def set_name(self, name) -> None:
        self.name = name

    def progress_hook(self, d: dict) -> None:
        if not self.verbose: return
        if d["status"] == "finished":
            print("\rDownload finished, converting...")
        elif d["status"] == "downloading":
            if self.count >= 3: self.count = 0
            if self.name == "": self.name = d["filename"]
            print(f"\r{d['status']}{'.'*self.count}", end='')
    
    def move_file(self) -> None:
        self.name.replace(".part", '')
        if not os.path.exists(self.name): self.name = '.'.join([*self.name.split('.')[:-1], "mp3"])
        os.replace(self.name, os.path.join(self.TARGET_FOLDER, self.name))
    
    def remove(self, name) -> None:
        if "/" in name and "\\" in name:
            raise ValueError("Only name allowed")
        if not os.path.exists(name):
            name = os.path.join(Downloader.TARGET_FOLDER, name)
        os.remove(name)

    def download(self, url, cach=True) -> str:
        while self.name != "": sleep(1)
        with youtube_dl.YoutubeDL(self.YDL_OPTS) as ydl:
            ydl.download([url])
        if cach: self.move_file()
        name = self.name
        self.name = ""
        return name