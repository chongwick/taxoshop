s = "x"*4000
class E; def initialize(s)=@s=s; def to_int; @s.clear; 3000; end; end
(format("%.*s", E.new(s), s)) rescue (puts "raised")
puts "t07 ok"
