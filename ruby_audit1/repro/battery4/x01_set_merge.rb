require 'set'
s=Set.new((1..3000).to_a); $s=s
e=Object.new; def e.each; $s.clear; yield 1; end; def e.is_a?(k); k==Enumerable||super; end
s.merge(e) rescue (puts "raised"); puts "x01 ok"
