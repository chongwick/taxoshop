a = Array.new(2000){|i| i}
bad = Object.new; def bad.to_str; $a.clear; "z"; end
$a = a; a << bad
a.join("-") rescue (puts "raised")
puts "t05 ok"
