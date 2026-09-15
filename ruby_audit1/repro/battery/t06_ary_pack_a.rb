class E; def initialize(a)=@a=a; def to_str; @a.replace([]); "Z"*10; end; end
a = (1..2000).map{"x"*8}
a << E.new(a)
a.pack("a8"*2001) rescue (puts "raised")
puts "t06 ok"
