import builtins
import sys
import baby


def compute_target_length():
    return baby.G0G0SQU1D(
        baby.gOg0sQuId(
            baby.g0GOsquiD(baby.G0g0sQu1D_116510(12775, 3349), baby.G0g0sQu1D_116510(15888, 6848)),
            baby.g0GOsquiD(baby.G0g0sQu1D_116510(13850, 8363), baby.G0g0sQu1D_116510(5053, 3980))
        ),
        baby.gOg0sQuId(
            baby.g0GOsquiD(baby.G0g0sQu1D_116510(1034, 5173), baby.G0g0sQu1D_116510(12571, 8408)),
            baby.g0GOsquiD(baby.G0g0sQu1D_116510(2118, 5430), baby.G0g0sQu1D_116510(1969, 2517))
        )
    )


class TracerStr(str):
    def __new__(cls, value, indexes=None):
        obj = super().__new__(cls, value)
        obj.indexes = list(indexes) if indexes is not None else list(range(len(value)))
        return obj

    def __getitem__(self, item):
        result = super().__getitem__(item)
        if isinstance(item, slice):
            new_indexes = self.indexes[item]
        else:
            idx = item if item >= 0 else len(self) + item
            new_indexes = [self.indexes[idx]]
        return TracerStr(result, new_indexes)

    def __eq__(self, other):
        return True

def extract_constraints():
    target_length = compute_target_length()
    placeholder = 'A'

    def run_attempt(candidate):
        tracer_value = TracerStr(candidate)
        orig_input = builtins.input
        orig_print = builtins.print
        records = []
        active = {}

        def fake_input(prompt=''):
            return tracer_value

        def silent_print(*args, **kwargs):
            return None

        def tracer(frame, event, arg):
            if frame.f_code.co_name != 'g0G0SQuid':
                return tracer
            frame_id = id(frame)
            if event == 'call':
                argument = frame.f_locals.get('GOGo')
                data = {
                    'is_user': isinstance(argument, TracerStr),
                    'indexes': list(argument.indexes) if isinstance(argument, TracerStr) else None,
                    'const': argument if not isinstance(argument, TracerStr) else None,
                    'key': frame.f_locals.get('sQuID'),
                }
                active[frame_id] = data
            elif event == 'return':
                record = active.pop(frame_id, None)
                if record is not None:
                    record['result'] = arg
                    records.append(record)
            return tracer

        try:
            builtins.input = fake_input
            builtins.print = silent_print
            sys.settrace(tracer)
            try:
                baby.gog0sQu1D()
            except Exception:
                pass
        finally:
            sys.settrace(None)
            builtins.input = orig_input
            builtins.print = orig_print

        return records

    candidate = placeholder * target_length
    comparisons = run_attempt(candidate)
    guess = ['?'] * target_length
    used_constants = set()
    for idx, entry in enumerate(comparisons):
        if not entry.get('is_user'):
            continue
        indexes = entry['indexes'] or []
        if not indexes:
            continue
        pair = None
        for j in range(idx + 1, len(comparisons)):
            candidate_const = comparisons[j]
            if candidate_const.get('is_user') or candidate_const.get('key') != entry.get('key') or j in used_constants:
                continue
            pair = candidate_const
            used_constants.add(j)
            break
        if pair is None:
            continue
        expected = pair.get('const')
        if not isinstance(expected, str) or len(expected) != len(indexes):
            continue
        for pos, ch in zip(indexes, expected):
            if 0 <= pos < target_length:
                guess[pos] = ch

    return ''.join(guess)


def main():
    flag = extract_constraints()
    print(flag)


if __name__ == '__main__':
    main()
