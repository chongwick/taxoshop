a=(1..3000).to_a; a.each_with_object([]){|x,m| a.clear if x==1} rescue (puts "raised"); puts "n06 ok"
