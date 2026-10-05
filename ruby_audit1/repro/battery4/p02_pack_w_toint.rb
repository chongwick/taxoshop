a=(1..3000).to_a; $a=a
e=Object.new; def e.to_int; $a.replace([]); 300; end
a[1000]=e
a.pack("w*") rescue (puts "raised"); puts "p02 ok"
