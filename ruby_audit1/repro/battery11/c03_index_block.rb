a=(1..3000).to_a; a.index{|x| a.clear if x==1; false} rescue (puts "raised"); puts "c03 ok"
