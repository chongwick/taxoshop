require 'json'
$src = '{' + (1..2000).map{|i| %Q{"k#{i}":#{i}} }.join(",") + '}'
JSON.load($src, proc { |o| $src.replace("z"*200000) if $src && !$d; $d=true }) rescue (puts "raised: #{$!.class}")
puts "j05 ok"
