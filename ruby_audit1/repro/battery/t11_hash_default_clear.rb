h = Hash.new { |hh,k| hh.clear; 0 }
100.times{|i| h[i]=i}
h[:missing] rescue (puts "raised")
puts "t11 ok"
