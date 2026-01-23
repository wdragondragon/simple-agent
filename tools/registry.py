from tools.calculator import calculator
from tools.filesystem import (
    read_file,
    write_file_safe,
    list_folder,
    tail_file
)
from tools.command import run_command


def finish(answer: str):
    return f"FINAL ANSWER: {answer}"


TOOLS = {
    "calculator": calculator,
    "read_file": read_file,
    "write_file_safe": write_file_safe,
    "list_folder": list_folder,
    "tail_file": tail_file,
    "run_command": run_command,
    "finish": finish,
}
