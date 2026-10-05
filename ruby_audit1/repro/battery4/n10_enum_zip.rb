class C; include Enumerable; def each; @a||=(1..3000).to_a; @a.each{|x|yield x}; end; def a; @a; end; end
c=C.new; c.each{break}; $c=c
e=Object.new; def e.to_ary; $c.a.clear; [1]; end
c.zip(e) rescue (puts "raised"); puts "n10 ok"
