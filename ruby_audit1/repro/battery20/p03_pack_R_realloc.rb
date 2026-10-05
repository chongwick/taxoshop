# force a realloc-move by growing then shrinking
buf = "A" * 64
$buf = buf
evil = Object.new
def evil.to_int
  $buf.replace("B" * (16*1024*1024))  # realloc-move res; base changes, start stale
  $buf.replace("C" * 8)               # shrink again
  999999999
end
[evil].pack("R", buffer: buf)
puts "p03 ok"
