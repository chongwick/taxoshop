# Array#join: element to_str clears the receiver array mid-join
a = ["x"] * 4000
$a = a
evil = Object.new
def evil.to_str; $a.clear; $a.replace([]); GC.start; "E"; end
a[10] = evil
a.join("-")
puts "t02 ok"
