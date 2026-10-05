e=Object.new; def e.to_ary; (1..5000).to_a; end
Array(e) rescue (puts "raised"); puts "k01 ok"
