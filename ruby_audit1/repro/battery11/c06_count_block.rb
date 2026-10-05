a=(1..3000).to_a; a.count{|x| a.clear if x==1; true} rescue (puts "raised"); puts "c06 ok"
