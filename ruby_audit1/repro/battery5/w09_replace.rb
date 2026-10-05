a=(1..3000).to_a; $a=a
e=Object.new; def e.to_ary; $a.clear; (1..9000).to_a; end
a.replace(e) rescue (puts "raised"); puts "w09 ok"
