a = (1..3000).to_a
evil = Object.new; $a=a
def evil.to_int; $a.clear; 2900; end
a.values_at(evil, 0, 1) rescue (puts "raised")
puts "u20 ok"
