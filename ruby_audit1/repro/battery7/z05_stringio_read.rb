require 'stringio'
s = "a"*4000
io = StringIO.new(s)
io.read(10)
s.clear
io.read(3000) rescue (puts "raised")
puts "z05 ok"
