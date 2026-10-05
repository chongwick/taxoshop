require 'strscan'
s = "a"*4000
sc = StringScanner.new(s)
sc.scan(/a{10}/)
s.clear                       # shrink/free source buffer under the scanner
sc.scan(/a+/) rescue (puts "raised")
sc.pre_match rescue nil
puts "z01 ok"
