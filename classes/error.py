from dataclasses import dataclass

@dataclass()
class Error:
    message: str
    status: int = 400