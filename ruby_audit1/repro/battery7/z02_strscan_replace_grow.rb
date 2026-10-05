require 'strscan'
s = "a"*4000
sc = StringScanner.new(s)
sc.scan(/a{10}/)
s.replace("b"*100000)         # realloc to new address
sc.scan(/b+/) rescue (puts "raised")
puts "z02 ok"
