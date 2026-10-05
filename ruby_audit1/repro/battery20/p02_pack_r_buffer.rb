# same via 'r' (SLEB128)
buf = "Z" * 4096
$buf = buf
evil = Object.new
def evil.to_int
  $buf.replace("q")
  123456789
end
[evil].pack("r", buffer: buf)
puts "p02 ok"
