a = (1..3000).to_a
evil = Object.new; $a=a
def evil.to_int; $a.clear; 2500; end
a.insert(evil, 9,9,9) rescue (puts "raised")
puts "u19 ok"
