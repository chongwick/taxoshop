a=(1..3000).to_a; $a=a
e=Object.new; def e.coerce(o); $a.clear; [o,1]; end; def e.+(o); 0; end
a[1000]=e
a.sum rescue (puts "raised"); puts "n09 ok"
