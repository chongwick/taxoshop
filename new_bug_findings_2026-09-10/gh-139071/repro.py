import _asyncio


class Dummy:
    def __hash__(self):
        return 0


class CorruptTrigger:
    def __hash__(self):
        return 0

    def __eq__(self, other):
        try:
            _asyncio._register_task(self)
        except BaseException:
            pass
        return False


# Leave dummy entries in the internal task set.
initial = [Dummy(), Dummy()]
_asyncio._register_task(initial[0])
_asyncio._register_task(initial[1])
del initial

# Colliding equality callbacks recursively re-enter insertion of that set.
triggers = [CorruptTrigger(), CorruptTrigger()]
_asyncio._register_task(triggers[0])
_asyncio._register_task(triggers[1])

print("completed")
