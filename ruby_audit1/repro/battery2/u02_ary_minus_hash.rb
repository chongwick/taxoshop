big = (1..3000).to_a
evil = Object.new; $big=big
def evil.hash; $big.clear; 7; end
def evil.eql?(o); false; end
other = [evil] + (1..100).to_a
(big - other) rescue (puts "raised")
puts "u02 ok"
