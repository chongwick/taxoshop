big = (1..3000).to_a
evil = Object.new; $big=big
def evil.hash; $big.clear; 7; end
def evil.eql?(o); false; end
big2 = big.dup; big2 << evil
big2.difference([1,2,3], big) rescue (puts "raised")
puts "u01 ok"
