a=(1..3000).to_a; $a=a
e=Object.new; def e.to_int; $a.replace([]); 5; end
a[1000]=e
a.pack("Q*") rescue (puts "raised"); puts "p03 ok"
