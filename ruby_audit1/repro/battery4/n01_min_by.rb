a=(1..3000).to_a; a.min_by{|x| a.clear if x==1; x} rescue (puts "raised"); puts "n01 ok"
