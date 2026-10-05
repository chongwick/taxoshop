h={}; (0...6).each{|i| h[i]=i}; $h=h   # small => ar_table
h.transform_values! { |v| $h[100+v]=v if v<3; $h.clear if v==5; v } rescue (puts "raised")
puts "y01 ok"
