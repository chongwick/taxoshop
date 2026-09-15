class E; def initialize(a)=@a=a; def to_str; @a.clear; "-"; end; end
a = (1..2000).to_a
a.join(E.new(a)) rescue (puts "raised")
puts "t04 ok"
