seeds = []
seeds << [1,2,3]
seeds << {"a"=>1,"b"=>2}
seeds << "hello"*10
seeds << :sym
seeds << (1..5)
seeds << [[1,2],[3,4]]
seeds << {a: [1,2], b: {c: 3}}
seeds << Struct.new(:x,:y).new(1,2)
seeds << 1.5
seeds << 2**80
seeds << Complex(1,2)
seeds << "utf".encode("UTF-16")
seeds << [nil,true,false]
seeds << Object.new
seeds << /rege/i
begin; seeds << Time.now; rescue; end
begin; seeds << Rational(1,3); rescue; end

count = 0
seeds.each do |obj|
  data = (Marshal.dump(obj) rescue next)
  bytes = data.bytes
  bytes.each_index do |i|
    [0x00, 0xff, 0x7f, 0x03, 0xfc, 0x80, 0x40, bytes[i]^0xff].each do |v|
      b = bytes.dup; b[i] = v
      begin
        Marshal.load(b.pack("C*"))
      rescue Exception
      end
      count += 1
    end
  end
end
puts "FUZZ DONE, #{count} loads, no crash"
