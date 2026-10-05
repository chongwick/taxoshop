a=(1..3000).to_a; a.chunk_while{|x,y| a.clear; true}.to_a rescue (puts "raised"); puts "n05 ok"
