from abc import ABC, abstractmethod


class Solver(ABC):
    @abstractmethod
    def create_int_var(self, name: str): ...
