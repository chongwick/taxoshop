# String#count: arg to_str mutates the receiver string
s = ("a".."z").to_a.join * 500
$s = s
evil = Object.new
def evil.to_str; $s.replace("q"*(8*1024*1024)); "a-z"; end
s.count(evil)
puts "t03 ok"
