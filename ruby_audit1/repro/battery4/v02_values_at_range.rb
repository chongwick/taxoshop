a = (1..5000).to_a; $a = a
e = Object.new
def e.to_int; STDERR.puts "TO_INT FIRED"; $a.clear; 4000; end
def e.to_str; "no"; end
r = Range.new(0, e)
p a.values_at(r).length rescue (puts "raised: #{$!.class}")
puts "v02 done"
