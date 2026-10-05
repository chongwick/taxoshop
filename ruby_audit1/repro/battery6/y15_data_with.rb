D=Data.define(:a,:b)
d=D.new(1,2)
d.with(a:9,b:8) rescue (puts "raised")
puts "y15 ok"
