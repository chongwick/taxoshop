S = Struct.new(*(0...50).map{|i| "m#{i}".to_sym})
s = S.new(*(0...50).to_a)
i = Object.new; def i.to_int; 10; end
s.values_at(i, 0, 1) rescue (puts "raised")
puts "d01 ok"
