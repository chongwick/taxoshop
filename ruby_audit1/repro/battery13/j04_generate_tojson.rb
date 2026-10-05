require 'json'
class Bad
  def to_json(*a); $arr.clear if $arr && !$d; $d=true; "1"; end
end
$arr = (1..3000).to_a
$arr[1500] = Bad.new
JSON.generate($arr) rescue (puts "raised: #{$!.class}")
puts "j04 ok"
