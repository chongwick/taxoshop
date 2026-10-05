require 'pathname'
p = Pathname.new("a/"*2000)
p.each_filename { }
puts "z09 ok"
