class Bad
  def _dump(lvl); $out.clear if $out; "payload"; end
end
$out = String.new
Marshal.dump(Bad.new) rescue (puts "raised")
puts "t17 ok"
