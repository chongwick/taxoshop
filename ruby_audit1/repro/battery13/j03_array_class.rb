require 'json'
class EvilA < Array
  def <<(v); $src.replace("9"*300000) if $src && !$d; $d=true; super; end
end
$src = '[' + (1..3000).to_a.join(",") + ']'
JSON.parse($src, array_class: EvilA) rescue (puts "raised: #{$!.class}")
puts "j03 ok"
