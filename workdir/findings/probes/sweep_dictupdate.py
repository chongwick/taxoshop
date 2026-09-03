# dict.update(list_of_pairs) where a key __hash__ mutates the source list
src=[]
class K:
    def __hash__(self):
        src.clear(); src.extend([(i,i) for i in range(3000)])
        return 7
    def __eq__(self,o): return self is o
src.extend([(K(),1),(K(),2),(K(),3)])
d={}
try: d.update(src)
except Exception as e: print("exc", type(e).__name__)
print("OK sweep_dictupdate")
