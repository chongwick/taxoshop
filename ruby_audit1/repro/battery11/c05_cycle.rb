a=(1..3000).to_a; n=0; a.cycle{|x| n+=1; a.clear if n==1; break if n>5000} rescue (puts "raised"); puts "c05 ok"
