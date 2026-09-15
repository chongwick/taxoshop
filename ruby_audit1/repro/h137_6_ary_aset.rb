# H137-6: Array#[]= splice path captures rptr=RARRAY_CONST_PTR(ary) (array.c:2338/2368)
# then index conversion / self-insert. A to_int that shrinks the array before
# ary_splice copies from rptr leaves rptr dangling. Self-insert (rpl==ary) is the
# fragile case flagged by the `self_insert` branch.

class Evil
  def initialize(a) = @a = a
  def to_int
    @a.replace([])   # shrink/free during index conversion
    0
  end
end

# Variant A: evil index that clears the array, self-insert of the array
begin
  a = (1..100).to_a
  a[Evil.new(a), 2] = a
rescue => e
  puts "A rescued: #{e.class}"
end
puts "A done"

# Variant B: self-insert splice that forces realloc (rpl == ary) with a big array
begin
  a = (1..1000).to_a
  a[0, 1] = a          # self-insert: ary_splice copies from RARRAY_CONST_PTR(rpl)=ary
rescue => e
  puts "B rescued: #{e.class}"
end
puts "B done"

# Variant C: evil length arg clears array after start captured
class EvilLen
  def initialize(a) = @a = a
  def to_int
    @a.clear
    50
  end
end
begin
  a = (1..100).to_a
  a[2, EvilLen.new(a)] = [9, 9, 9]
rescue => e
  puts "C rescued: #{e.class}"
end
puts "C done"

puts "H137-6 completed cleanly"
