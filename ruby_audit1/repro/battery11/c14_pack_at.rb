a=(1..3000).to_a; $a=a
e=Object.new; def e.to_int; $a.clear; 5; end
[e].pack("@*") rescue (puts "raised"); puts "c14 ok"
