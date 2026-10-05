a=(1..3000).to_a; $a=a
e=Object.new; def e.to_int; $a.replace([]); 65; end
a[1000]=e
a.pack("C*") rescue (puts "raised"); puts "p01 ok"
