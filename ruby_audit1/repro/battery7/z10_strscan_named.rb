require 'strscan'
s = "hello world "*500
sc = StringScanner.new(s)
sc.scan(/(?<w>\w+)/)
s.clear
sc[:w] rescue (puts "raised")
sc.pre_match rescue (puts "raised")
puts "z10 ok"
