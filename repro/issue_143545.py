import cProfile


class Timer:
    def __call__(self):
        return self

    def __index__(self):
        prof.clear()
        return 0


prof = cProfile.Profile(timer=Timer())


def victim():
    return None


prof._pystart_callback(victim.__code__, 0)
