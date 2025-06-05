from abc import ABC, abstractmethod

class Entity(ABC):
    _name : str
    _prompt : str

    def to_dict(self):
        pass