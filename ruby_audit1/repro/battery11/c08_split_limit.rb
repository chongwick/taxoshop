s=("ab,"*3000); $s=s
n=Object.new; def n.to_int; $s.clear; 100; end
s.split(",", n) rescue (puts "raised"); puts "c08 ok"
