from abc import ABC, abstractmethod

class Effect(ABC):
    def __init__(self, name: str, time: int):
        self.name = name
        self.time = time
    @abstractmethod
    def get(self, enemy):
        pass

class Stun(Effect):
    def __init__(self, name, time):
        super().__init__(name, time)

    def get(self, enemy):
        pass

class KnockedUp(Effect):
    def __init__(self, name, time):
        super().__init__(name, time)

    def get(self, enemy):
        pass

class KnockedBack(Effect):
    def __init__(self, name, time):
        super().__init__(name, time)

    def get(self, enemy):
        pass