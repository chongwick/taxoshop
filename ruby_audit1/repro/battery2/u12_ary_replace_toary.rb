a = (1..3000).to_a
evil = Object.new; $a=a
def evil.to_ary; $a.clear; (1..5000).to_a; end
a.replace(evil) rescue (puts "raised")
puts "u12 ok"
