s = "%s and %d"; args = ["x"*4000, 5]
# format where an arg's to_s mutates a prior captured buffer
puts (format("%s", "y"*10)) rescue (puts "raised")
puts "s18 ok"
