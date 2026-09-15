big = (1..3000).to_a
evil = Object.new; $big=big
def evil.hash; $big.clear; 7; end
def evil.eql?(o); false; end
a = big.dup; a << evil
(a & [1,2,3,evil]) rescue (puts "raised")
puts "u03 ok"
