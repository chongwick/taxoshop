# H80-2: Array#sort! comparator mutates the array. If sort! sorts live storage,
# replace/clear triggers realloc/free of the buffer ruby_qsort is permuting.

begin
  a = (1..2000).to_a
  a.sort! do |x, y|
    a.replace([])          # free/realloc the backing buffer mid-sort
    x <=> y
  end
rescue => e
  puts "A rescued: #{e.class}"
end
puts "A done"

# Variant B: grow the array during comparison to force realloc to a new address
begin
  a = (1..2000).to_a
  did = false
  a.sort! do |x, y|
    unless did
      did = true
      a.concat((1..200000).to_a)
    end
    x <=> y
  end
rescue => e
  puts "B rescued: #{e.class}"
end
puts "B done"

# Variant C: sort_by! (collects tuples over live storage)
begin
  a = (1..2000).to_a
  did = false
  a.sort_by! { |x| a.replace([]) unless did; did = true; x }
rescue => e
  puts "C rescued: #{e.class}"
end
puts "C done"

puts "H80-2 completed cleanly"
