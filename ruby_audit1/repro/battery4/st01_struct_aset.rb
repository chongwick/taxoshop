S=Struct.new(:a,:b,:c); s=S.new(1,2,3)
i=Object.new; def i.to_int; 0; end
s[i]=9 rescue (puts "raised"); puts "st01 ok"
