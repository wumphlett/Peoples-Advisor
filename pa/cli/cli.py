import argparse
import io
import re
import sys
from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime
from pathlib import Path
from threading import Thread

from prompt_toolkit import PromptSession
from prompt_toolkit import print_formatted_text as print
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.document import Document
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.lexers import Lexer
from prompt_toolkit.output.color_depth import ColorDepth
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.shortcuts import ProgressBar
from prompt_toolkit.shortcuts.progress_bar import formatters
from prompt_toolkit.styles import Style

from pa.backtest.backtest import get_historical_gen, get_backtesting_gen
from pa.backtest.common import file_size
from pa.backtest.common import standard_file_name as history_file_name
from pa.control.control import Control
from pa.event.event import StartEvent, StopEvent, ExitEvent
from pa.settings import color, instruments, live_strategies, backtest_strategies

style = Style.from_dict(
    {
        "red": "#ff3333",
        "green": "#c2d94c",
        "orange": "#ff8f40",
        "blue": "#59c2ff",
        "yellow": "#ffee99",
        "cyan": "#95e6cb",
        "gray": "#b3b1ad",
        "dark-gray": "#4d5566",
        "bgbox": "bg:#4d5566",
    }
)

TRUE_COLOR = ColorDepth.TRUE_COLOR

splash_screen = """\n \
    _______  _______  _______  _______  ___      _______  __   _______   \
    _______  ______   __   __  ___   _______  _______  ______   
    |       ||       ||       ||       ||   |    |       ||  | |       | \
    |       ||      | |  | |  ||   | |       ||       ||      |  
    |    _  ||    ___||   _   ||    _  ||   |    |    ___||__| |  _____| \
    |   _   ||  _    ||  |_|  ||   | |  _____||   _   ||    _ |  
    |   |_| ||   |___ |  | |  ||   |_| ||   |    |   |___      | |_____  \
    |  |_|  || | |   ||       ||   | | |_____ |  | |  ||   |_||_ 
    |    ___||    ___||  |_|  ||    ___||   |___ |    ___|     |_____  | \
    |       || |_|   ||       ||   | |_____  ||  |_|  ||    __  |
    |   |    |   |___ |       ||   |    |       ||   |___       _____| | \
    |   _   ||       | |     | |   |  _____| ||       ||   |  | |
    |___|    |_______||_______||___|    |_______||_______|     |_______| \
    |__| |__||______|   |___|  |___| |_______||_______||___|  |_|

    """

datetime_pattern = (
    r"\([12][90][0-9][0-9],[01]?[0-9],[0123]?[0-9](?:,[0-9]?[0-9]){0,3}\)"
)

allowed_grans = [
    "S5",
    "S10",
    "S15",
    "S30",
    "M1",
    "M2",
    "M4",
    "M5",
    "M10",
    "M15",
    "M30",
    "H1",
    "H2",
    "H3",
    "H4",
    "H6",
    "H8",
    "H12",
    "D",
    "W",
    "M",
]


class HistoryCompleter(Completer):
    def get_completions(self, document, complete_event):
        text = document.text_before_cursor.lstrip()
        if " " in text:
            return
        else:
            word = document.get_word_before_cursor()
            history_files = Path(__file__).parents[1] / "data" / "history"
            if not history_files.is_dir():
                history_files.mkdir()
            history_files = [his_file.name for his_file in history_files.iterdir()]
            for his_file in history_files:
                if his_file.startswith(word):
                    if color:
                        yield Completion(
                            his_file,
                            start_position=-len(word),
                            style="class:yellow,bgbox",
                        )
                    else:
                        yield Completion(
                            his_file,
                            start_position=-len(word),
                        )


class NestedCLiCompleter(Completer):
    def __init__(self):
        self.options = {"backtest": HistoryCompleter()}

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor.lstrip()
        stripped_len = len(document.text_before_cursor) - len(text)
        if " " in text:
            first_term = text.split()[0]
            completer = self.options.get(first_term)

            # If we have a sub completer, use this for the completions.
            if completer is not None:
                remaining_text = text[len(first_term) :].lstrip()
                move_cursor = len(text) - len(remaining_text) + stripped_len

                new_document = Document(
                    remaining_text,
                    cursor_position=document.cursor_position - move_cursor,
                )

                for c in completer.get_completions(new_document, complete_event):
                    yield c

            # No space in the input: behave exactly like `WordCompleter`.
        else:
            word = document.get_word_before_cursor()
            for command in [
                "start",
                "stop",
                "exit",
                "history",
                "backtest",
                "deploy",
                "help",
            ]:
                if command.startswith(word):
                    if color:
                        yield Completion(
                            command,
                            start_position=-len(word),
                            style="class:green,bgbox",
                        )
                    else:
                        yield Completion(
                            command,
                            start_position=-len(word),
                        )


class CliLexer(Lexer):
    def lex_document(self, document):
        def get_line(lineno):
            line = []
            history_files = Path(__file__).parents[1] / "data" / "history"
            history_files = [his_file.name for his_file in history_files.iterdir()]
            for token in document.lines[lineno].split(" "):
                if token in [
                    "start",
                    "stop",
                    "exit",
                    "history",
                    "backtest",
                    "deploy",
                    "help",
                ]:
                    line.append(("class:green", token))
                elif re.match(datetime_pattern, token):
                    line.append(("class:yellow", token))
                elif token in allowed_grans:
                    line.append(("class:yellow", token))
                elif token in history_files:
                    line.append(("class:yellow", token))
                elif re.match("-[a-zA-Z]", token):
                    line.append(("class:blue", token))
                else:
                    line.append(("", token))
                line.append(("", " "))
            return line

        return get_line


class CLI:
    def __init__(self):
        self.parser = argparse.ArgumentParser(prog="peoples_advisor_usage")
        subparsers = self.parser.add_subparsers(dest="command")
        subparsers.add_parser("start", usage="start_usage")
        subparsers.add_parser("stop", usage="stop_usage")
        subparsers.add_parser("exit", usage="exit_usage")
        history = subparsers.add_parser("history", usage="history_usage")
        history.add_argument("from_time", type=self.cli_datetime)
        history.add_argument("to_time", type=self.cli_datetime)
        history.add_argument(
            "-g",
            dest="granularity",
            action="store",
            default="M5",
            type=self.cli_granularity,
        )
        history.add_argument("-a", dest="alias", action="store", type=self.cli_filename)
        backtesting = subparsers.add_parser("backtest", usage="backtest_usage")
        backtesting.add_argument("data_file", type=self.backtest_filename)
        subparsers.add_parser("help", add_help=False)

        self.session = PromptSession()
        self.exit_flag = False

        control = Control(live_strategies[0], live_strategies[1])
        self.control_thread = Thread(target=control.run, daemon=True)
        self.run_flag = control.run_flag
        self.events = control.events

    @staticmethod
    def cli_datetime(datetime_string):
        datetime_match = re.match(datetime_pattern, datetime_string)
        if not datetime_match:
            raise argparse.ArgumentTypeError(
                f"{datetime_string} is not a valid datetime string"
            )
        else:
            init_list = [int(x) for x in datetime_string[1:-1].split(",")]
            while len(init_list) < 6:
                init_list.append(0)
            return datetime(
                init_list[0],
                init_list[1],
                init_list[2],
                init_list[3],
                init_list[4],
                init_list[5],
            )

    @staticmethod
    def cli_granularity(gran_string):
        if gran_string not in allowed_grans:
            raise argparse.ArgumentTypeError(
                f"{gran_string} is not a valid granularity string"
            )
        else:
            return gran_string

    @staticmethod
    def cli_filename(filename_string):
        filename_match = re.match(r"[a-zA-Z-_\[\].]+", filename_string)
        if not filename_match:
            raise argparse.ArgumentTypeError(
                f"{filename_string} is not a valid filename string"
            )
        else:
            return filename_string

    @staticmethod
    def backtest_filename(filename_string):
        data_path = Path(__file__).parents[1] / "data" / "history" / filename_string
        if not data_path.exists():
            raise argparse.ArgumentTypeError(
                f"{filename_string} is not a valid file in data/history/"
            )
        else:
            return data_path

    @staticmethod
    def peoples_advisor_usage():
        if color:
            color_start_usage = FormattedText(
                [
                    ("", "\n    "),
                    ("class:cyan", "Usage"),
                    ("", ": "),
                    ("class:gray", "pa> "),
                    ("", "{"),
                    ("class:green", "start"),
                    ("", ", "),
                    ("class:green", "stop"),
                    ("", ", "),
                    ("class:green", "exit"),
                    ("", ", "),
                    ("class:green", "history"),
                    ("", ", "),
                    ("class:green", "backtest"),
                    ("", ", "),
                    ("class:green", "deploy"),
                    ("", ", "),
                    ("class:green", "help"),
                    ("", "} ..."),
                    (
                        "",
                        "\n      These commands allow you directly control People's Advisor",
                    ),
                    ("", "\n\n    Available Commands:"),
                    ("class:green", "\n      start"),
                    (
                        "",
                        "\tStart People's Advisor using the settings provided in settings.py",
                    ),
                    ("class:green", "\n      stop"),
                    ("", "\tStop People's Advisor"),
                    ("class:green", "\n      exit"),
                    ("", "\tExit People's Advisor"),
                    ("class:green", "\n      history"),
                    ("", "\tGather historical data for backtesting"),
                    ("class:green", "\n      backtest"),
                    ("", "\tBacktest the algorithms provided in settings.py"),
                    ("class:green", "\n      deploy"),
                    (
                        "",
                        "\tDeploy the algorithms provided in settings.py on a paper or live account",
                    ),
                    ("class:green", "\n      help"),
                    ("", "\tDisplay this help message\n"),
                ]
            )
            print(color_start_usage, style=style, color_depth=TRUE_COLOR)
        else:
            peoples_usage = "\n    Usage: pa> {start, stop, exit, history, backtest, deploy, help} ..."
            peoples_usage += (
                "\n      These commands allow you directly control People's Advisor"
            )
            peoples_usage += "\n\n    Available Commands:"
            peoples_usage += "\n      start\tStart People's Advisor using the settings provided in settings.py"
            peoples_usage += "\n      stop\tStop People's Advisor"
            peoples_usage += "\n      exit\tExit People's Advisor"
            peoples_usage += "\n      history\tGather historical data for backtesting"
            peoples_usage += (
                "\n      backtest\tBacktest the algorithms provided in settings.py"
            )
            peoples_usage += "\n      deploy\tDeploy the algorithms provided in settings.py on a paper or live account"
            peoples_usage += "\n      help\tDisplay this help message\n"
            print(peoples_usage)

    @staticmethod
    def start_usage():
        if color:
            color_start_usage = FormattedText(
                [
                    ("", "\n    "),
                    ("class:cyan", "Usage"),
                    ("", ": "),
                    ("class:green", "start"),
                    ("", " ["),
                    ("class:blue", "-h"),
                    ("", "]"),
                    (
                        "",
                        "\n      Start People's Advisor using the settings provided in settings.py",
                    ),
                    ("", "\n\n    Optional Arguments:"),
                    ("", "\n      "),
                    ("class:blue", "-h"),
                    ("", ", "),
                    ("class:blue", "--help"),
                    ("", "  Display this help message\n"),
                ]
            )
            print(color_start_usage, style=style, color_depth=TRUE_COLOR)
        else:
            start_usage = "\n    Usage: start [-h]"
            start_usage += "\n      Start People's Advisor using the settings provided in settings.py"
            start_usage += "\n\n    Optional Arguments:"
            start_usage += "\n      -h, --help  Display this help message\n"
            print(start_usage)

    @staticmethod
    def stop_usage():
        if color:
            color_stop_usage = FormattedText(
                [
                    ("", "\n    "),
                    ("class:cyan", "Usage"),
                    ("", ": "),
                    ("class:green", "stop"),
                    ("", " ["),
                    ("class:blue", "-h"),
                    ("", "]"),
                    ("", "\n      Stop People's Advisor"),
                    (
                        "",
                        "\n      Note: This will attempt a gentle stop of People's Advisor and may take some time",
                    ),
                    ("", "\n\n    Optional Arguments:"),
                    ("", "\n      "),
                    ("class:blue", "-h"),
                    ("", ", "),
                    ("class:blue", "--help"),
                    ("", "  Display this help message\n"),
                ]
            )
            print(color_stop_usage, style=style, color_depth=TRUE_COLOR)
        else:
            stop_usage = "\n    Usage: stop [-h]"
            stop_usage += "\n      Stop People's Advisor"
            stop_usage += "\n      Note: This will attempt a gentle stop People's Advisor and may take some time"
            stop_usage += "\n\n    Optional Arguments:"
            stop_usage += "\n      -h, --help  Display this help message\n"
            print(stop_usage)

    @staticmethod
    def exit_usage():
        if color:
            color_exit_usage = FormattedText(
                [
                    ("", "\n    "),
                    ("class:cyan", "Usage"),
                    ("", ": "),
                    ("class:green", "exit"),
                    ("", " ["),
                    ("class:blue", "-h"),
                    ("", "]"),
                    ("", "\n      Exit People's Advisor"),
                    (
                        "",
                        "\n      Note: If People's Advisor is currently running, this will perform a hard stop",
                    ),
                    ("", "\n\n    Optional Arguments:"),
                    ("", "\n      "),
                    ("class:blue", "-h"),
                    ("", ", "),
                    ("class:blue", "--help"),
                    ("", "  Display this help message\n"),
                ]
            )
            print(color_exit_usage, style=style, color_depth=TRUE_COLOR)
        else:
            exit_usage = "\n    Usage: exit [-h]"
            exit_usage += "\n      Exit People's Advisor"
            exit_usage += "\n      Note: If People's Advisor is currently running, this will perform a hard stop"
            exit_usage += "\n\n    Optional Arguments:"
            exit_usage += "\n      -h, --help  Display this help message\n"
            print(exit_usage)

    @staticmethod
    def history_usage():
        if color:
            color_history_usage = FormattedText(
                [
                    ("", "\n    "),
                    ("class:cyan", "Usage"),
                    ("", ": "),
                    ("class:green", "history"),
                    ("class:yellow", " FROM TO "),
                    ("", "["),
                    ("class:blue", "-g "),
                    ("class:yellow", "GRANULARITY"),
                    ("", ", "),
                    ("class:blue", "-h"),
                    ("", "]"),
                    (
                        "",
                        "\n      Gather historical data for backtesting given a time range",
                    ),
                    ("", "\n\n    Required Arguments:"),
                    ("", "\n      "),
                    ("class:yellow", "FROM"),
                    (
                        "",
                        "   The start of the time range to gather historical data for",
                    ),
                    ("", "\n         Given as "),
                    ("class:yellow", "(YYYY,MM,DD[,HH,MM,SS])"),
                    ("", " ex. "),
                    ("class:yellow", "(2021,1,1)"),
                    ("", "\n      "),
                    ("class:yellow", "TO"),
                    (
                        "",
                        "     The end of the time range to gather historical data for",
                    ),
                    ("", "\n         Given as "),
                    ("class:yellow", "(YYYY,MM,DD[,HH,MM,SS])"),
                    ("", " ex. "),
                    ("class:yellow", "(2021,2,1,20,30)"),
                    ("", "\n\n    Optional Arguments:"),
                    ("", "\n      "),
                    ("class:blue", "-g"),
                    ("class:yellow", " GRANULARITY "),
                    ("", "Specify a granularity to use when gathering historical data"),
                    (
                        "",
                        "\n             [S5, S10, S15, S30, M1, M2, M4, M5, M10, M15, M30, H1, H2, H3, H4]",
                    ),
                    ("", "\n      "),
                    ("class:blue", "-a"),
                    ("class:yellow", " FILENAME    "),
                    (
                        "",
                        "Specify an alternative filename to save the historical data under",
                    ),
                    ("", "\n      "),
                    ("class:blue", "-h"),
                    ("", ", "),
                    ("class:blue", "--help"),
                    ("", "  Display this help message\n"),
                ]
            )
            print(color_history_usage, style=style, color_depth=TRUE_COLOR)
        else:
            history_usage = "\n    Usage: history FROM TO [-g GRANULARITY, -h]"
            history_usage += (
                "\n      Gather historical data for backtesting given a time range"
            )
            history_usage += "\n\n    Required Arguments:"
            history_usage += "\n      FROM   The start of the time range to gather historical data for"
            history_usage += "\n        Given as (YYYY,MM,DD[,HH,MM,SS]) ex. (2021,1,1)"
            history_usage += (
                "\n      TO     The end of the time range to gather historical data for"
            )
            history_usage += (
                "\n        Given as (YYYY,MM,DD[,HH,MM,SS]) ex. (2021,2,1,20,30)"
            )
            history_usage += "\n\n    Optional Arguments:"
            history_usage += "\n      -g GRANULARITY Specify a granularity to use when gathering historical data"
            history_usage += "\n      -a FILENAME    Specify an alternative filename to save the historical data under"
            history_usage += "\n             [S5, S10, S15, S30, M1, M2, M4, M5, M10, M15, M30, H1, H2, H3, H4]"
            history_usage += "\n      -h, --help  Display this help message\n"
            print(history_usage)

    @staticmethod
    def backtest_usage():
        if color:
            color_backtest_usage = FormattedText(
                [
                    ("", "\n    "),
                    ("class:cyan", "Usage"),
                    ("", ": "),
                    ("class:green", "backtest"),
                    ("class:yellow", " HISTORY_FILE"),
                    ("", " ["),
                    ("class:blue", "-h"),
                    ("", "]"),
                    (
                        "",
                        "\n      Backtest all algorithm pairs provided in settings.py",
                    ),
                    ("", "\n\n    Required Arguments:"),
                    ("", "\n      "),
                    ("class:yellow", "HISTORY_FILE"),
                    (
                        "",
                        "   The historical data file to backtest your algorithms against",
                    ),
                    ("", "\n         ex. "),
                    (
                        "class:yellow",
                        "2021.04.01-2021.05.01[EUR_USD-GBP_USD-EUR_JPY].txt",
                    ),
                    ("", "\n\n    Optional Arguments:"),
                    ("", "\n      "),
                    ("class:blue", "-h"),
                    ("", ", "),
                    ("class:blue", "--help"),
                    ("", "  Display this help message\n"),
                ]
            )
            print(color_backtest_usage, style=style, color_depth=TRUE_COLOR)
        else:
            backtest_usage = "\n    Usage: backtest [-h]"
            backtest_usage += (
                "\n      Backtest all algorithm pairs provided in settings.py"
            )
            backtest_usage += "\n\n    Required Arguments:"
            backtest_usage += "\n      HISTORY_FILE   The historical data file to backtest your algorithms against"
            backtest_usage += (
                "\n        ex. 2021.04.01-2021.05.01[EUR_USD-GBP_USD-EUR_JPY].txt"
            )
            backtest_usage += "\n\n    Optional Arguments:"
            backtest_usage += "\n      -h, --help  Display this help message\n"
            print(backtest_usage)

    @staticmethod
    def error(error_message):
        replace_snippets = [
            ("from_time", "FROM"),
            ("to_time", "TO"),
            ("cli_datetime", "datetime"),
            ("cli_granularity", "granularity"),
        ]
        for rep in replace_snippets:
            error_message = error_message.replace(rep[0], rep[1])
        if color:
            if error_message.startswith("unrecognized arguments:"):
                color_error_message = FormattedText(
                    [
                        ("class:orange", "    Error"),
                        ("", ": " + error_message + "\n"),
                    ]
                )
            elif error_message.startswith("argument command: invalid choice: "):
                error_message = error_message.replace(
                    "argument command: invalid choice: ", "invalid command: "
                )
                color_error_message = FormattedText(
                    [
                        ("class:orange", "    Error"),
                        ("", ": " + error_message[: error_message.index("(")]),
                        ("", "(choose from '"),
                        ("class:green", "start"),
                        ("", "', '"),
                        ("class:green", "stop"),
                        ("", "', '"),
                        ("class:green", "exit"),
                        ("", "', '"),
                        ("class:green", "history"),
                        ("", "', '"),
                        ("class:green", "backtest"),
                        ("", "', '"),
                        ("class:green", "deploy"),
                        ("", "', '"),
                        ("class:green", "help"),
                        ("", "')\n"),
                    ]
                )
            elif error_message.startswith("the following arguments are required: "):
                req_args = error_message.replace(
                    "the following arguments are required: ", ""
                ).split(", ")
                format_args = []
                for arg in req_args:
                    format_args.append(("class:yellow", arg))
                    if arg != req_args[-1]:
                        format_args.append(("", ", "))
                color_error_message = [
                    ("class:orange", "    Error"),
                    ("", ": the following arguments are required: "),
                ]
                color_error_message.extend(format_args)
                color_error_message.append(("", "\n"))
                color_error_message = FormattedText(color_error_message)
            elif error_message.startswith("argument -"):
                error_message = error_message.replace("argument ", "").split(":")
                color_error_message = FormattedText(
                    [
                        ("class:orange", "    Error"),
                        ("", ": argument "),
                        ("class:blue", error_message[0]),
                        ("", ":" + ":".join(error_message[1:])),
                        ("", "\n"),
                    ]
                )
            elif error_message.startswith("argument "):
                error_message = error_message.replace("argument ", "").split(":")
                color_error_message = FormattedText(
                    [
                        ("class:orange", "    Error"),
                        ("", ": argument "),
                        ("class:yellow", error_message[0]),
                        ("", ":" + ":".join(error_message[1:])),
                        ("", "\n"),
                    ]
                )
            else:
                color_error_message = FormattedText(
                    [
                        ("class:orange", "    Error"),
                        ("", ": " + error_message + "\n"),
                    ]
                )
            print(color_error_message, style=style, color_depth=TRUE_COLOR)
        else:
            if error_message.startswith("unrecognized arguments:"):
                error_message = "    Error: " + error_message + "\n"
            elif error_message.startswith("argument command: invalid choice: "):
                error_message = error_message.replace(
                    "argument command: invalid choice: ", "invalid command: "
                )
                error_message = "    Error: " + error_message + "\n"
            elif error_message.startswith("the following arguments are required: "):
                error_message = "    Error: " + error_message + "\n"
            elif error_message.startswith("argument "):
                error_message = "    Error: " + error_message + "\n"
            else:
                error_message = "    Error: " + error_message + "\n"
            print(error_message)

    def start(self):
        if self.run_flag.is_set():
            if color:
                start_message = FormattedText(
                    [
                        ("class:cyan", "Info"),
                        ("", ": People's Advisor is already running"),
                    ]
                )
                print(start_message, style=style, color_depth=TRUE_COLOR)
            else:
                print("Info: People's Advisor is already running")
        else:
            if color:
                start_message = FormattedText(
                    [
                        ("class:cyan", "Info"),
                        ("", ": Starting People's Advisor"),
                    ]
                )
                print(start_message, style=style, color_depth=TRUE_COLOR)
            else:
                print("Info: Starting People's Advisor")
            self.events.put(StartEvent())

    def stop(self):
        if self.run_flag.is_set():
            if color:
                stop_message = FormattedText(
                    [
                        ("class:cyan", "Info"),
                        ("", ": Stopping People's Advisor"),
                    ]
                )
                print(stop_message, style=style, color_depth=TRUE_COLOR)
            else:
                print("Info: Stopping People's Advisor")
            self.events.put(StopEvent())
        else:
            if color:
                stop_message = FormattedText(
                    [
                        ("class:cyan", "Info"),
                        ("", ": People's Advisor is already stopped"),
                    ]
                )
                print(stop_message, style=style, color_depth=TRUE_COLOR)
            else:
                print("Info: People's Advisor is already stopped")

    def exit(self):
        if self.run_flag.is_set():
            if color:
                exit_message = FormattedText(
                    [
                        ("class:orange", "WARNING"),
                        ("", ": People's Advisor is currently running."),
                        (
                            "",
                            " It is recommended you run the stop command before the exit command.",
                        ),
                    ]
                )
                print(exit_message, style=style, color_depth=TRUE_COLOR)
            else:
                exit_message = "WARNING: People's Advisor is currently running."
                exit_message += " It is recommended you run the stop command before the exit command."
                print(exit_message)
            with patch_stdout():
                prompt = self.session.prompt(
                    "Are you sure you wish to continue and perform a hard stop? (Y/n): "
                )
            if prompt[0] == "Y":
                if color:
                    exit_message = FormattedText(
                        [
                            ("class:cyan", "Info"),
                            ("", ": Hard stopping People's Advisor"),
                        ]
                    )
                    print(exit_message, style=style, color_depth=TRUE_COLOR)
                else:
                    print("Info: Hard stopping People's Advisor")
                self.events.put(ExitEvent())
                self.control_thread.join()
                self.exit_flag = True
            else:
                if color:
                    exit_message = FormattedText(
                        [
                            ("class:cyan", "Info"),
                            ("", ": Aborting hard stop of People's Advisor"),
                        ]
                    )
                    print(exit_message, style=style, color_depth=TRUE_COLOR)
                else:
                    print("Info: Aborting hard stop of People's Advisor")
        else:
            if color:
                exit_message = FormattedText(
                    [
                        ("class:cyan", "Info"),
                        ("", ": Exiting People's Advisor"),
                    ]
                )
                print(exit_message, style=style, color_depth=TRUE_COLOR)
            else:
                print("Info: Exiting People's Advisor")
            self.events.put(ExitEvent())
            self.control_thread.join()
            self.exit_flag = True

    @staticmethod
    def history(from_datetime, to_datetime, granularity, filename=None):
        filename = (
            history_file_name(instruments, from_datetime, to_datetime)
            if not filename
            else filename + ".txt"
        )
        historical_data = get_historical_gen(
            instruments, from_datetime, to_datetime, granularity, filename
        )
        if color:
            color_formatters = [
                formatters.Text("Info", style="class:cyan"),
                formatters.Text(": Gathering: "),
                formatters.Bar(sym_a="=", sym_b="=", sym_c=" ", unknown="="),
                formatters.Text(" "),
                formatters.IterationsPerSecond(),
                formatters.Text(" data-points/second"),
                formatters.Text("  "),
            ]
            with ProgressBar(
                style=style, formatters=color_formatters, color_depth=TRUE_COLOR
            ) as pb:
                for _ in pb(historical_data.gen()):
                    pass
            history_message = FormattedText(
                [
                    ("class:cyan", "Info"),
                    ("", ": Data saved to data/history/"),
                    ("class:cyan", filename),
                ]
            )
            print(history_message, style=style, color_depth=TRUE_COLOR)
        else:
            base_formatters = [
                formatters.Text("Info: Gathering: "),
                formatters.Bar(sym_a="=", sym_b="=", sym_c=" ", unknown="="),
                formatters.Text(" "),
                formatters.IterationsPerSecond(),
                formatters.Text(" data-points/second"),
                formatters.Text("  "),
            ]
            with ProgressBar(formatters=base_formatters) as pb:
                for _ in pb(historical_data.gen()):
                    pass
            print("Info: Data saved to data/history/" + filename)

    @staticmethod
    def backtest(data_path):
        line_count = 0
        if color:
            color_formatters = [
                formatters.Text("Info", style="class:cyan"),
                formatters.Text(": Preparing backtest: "),
                formatters.Bar(sym_a="=", sym_b="=", sym_c=" ", unknown="="),
                formatters.Text(" "),
                formatters.IterationsPerSecond(),
                formatters.Text(" data-points/second"),
                formatters.Text("  "),
            ]
            with ProgressBar(
                style=style, formatters=color_formatters, color_depth=TRUE_COLOR
            ) as pb:
                for _ in pb(file_size(data_path)):
                    line_count += 1
            backtest_message = FormattedText(
                [
                    ("class:cyan", "Info"),
                    ("", ": Done, beginning backtest"),
                ]
            )
            print(backtest_message, style=style, color_depth=TRUE_COLOR)
            color_formatters = [
                formatters.Text("Backtest", style="class:cyan"),
                formatters.Text(": ["),
                formatters.Label(),
                formatters.Text("]: "),
                formatters.Bar(sym_a="=", sym_b="=", sym_c=" ", unknown="="),
                formatters.Text(" "),
                formatters.Progress(),
                formatters.Text(" "),
                formatters.TimeLeft(),
                formatters.Text("  "),
            ]
            for strat_pair in backtest_strategies:
                control = Control(strat_pair[0], strat_pair[1], backtesting=True)
                control_thread = Thread(target=control.run, daemon=True)
                control_thread.start()
                control.events.put(StartEvent())
                label = FormattedText(
                    [
                        ("class:yellow", str(type(strat_pair[0])).split(".")[-1][:-2]),
                        ("", ", "),
                        ("class:yellow", str(type(strat_pair[1])).split(".")[-1][:-2]),
                    ]
                )
                with ProgressBar(
                    formatters=color_formatters, style=style, color_depth=TRUE_COLOR
                ) as pb:
                    historical_gen = get_backtesting_gen(
                        control.events,
                        control.run_flag,
                        data_path,
                    )
                    for _ in pb(historical_gen.gen(), label=label, total=line_count):
                        pass
                control_thread.join()
            backtest_message = FormattedText(
                [
                    ("class:cyan", "Info"),
                    ("", ": Done, finished backtest"),
                ]
            )
            print(backtest_message, style=style, color_depth=TRUE_COLOR)
        else:
            base_formatters = [
                formatters.Text("Info: Preparing backtest: "),
                formatters.Bar(sym_a="=", sym_b="=", sym_c=" ", unknown="="),
                formatters.Text(" "),
                formatters.IterationsPerSecond(),
                formatters.Text(" data-points/second"),
                formatters.Text("  "),
            ]
            with ProgressBar(formatters=base_formatters) as pb:
                for _ in pb(file_size(data_path)):
                    line_count += 1
            print("Info: Done, beginning backtest")
            base_formatters = [
                formatters.Text("Backtest: ["),
                formatters.Label(),
                formatters.Text("]: "),
                formatters.Bar(sym_a="=", sym_b="=", sym_c=" ", unknown="="),
                formatters.Text(" "),
                formatters.IterationsPerSecond(),
                formatters.Text(" data-points/second"),
                formatters.Text(" "),
                formatters.TimeLeft(),
                formatters.Text("  "),
            ]
            for strat_pair in backtest_strategies:
                control = Control(strat_pair[0], strat_pair[1], backtesting=True)
                control_thread = Thread(target=control.run, daemon=True)
                control_thread.start()
                control.events.put(StartEvent())
                label = str(type(strat_pair[0])).split(".")[-1][:-2] + ", "
                label += str(type(strat_pair[1])).split(".")[-1][:-2]
                with ProgressBar(
                    formatters=base_formatters, style=style, color_depth=TRUE_COLOR
                ) as pb:
                    historical_gen = get_backtesting_gen(
                        control.events, control.run_flag, data_path
                    )
                    for _ in pb(historical_gen.gen(), label=label, total=line_count):
                        pass
                control_thread.join()
            print("Info: Done, finished backtest")

    def run(self):
        if color:
            print(
                FormattedText([("class:red", splash_screen)]),
                style=style,
                color_depth=TRUE_COLOR,
            )
        else:
            print(splash_screen)

        self.control_thread.start()

        while not self.exit_flag:
            try:
                with patch_stdout():
                    if color:
                        prompt = self.session.prompt(
                            FormattedText([("class:gray", "pa> ")]),
                            style=style,
                            color_depth=TRUE_COLOR,
                            completer=NestedCLiCompleter(),
                            complete_while_typing=True,
                            lexer=CliLexer(),
                        )
                    else:
                        prompt = self.session.prompt(
                            "pa> ",
                            completer=NestedCLiCompleter(),
                            complete_while_typing=True,
                        )

                argparse_output = io.StringIO()
                try:
                    # Catch all output from argparse to substitute custom usage/error messages
                    with redirect_stdout(argparse_output):
                        with redirect_stderr(argparse_output):
                            args = self.parser.parse_args(prompt.split(" "))
                            if args.command == "history":
                                if args.from_time >= args.to_time:
                                    self.history_usage()
                                    self.error("FROM must be chronologically before TO")
                except SystemExit:
                    argparse_output = argparse_output.getvalue().split("\n")[:-1]
                    for line in argparse_output:
                        if re.match("usage: ([a-z_]+)", line):
                            usage_attr = re.match("usage: ([a-z_]+)", line).group(1)
                            self.__getattribute__(usage_attr)()
                        elif "error: " in line:
                            self.error(line[line.index("error: ") + 7 :])
                        else:
                            pass
                    continue

                if args.command == "start":
                    self.start()
                elif args.command == "stop":
                    self.stop()
                elif args.command == "exit":
                    self.exit()
                elif args.command == "history":
                    self.history(
                        args.from_time, args.to_time, args.granularity, args.alias
                    )
                elif args.command == "backtest":
                    self.backtest(args.data_file)
                elif args.command == "deploy":
                    pass
                elif args.command == "help":
                    self.peoples_advisor_usage()
            except KeyboardInterrupt:
                try:
                    if color:
                        exit_message = FormattedText(
                            [
                                ("class:orange", "WARNING"),
                                (
                                    "",
                                    ": It is recommended you exit People's Advisor with the exit command.",
                                ),
                                (
                                    "",
                                    " If you would like to continue anyways, input [ctrl+c] again. Else, hit enter.",
                                ),
                            ]
                        )
                        print(exit_message, style=style, color_depth=TRUE_COLOR)
                    else:
                        exit_message = "WARNING: It is recommended you exit People's Advisor with the exit command."
                        exit_message += " If you would like to continue anyways, input [ctrl+c] again."
                        exit_message += " Else, hit enter."
                        print(exit_message)
                    input()
                except KeyboardInterrupt:
                    sys.exit(-1)
