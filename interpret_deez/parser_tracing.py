from dataclasses import dataclass


@dataclass
class TraceDeez:
    trace_level: int = 0
    place_holder: str = "\t"

    def ident_level(self) -> str:
        return self.place_holder * (self.trace_level - 1)

    def printer(self, message: str):
        print(f"{self.ident_level()}{message}")

    def increase_ident(self):
        self.trace_level = self.trace_level + 1

    def decrease_ident(self):
        self.trace_level = self.trace_level - 1

    def begin_trace(self, message: str) -> str:
        self.increase_ident()
        self.printer(f"BEGIN {message}")
        return message

    def end_trace(self, message: str):
        self.printer(f"END {message}")
        self.decrease_ident()
