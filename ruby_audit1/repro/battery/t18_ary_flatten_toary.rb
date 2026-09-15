a = (1..2000).to_a
bad = Object.new; def bad.to_ary; $a.clear; [1,2,3]; end
$a = a; a << bad
a.flatten rescue (puts "raised")
puts "t18 ok"
