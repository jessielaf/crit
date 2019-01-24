from typing import List
from dataclasses import dataclass


@dataclass
class Result:
    stdin: str
    stdout: List[str]
    success: bool
