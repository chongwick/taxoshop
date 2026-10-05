o = Object.new
def o.to_int; 5000; end
(1..o).to_a rescue (puts "raised")
puts "r01 ok"
