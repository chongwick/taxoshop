require 'stringio'
s = ("a"*100 + "\n")*100
io = StringIO.new(s)
s.replace("x"*10)
io.gets rescue (puts "raised")
io.read rescue (puts "raised")
puts "z06 ok"
