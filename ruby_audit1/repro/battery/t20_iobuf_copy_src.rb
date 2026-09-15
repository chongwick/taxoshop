dst = IO::Buffer.new(4000)
src = IO::Buffer.for("B"*4000)
dst.copy(src) rescue (puts "raised")
puts "t20 ok"
