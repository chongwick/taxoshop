b = IO::Buffer.new(4000)
b.each_byte { b.resize(8) } rescue (puts "raised")
puts "t03 ok"
