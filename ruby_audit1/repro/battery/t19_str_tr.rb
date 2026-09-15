s = "A"*4000
class E; def initialize(s)=@s=s; def to_str; @s.clear; "B"; end; end
s.tr("A", E.new(s)) rescue (puts "raised")
puts "t19 ok"
