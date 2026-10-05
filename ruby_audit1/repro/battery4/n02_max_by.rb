a=(1..3000).to_a; a.max_by{|x| a.clear if x==1; x} rescue (puts "raised"); puts "n02 ok"
