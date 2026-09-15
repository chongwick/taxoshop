a = (1..3000).to_a
evil = Object.new; $a=a
def evil.hash; $a.clear; 7; end
def evil.eql?(o); false; end
a << evil
a.uniq rescue (puts "raised")
puts "u08 ok"
