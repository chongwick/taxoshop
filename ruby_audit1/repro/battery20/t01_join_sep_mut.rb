# Array#join: element to_str mutates the separator string mid-join
a = ["x"] * 2000
sep = "," * 100
evil = Object.new
def evil.to_str; $sep.replace("z"*(8*1024*1024)); "E"; end
$sep = sep
a[1000] = evil
a.join(sep)
puts "t01 ok"
