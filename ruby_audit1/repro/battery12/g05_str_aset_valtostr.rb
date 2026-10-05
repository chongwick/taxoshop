$s = "a"*4000
val = Object.new; def val.to_str; $s.clear; "z"*10; end
$s[100, 50] = val rescue (puts "raised")
puts "g05 ok"
