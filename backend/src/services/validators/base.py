from abc import ABC, abstractmethod


class ValidatorABC(ABC):
    @abstractmethod
    def validate(self, value):
        raise NotImplementedError
