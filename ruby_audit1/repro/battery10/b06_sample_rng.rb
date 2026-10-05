a=(1..3000).to_a; $a=a
rng=Object.new; def rng.rand(n); $a.clear; 0; end
a.sample(100, random: rng) rescue (puts "raised"); puts "b06 ok"
