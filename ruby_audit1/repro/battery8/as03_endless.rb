a = (1..3000).to_a; $a = a
step = Object.new
def step.to_int; $a.clear; 2; end
p a[(2900..).step(step)] rescue (puts "raised: #{$!.class}")
puts "as03 ok"
