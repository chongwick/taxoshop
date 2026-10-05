import abc
class Meta(abc.ABC):
    pass
class Evil:
    def __subclasshook__(cls, C):
        return NotImplemented
# register many virtual subclasses, then mutate during check
subs = []
for i in range(50):
    c = type(f"S{i}", (), {})
    Meta.register(c)
    subs.append(c)
class Q:
    @property
    def __class__(self):
        # mutate registry during isinstance check
        Meta.register(type(f"X{len(subs)}", (), {}))
        return object
print(isinstance(Q(), Meta))
print("done")
