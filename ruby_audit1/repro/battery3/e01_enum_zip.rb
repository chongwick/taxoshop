require 'set'
class C
  include Enumerable
  def each; @a ||= (1..3000).to_a; @a.each{|x| yield x}; end
  def mutate; @a.clear; end
end
c = C.new
evil = Object.new; $c=c
def evil.to_ary; $c.mutate; [1,2,3]; end
c.zip(evil) rescue (puts "raised")
puts "e01 ok"
