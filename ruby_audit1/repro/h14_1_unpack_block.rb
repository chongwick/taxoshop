# H14-1: String#unpack with a block caches s=RSTRING_PTR(str) at pack.c:1131,
# then rb_yield()s inside the decode loop with no str_mod_check afterward.
# If the block frees/reallocs the source buffer, subsequent UNPACK_FETCH reads dangle.

# Variant A: shrink/replace the source mid-iteration
begin
  s = "A" * 400
  n = 0
  s.unpack("C*") do |_c|
    n += 1
    s.replace("") if n == 1      # free the original heap buffer
  end
rescue => e
  puts "A rescued: #{e.class}"
end
puts "A done"

# Variant B: grow the source to force realloc mid-iteration
begin
  s = "B" * 64
  n = 0
  s.unpack("C*") do |_c|
    n += 1
    s << ("x" * 100000) if n == 1  # realloc the buffer to a new address
  end
rescue => e
  puts "B rescued: #{e.class}"
end
puts "B done"

# Variant C: unpack1 with block-less but keyword offset conversion is separate (H137-2)
# Variant D: clear via slice buffer, wide directive to keep reading after free
begin
  s = "C" * 4000
  n = 0
  s.unpack("L*") do |_c|
    n += 1
    s.clear if n == 1
  end
rescue => e
  puts "D rescued: #{e.class}"
end
puts "D done"

puts "H14-1 completed cleanly"
