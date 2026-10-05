# String#squeeze: arg to_str mutates the receiver string
s = ("aabbccddee" * 2000).dup
$s = s
evil = Object.new
def evil.to_str; $s.replace("q"*(8*1024*1024)); "a-e"; end
s.squeeze(evil)
puts "t05 ok"
