h={}; (0...6).each{|i| h[i]=i}; $h=h
h.transform_keys! { |k| $h.clear if k==0; k+1000 } rescue (puts "raised")
puts "y02 ok"
