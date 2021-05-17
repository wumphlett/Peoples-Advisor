from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import List

base_path = Path(__file__).parents[1] / "data" / "history"


def standard_file_name(instruments: List[str], from_time: datetime, to_time: datetime):
    file_name = from_time.strftime("%Y.%m.%d") + "-" + to_time.strftime("%Y.%m.%d")
    file_name += "[" + "-".join(instruments) + "]" + ".txt"
    return file_name


def history_file_path(file_name: str):
    history_path = base_path / file_name
    if history_path.is_file():
        history_path.unlink()
    return history_path


def file_size(file_path):
    count = 0
    for _ in open(file_path):
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
