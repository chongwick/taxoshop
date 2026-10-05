a = (1..3000).to_a; $a = a
e = Object.new; def e.to_ary; $a.clear; [9,9,9]; end
a[2900..2950] = e rescue (puts "raised: #{$!.class}")
puts "m01 ok"
