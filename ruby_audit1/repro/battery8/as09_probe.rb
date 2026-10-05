class Evil < Numeric
  def initialize(v); @v=v; end
  def val; @v; end
  def <=>(o); @v <=> (o.is_a?(Evil) ? o.val : o); end
  def to_int; $a.clear; @v; end
  def to_i; @v; end
  def coerce(o); [o, @v]; end
end
$a = (1..3000).to_a
r = Range.new(Evil.new(2900), Evil.new(2950))
res = $a[r]
STDERR.puts "res.class=#{res.class} res.length=#{res.length rescue 'ERR'}"
# Try to weaponize the possibly-corrupt result
STDERR.puts "dup..."; (res.dup rescue STDERR.puts("dup raised"))
STDERR.puts "each..."; (res.each{|x| x} rescue STDERR.puts("each raised"))
STDERR.puts "plus..."; (z = res + [1,2,3]; STDERR.puts "plus len=#{z.length}" rescue STDERR.puts("plus raised"))
STDERR.puts "done"
