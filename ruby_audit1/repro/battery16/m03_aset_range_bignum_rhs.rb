a = (1..3000).to_a; $a = a
e = Object.new; def e.to_ary; $a.clear; []; end   # shrink RHS to empty
a[100..2999] = e rescue (puts "raised: #{$!.class}")
puts "m03 ok"
