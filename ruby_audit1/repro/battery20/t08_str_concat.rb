# String#concat(a, b): first arg to_str mutates receiver before second appended
s = "base".dup
$s = s
e1 = Object.new
def e1.to_str; $s.replace("q"*(8*1024*1024)); "A"; end
s.concat(e1, "tail")
puts "t08 ok"
