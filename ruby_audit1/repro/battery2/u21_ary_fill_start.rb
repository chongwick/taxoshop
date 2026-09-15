a = (1..3000).to_a
evil = Object.new; $a=a
def evil.to_int; $a.clear; 0; end
a.fill(7, evil) rescue (puts "raised")
puts "u21 ok"
