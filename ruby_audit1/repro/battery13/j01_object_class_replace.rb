require 'json'
class Evil < Hash
  def []=(k, v)
    $src.replace("Z" * 300000) if $src && !$done   # realloc source buffer mid-parse
    $done = true
    super
  end
end
$src = ('{"a":' * 200) + '1' + ('}' * 200)
JSON.parse($src, object_class: Evil) rescue (puts "raised: #{$!.class}")
puts "j01 ok"
