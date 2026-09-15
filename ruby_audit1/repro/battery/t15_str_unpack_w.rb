s = ([300]*4000).pack("w*")
s.unpack("w*") { s.clear } rescue (puts "raised")
puts "t15 ok"
