a = (1..3000).to_a; $a = a
step = Object.new
def step.to_int; $a.replace([1,2,3]); 2; end
p a[(2900..2950).step(step)] rescue (puts "raised: #{$!.class}")
puts "as04 ok"
