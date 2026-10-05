a=(1..3000).to_a; a.flat_map{|x| a.clear if x==1; [x,x]} rescue (puts "raised"); puts "n04 ok"
