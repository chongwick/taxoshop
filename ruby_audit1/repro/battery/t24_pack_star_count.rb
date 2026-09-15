class E; def initialize(a)=@a=a; def to_int; @a.replace([]); 100; end; end
a = (1..2000).to_a
[a.size, *a].pack("N*") rescue (puts "raised")
puts "t24 ok"
