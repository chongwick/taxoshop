# Array#sum: element coerce/+ clears the array
a = [1] * 5000
$a = a
class Evil5; def coerce(o); $a.clear; $a.replace([]); GC.start; [0,0]; end; end
a[4000] = Evil5.new
a.sum
puts "t06 ok"
