# String#delete!: arg to_str mutates the receiver string
s = (("a".."z").to_a.join) * 500
$s = s
evil = Object.new
def evil.to_str; $s.replace("q"*(8*1024*1024)); "a-y"; end
s.delete(evil)
puts "t04 ok"
