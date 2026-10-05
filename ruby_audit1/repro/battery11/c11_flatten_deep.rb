inner=(1..2000).to_a; $inner=inner
e=Object.new; def e.to_ary; $inner.clear; [1,2]; end
inner << e
outer=[inner]
outer.flatten rescue (puts "raised"); puts "c11 ok"
