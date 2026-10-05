# Array#pack with buffer: keyword; element to_str shrinks the buffer string
a = ["x"*100] * 2000
buf = "P" * 10
$buf = buf
evil = Object.new
def evil.to_str; $buf.replace("z"*(8*1024*1024)); "Z"*100; end
a[1] = evil
a.pack("a100"*2000, buffer: buf)
puts "t12 ok"
