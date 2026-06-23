from abc import ABC, abstractmethod


class Solver(ABC):
    @abstractmethod
    def create_int_var(self, name: str, lb: int, ub: int):
        pass

    @abstractmethod
    def create_bool_var(self, name: str):
        pass

    @abstractmethod
    def constraint(self, expression):
        pass

    @abstractmethod
    def solve(self):
        pass

    @abstractmethod
    def get_value(self, var):
        pass
