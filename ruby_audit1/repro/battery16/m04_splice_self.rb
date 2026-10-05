a = (1..3000).to_a
a[100..2900] = a rescue (puts "raised: #{$!.class}")   # self-splice big
puts "m04 ok"
