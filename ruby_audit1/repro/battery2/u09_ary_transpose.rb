rows = Array.new(2000){|i| [i, i+1]}
evil = Object.new; $rows=rows
def evil.to_ary; $rows.clear; [1,2]; end
rows << evil
rows.transpose rescue (puts "raised")
puts "u09 ok"
