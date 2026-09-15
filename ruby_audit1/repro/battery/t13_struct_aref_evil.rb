S = Struct.new(:a,:b,:c)
s = S.new(1,2,3)
class E; def to_int; 0; end; end
s[E.new] rescue (puts "raised")
puts "t13 ok"
