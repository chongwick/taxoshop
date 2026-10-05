a=(1..3000).to_a; a.max(5){|x,y| a.clear; x<=>y} rescue (puts "raised"); puts "n08 ok"
