require 'set'
a=Set.new((1..3000).to_a); b=(1..100).to_a; $a=a
e=Object.new; def e.hash; $a.clear; 1; end; def e.eql?(o);false;end
a.subtract([e]+b) rescue (puts "raised"); puts "x02 ok"
