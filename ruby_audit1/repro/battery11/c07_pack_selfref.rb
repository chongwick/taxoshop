a=(1..2000).map{"x"*8}; $a=a
e=Object.new; def e.to_str; $a.replace([]); "Z"*4000; end
a[100]=e
a.pack("a*"*2000) rescue (puts "raised"); puts "c07 ok"
