import secrets
import random
import os

from typing import Callable

FLAG = os.getenv("FLAG") or "flag{this_is_a_test_flag_:D_>.<}"

class InstructionManual:
    STEP_COUNT = 40
    PIECE_SIZE = 256
    PIECE_COUNT = PIECE_SIZE // 8
    BIGGEST_PIECE = 2**PIECE_SIZE - 1

    _steps: list[Callable[[int], int]]
    
    def __init__(self):
        step_types = [self.step_screw_in, self.step_turn_around, self.step_hammer_together]
        prefix = [x() for x in step_types]
        suffix = [x() for x in step_types[::-1]]
        self._operations = prefix + [random.choice(step_types)() for _ in range(self.STEP_COUNT)] + suffix

    def build(self, value: bytes) -> bytes:
        assert len(value) == self.PIECE_COUNT, "These pieces don't seem to be the correct size :("
        wip_furniture = int.from_bytes(value, "big")
        for op in self._operations:
            wip_furniture = op(wip_furniture)

        return wip_furniture.to_bytes(self.PIECE_COUNT, "big")

    @classmethod
    def step_screw_in(cls):
        screw_tight = secrets.randbits(1) == 1
        screw_amount = secrets.randbelow(cls.PIECE_SIZE)
        def _inner(value: int) -> int:
            if screw_tight:
                return ((value >> screw_amount) | (value << (cls.PIECE_SIZE - screw_amount))) & cls.BIGGEST_PIECE
            else:
                return ((value << screw_amount) | (value >> (cls.PIECE_SIZE - screw_amount))) & cls.BIGGEST_PIECE
            
        return _inner

    @classmethod
    def step_turn_around(cls):
        def _inner(value: int) -> int:
            return int.from_bytes(value.to_bytes(cls.PIECE_COUNT, "little"), "big")

        return _inner

    @classmethod
    def step_hammer_together(cls):
        required_hammer = secrets.randbits(cls.PIECE_SIZE)
        def _inner(value: int) -> int:
            return value ^ required_hammer
        
        return _inner

def main():
    assert len(FLAG) == InstructionManual.PIECE_COUNT, "incorrect flag length!!"
    
    instruction_manual = InstructionManual()
    print("Here at FLUX, we always strive to include the latest technological advancements in our products.")
    print("This instruction manual has been generated just for you! But we don't know which pieces are needed to actually construct it...")
    print("Can you help us figure out how it all fits together?")
    print()

    max_count = 300

    print("We've allocated some time for one of our interns to help you with this task.")
    print(f"They will attempt to follow the instruction manual using pieces you provide, for a maximum of {max_count} attempts.")

    remaining = max_count
    while remaining > 0:
        val = input(f"({max_count - remaining}/{max_count}) Please enter your {InstructionManual.PIECE_COUNT} selected pieces as one hex encoded string, or 'finish' to exit early:\n")
        if val == "finish":
            break

        try:
            decoded = bytes.fromhex(val)
            if len(decoded) != InstructionManual.PIECE_COUNT:
                print("incorrect piece count.")
                continue

        except Exception:
            print("incorrect pieces.")
            continue

        assembled_furniture = instruction_manual.build(decoded)
        print("Here is what the intern put together:")
        print(assembled_furniture.hex())

        remaining -= 1

    print("The intern says they've understood what the manual is supposed to construct now, and to relay you this message:")
    print(instruction_manual.build(FLAG.encode()).hex())
    print("Thanks for your help!")

if __name__ == "__main__":
    main()