a=(1..3000).to_a; e=a.each
e.each{ a.clear; e.next rescue nil } rescue (puts "raised"); puts "c09 ok"
