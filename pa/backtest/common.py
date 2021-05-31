from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path

base_path = Path(__file__).parents[1] / "data" / "history"


def standard_filename(from_time: datetime, to_time: datetime, instruments):
    filename = from_time.strftime("%Y.%m.%d") + "-" + to_time.strftime("%Y.%m.%d")
    filename += "[" + "-".join(instruments) + "]" + ".txt"
    return filename


def history_filepath(filename: str):
    history_path = base_path / filename
    if history_path.is_file():
        history_path.unlink()
    return history_path


def filesize(filepath):
    count = 0
    for _ in open(filepath):
        count += 1
        yield count
    return count


class BaseBacktestingData(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def gen(self):
        pass


class BaseBacktestingGen(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def gen(self):
        pass
