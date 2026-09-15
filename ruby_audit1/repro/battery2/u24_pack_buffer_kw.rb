buf = "x" * 4000
evil = Object.new; $buf = buf
def evil.to_int; $buf.clear; 65; end
[evil, 1, 2, 3].pack("N*", buffer: buf) rescue (puts "raised")
puts "u24 ok"
