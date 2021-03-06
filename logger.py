from datetime import datetime, timedelta
import inspect
from typing import Callable, List
from enum import Enum
from os import path, walk, remove
from sys import stdout
from shutil import copy

class LEVEL(Enum):
    WARNING = "WARNING"
    INFO = "INFO"
    ERROR = "ERROR"
    DEBUG = "DEBUG"
    HEADER = "HEADER"

    def from_string(string: str) -> 'LEVEL':
        for lvl in [LEVEL.DEBUG, LEVEL.INFO, LEVEL.WARNING, LEVEL.ERROR, LEVEL.HEADER]:
            if lvl.value.lower() == string.lower(): return lvl
        return None

    def get_hierarchy(selected: 'LEVEL') -> List['LEVEL']:
        tmp = [LEVEL.DEBUG, LEVEL.INFO, LEVEL.WARNING, LEVEL.ERROR, LEVEL.HEADER]
        if isinstance(selected, str): selected = LEVEL.from_string(selected)
        return tmp[tmp.index(selected):]
        
class COLOR(Enum):
    INFO = "\033[92m"
    ERROR = "\033[91m"
    WARNING = "\033[93m"
    HEADER = "\033[94m"
    DEBUG="\033[95m"
    END = "\033[0m"

    def from_level(level: LEVEL) -> "COLOR":
        return getattr(COLOR, level.value)

class logger_class:
    __slots__ = "log_file", "allowed", "log_to_console", "storage_life_extender_mode", "stored_logs", "max_logfile_size", "max_logfile_lifetime", "__print", "use_caller_name", "use_file_names"

    def __init__(
        self, 
        log_file: str, 
        clear: bool = False, 
        level: LEVEL = LEVEL.INFO, 
        log_to_console: bool = False, 
        storage_life_extender_mode: bool = False, 
        max_logfile_size: int = -1, 
        max_logfile_lifetime: int = -1,
        __print: Callable = stdout.write,
        use_caller_name: bool = False,
        use_file_names: bool = True
    ) -> None:
        self.log_file = log_file
        self.allowed = LEVEL.get_hierarchy(level)
        self.log_to_console = log_to_console
        self.storage_life_extender_mode = storage_life_extender_mode
        self.stored_logs = []
        self.max_logfile_size = max_logfile_size
        self.max_logfile_lifetime = max_logfile_lifetime
        self.__print = __print
        self.use_caller_name = use_caller_name
        self.use_file_names = use_file_names
        if clear:
            with open(log_file, "w"): pass

    def __check_logfile(self) -> None:
        if self.max_logfile_size != -1 and (path.getsize(self.log_file) / 1024^2) > self.max_logfile_size:
            tmp = self.log_file.split(".")
            tmp[0] += str(datetime.now())
            new_name = ".".join(tmp)
            copy(self.log_file, new_name)

        if self.max_logfile_lifetime != -1:
            names = self.__get_all_logfile_names()
            for name in names:
                if datetime.now() - datetime.fromtimestamp(path.getctime(name)) > timedelta(days=self.max_logfile_lifetime):
                    remove(name)

    def __get_all_logfile_names(self) -> List[str]:
        for dir_path, _, filenames in walk(path.dirname(self.log_file)):
            return [path.join(dir_path, fname) for fname in filenames if self.log_file.split(".")[-1] in fname]

    def __log_to_file(self, log_msg: str, flush: bool = False) -> None:
        if self.storage_life_extender_mode:
            self.stored_logs.append(log_msg)
        else:
            with open(self.log_file, "a") as f:
                f.write(log_msg)
                f.write("\n")
        if len(self.stored_logs) > 500 or flush:
            with open(self.log_file, "a") as f:
                f.write("\n".join(self.stored_logs))
                self.stored_logs = []
        self.__check_logfile()

    def __get_caller_name(self):
        frames = inspect.getouterframes(inspect.currentframe().f_back.f_back, 2)
        caller = f"{frames[1].function if frames[1].function != 'log' else frames[2].function}"
        start = 3 if frames[1].function == "log" else 2
        previous_filename = path.basename(frames[start-1].filename)
        if caller == "<module>": return previous_filename
        for frame in frames[start:]:
            if frame.function in ["<module>", "_run_event", "_run_once", "_bootstrap_inner"] or path.basename(frame.filename) in ["threading.py"]: break
            if path.basename(frame.filename) != previous_filename and self.use_file_names:
                caller = f"{frame.function}->{previous_filename}->{caller}"
                previous_filename = path.basename(frame.filename)
            else:
                caller = f"{frame.function}->{caller}"
        return f"{previous_filename}->{caller}" if self.use_file_names else caller
            
    def __log(self, level: LEVEL, data: str, counter: str, end: str) -> None:
        log_msg = f"[{counter}] [{level.value}]: {data}"
        self.__log_to_file(log_msg)
        if self.log_to_console and level in self.allowed:
            if self.use_caller_name:
                caller = self.__get_caller_name()
                log_msg = f"[{counter}] [{caller}]: {data}"
            self.__print(f"{COLOR.from_level(level).value}{log_msg}{COLOR.END.value}{end}")
    
    def get_buffer(self) -> List[str]:
        return self.stored_logs if self.storage_life_extender_mode else []

    def flush_buffer(self):
        if self.storage_life_extender_mode:
            self.__log_to_file("", True)

    def set_level(self, level: LEVEL) -> None:
        self.allowed = LEVEL.get_hierarchy(level)

    def log(self, level: LEVEL, data: str, counter: str = str(datetime.now()), end: str = "\n") -> None:
        if level == LEVEL.INFO:
            self.info(data, counter, end)
        elif level == LEVEL.WARNING:
            self.warning(data, counter, end)
        elif level == LEVEL.ERROR:
            self.error(data, counter, end)
        elif level == LEVEL.HEADER:
            self.header(data, counter, end)
        else:
            self.debug(data, counter, end)

    def header(self, data: str, counter: str = str(datetime.now()), end: str = "\n") -> None:
        decor = list("="*40)
        decor.insert(int(20-len(data) / 2), data)
        final_decor = decor[0:int(20-len(data) / 2) + 1]
        final_decor.extend(decor[int((20-len(data) / 2) + len(data)):])
        self.__log(LEVEL.HEADER, "".join(final_decor), counter, end)

    def debug(self, data: str, counter: str = str(datetime.now()), end: str = "\n") -> None:
        self.__log(LEVEL.DEBUG, data, counter, end)

    def warning(self, data: str, counter: str = str(datetime.now()), end: str = "\n") -> None:
        self.__log(LEVEL.WARNING, data, counter, end)

    def info(self, data: str, counter: str = str(datetime.now()), end: str = "\n") -> None:
        self.__log(LEVEL.INFO, data, counter, end)

    def error(self, data: str, counter: str = str(datetime.now()), end: str = "\n") -> None:
        self.__log(LEVEL.ERROR, data, counter, end)

def test():
    logger = logger_class("asd", True, log_to_console=True, use_caller_name=True)
    logger.info("Info")
    logger.log(LEVEL.INFO, "Log")

if __name__ == "__main__":
    test()