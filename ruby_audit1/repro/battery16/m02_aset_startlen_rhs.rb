a = (1..3000).to_a; $a = a
e = Object.new; def e.to_ary; $a.clear; (1..5000).to_a; end
a[2900, 50] = e rescue (puts "raised: #{$!.class}")
puts "m02 ok"
