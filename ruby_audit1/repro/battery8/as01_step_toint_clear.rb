a = (1..3000).to_a; $a = a
step = Object.new
def step.to_int; $a.clear; 2; end
seq = (2900..2950).step(step)
p a[seq] rescue (puts "raised: #{$!.class}")
puts "as01 ok"
