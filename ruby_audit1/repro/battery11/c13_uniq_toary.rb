a=(1..3000).to_a; $a=a
e=Object.new; def e.hash; $a.clear; 1; end; def e.eql?(o);false;end
a2=a.dup; a2 << e
a2.uniq rescue (puts "raised"); puts "c13 ok"
