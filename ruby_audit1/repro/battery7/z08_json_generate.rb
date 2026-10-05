require 'json'
class Bad; def to_json(*a); $arr.clear if $arr; "1"; end; end
$arr = (1..1000).to_a
$arr[500] = Bad.new
JSON.generate($arr) rescue (puts "raised")
puts "z08 ok"
