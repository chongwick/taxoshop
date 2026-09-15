a = (1..3000).to_a
evil = Object.new; $a=a
def evil.to_ary; $a.clear; [1,2,3]; end
a.concat(evil) rescue (puts "raised")
puts "u11 ok"
