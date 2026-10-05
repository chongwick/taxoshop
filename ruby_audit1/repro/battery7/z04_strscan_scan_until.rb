require 'strscan'
s = "a"*4000 + "Z"
sc = StringScanner.new(s)
s.clear
sc.scan_until(/Z/) rescue (puts "raised")
sc.rest rescue nil
puts "z04 ok"
