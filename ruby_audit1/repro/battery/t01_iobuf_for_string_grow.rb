str = "A" * 4000
buf = IO::Buffer.for(str)          # aliases str's internal buffer
buf.each_byte { str << ("x"*100000) } rescue (puts "raised")
puts "t01 ok"
