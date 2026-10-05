require 'json'
class Evil < Hash
  def []=(k, v); $src.clear if $src && !$d; $d=true; super; end
end
$src = '{' + (1..2000).map{|i| %Q{"k#{i}":#{i}} }.join(",") + '}'
JSON.parse($src, object_class: Evil) rescue (puts "raised: #{$!.class}")
puts "j02 ok"
