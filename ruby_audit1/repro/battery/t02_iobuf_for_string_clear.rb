str = "A" * 4000
IO::Buffer.for(str) do |buf|
  buf.each_byte { str.clear }
end rescue (puts "raised")
puts "t02 ok"
