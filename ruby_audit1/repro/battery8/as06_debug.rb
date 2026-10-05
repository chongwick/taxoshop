a = (1..3000).to_a; $a = a
step = Object.new
def step.to_int; STDERR.puts "TO_INT fired; clearing (len was #{$a.length})"; $a.clear; 2; end
seq = (2900..2950).step(step)
STDERR.puts "seq built: #{seq.inspect} (len now #{$a.length})"
r = a[seq]
STDERR.puts "result=#{r.inspect} a.len=#{a.length}"
