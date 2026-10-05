# Array#pack: element to_str mutates a sibling / the array
a = ["x"*100] * 3000
$a = a
evil = Object.new
def evil.to_str; $a.clear; $a.replace([]); GC.start; "Z"*100; end
a[1] = evil
a.pack("a100"*3000)
puts "t07 ok"
