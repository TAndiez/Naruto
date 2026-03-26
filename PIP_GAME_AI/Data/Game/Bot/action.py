from enum import Enum
from enum import Enum, auto

class A(Enum):
    STAND = auto()
    DEFEND = auto()
    MOVE_LEFT = auto()
    MOVE_RIGHT = auto()
    RUN_LEFT = auto()
    RUN_RIGHT = auto()
    JUMP = auto()
    HIGH_JUMP = auto()
    ATTACK = auto()
    SKILL_1 = auto()
    SKILL_2 = auto()
    SKILL_3 = auto()
    SKILL_4 = auto()
    SKILL_5 = auto()

ACTION_LIST = [
    [A.STAND],
    [A.DEFEND],
    [A.MOVE_LEFT],
    [A.MOVE_RIGHT],
    [A.RUN_LEFT],
    [A.RUN_RIGHT],
    [A.ATTACK],
    [A.JUMP],
    [A.HIGH_JUMP],
    [A.SKILL_1],
    [A.SKILL_2],
    [A.SKILL_3],
    [A.MOVE_LEFT, A.JUMP],
    [A.MOVE_LEFT, A.ATTACK],
    [A.MOVE_LEFT, A.SKILL_1],
    [A.MOVE_LEFT, A.SKILL_2],
    [A.MOVE_LEFT, A.SKILL_3],
    [A.MOVE_RIGHT, A.JUMP],
    [A.MOVE_RIGHT, A.ATTACK],
    [A.MOVE_RIGHT, A.SKILL_1],
    [A.MOVE_RIGHT, A.SKILL_2],
    [A.MOVE_RIGHT, A.SKILL_3],
    [A.RUN_LEFT, A.JUMP],
    [A.RUN_LEFT, A.ATTACK],
    [A.RUN_LEFT, A.SKILL_1],
    [A.RUN_LEFT, A.SKILL_2],
    [A.RUN_LEFT, A.SKILL_3],
    [A.RUN_RIGHT, A.JUMP],
    [A.RUN_RIGHT, A.ATTACK],
    [A.RUN_RIGHT, A.SKILL_1],
    [A.RUN_RIGHT, A.SKILL_2],
    [A.RUN_RIGHT, A.SKILL_3],
    [A.HIGH_JUMP],
    [A.SKILL_4],
    [A.SKILL_5],
]


