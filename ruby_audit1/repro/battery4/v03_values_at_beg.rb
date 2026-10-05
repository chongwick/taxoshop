# evil as the BEGIN of the range
a = (1..5000).to_a; $a = a
e = Object.new
def e.to_int; STDERR.puts "TO_INT FIRED"; $a.clear; 0; end
r = Range.new(e, 4900)
p a.values_at(r).length rescue (puts "raised: #{$!.class}")
puts "v03 done"
