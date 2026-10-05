require 'strscan'
s = "abcdef"*1000
sc = StringScanner.new(s)
sc.pos = 5000
s.replace("x")                # shrink far below pos
sc.getch rescue (puts "raised")
sc.peek(100) rescue (puts "raised")
puts "z03 ok"
