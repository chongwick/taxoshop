b = (1..3000).to_a; $a=b
e=Object.new; def e.hash; $a.clear if $a && !$d; $d=true; 1; end; def e.eql?(o); false; end
b2=b.dup; b2 << e; b2 << e
b2.uniq rescue (puts "raised"); puts "k08 ok"
