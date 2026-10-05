rows=[]; 2000.times{|i| rows << [i,i]}
$rows=rows; $first=nil
e=Object.new
def e.to_ary; $rows.each{|r| r.clear if r.length==2 && r[0]==0}; [1,2]; end
rows << e
rows.transpose rescue (puts "raised"); puts "w12 ok"
