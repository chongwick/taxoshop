a=(1..3000).to_a; a.sort_by{|x| a.clear if x==1; x} rescue (puts "raised"); puts "n03 ok"
