a=(1..3000).to_a
lo=Object.new; def lo.<=>(o); 0; end
5.clamp(lo, 10) rescue (puts "raised"); puts "c01 ok"
