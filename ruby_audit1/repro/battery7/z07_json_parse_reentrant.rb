require 'json'
JSON.parse('[1,2,' * 1000) rescue (puts "raised")
puts "z07 ok"
