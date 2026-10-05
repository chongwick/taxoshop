buf="x"*4000; $buf=buf
e=Object.new; def e.to_str; $buf.clear; "Z"*10; end
[e, "aaa"].pack("a5a5", buffer: buf) rescue (puts "raised"); puts "b09 ok"
