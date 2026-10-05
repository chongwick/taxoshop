require 'set'
# Set reentrancy fuzzer. Each test mutates the receiver (or a table captured by
# the C op) via user code (each / hash / eql? / block) reachable mid-operation.
$log = ->(m){ STDERR.puts("TRY #{m}") }
def big;  s = Set.new; (0...4000).each{|i| s << i}; s; end

# ---- evil enumerable whose #each clears/mutates a target set mid-iteration ----
class EvilEnum
  def initialize(tgt, extra=[1,2,3]); @tgt=tgt; @extra=extra; end
  def each
    @tgt.clear
    (0...5000).each{|i| @tgt << (i+100000)}   # force rehash/realloc of target table
    @extra.each{|x| yield x}
  end
  include Enumerable
end

# evil element: its #hash mutates a target set (fires during lookup/insert)
class EvilHash
  def initialize(tgt); @tgt=tgt; end
  def hash; @tgt.clear; (0...5000).each{|i| @tgt << (i+200000)}; 42; end
  def eql?(o); false; end
end

# enumerable whose #each resets the target's table type (compare_by_identity) then grows it
class CbiEnum
  include Enumerable
  def initialize(tgt); @tgt=tgt; end
  def each
    @tgt.compare_by_identity
    (0...3000).each{|i| @tgt << i}
    yield 1
  end
end

tests = {
  intersection_enum: ->{ s=big; s & EvilEnum.new(s) },
  intersection_hash: ->{ s=big; o=Set.new([EvilHash.new(s)]); s & o },
  union_enum:        ->{ s=big; s | EvilEnum.new(s) },
  merge_enum:        ->{ s=big; s.merge(EvilEnum.new(s)) },
  subtract_enum:     ->{ s=big; s.subtract(EvilEnum.new(s)) },
  xor_enum:          ->{ s=big; s ^ EvilEnum.new(s) },
  minus_enum:        ->{ s=big; s - EvilEnum.new(s) },
  subset_hash:       ->{ s=big; o=Set.new([EvilHash.new(s)]); o.subset?(s) },
  superset_hash:     ->{ s=big; o=Set.new([EvilHash.new(s)]); s.superset?(o) },
  disjoint_hash:     ->{ s=big; o=Set.new([EvilHash.new(s)]); s.disjoint?(o) },
  intersect_hash:    ->{ s=big; o=Set.new([EvilHash.new(s)]); s.intersect?(o) },
  eq_hash:           ->{ s=big; o=Set.new([EvilHash.new(s)]); s == o },
  # block methods mutate receiver mid-iteration
  each_clear:        ->{ s=big; s.each{|x| s.clear; s.add(99) rescue nil} },
  classify_clear:    ->{ s=big; s.classify{|x| s.clear rescue nil; x%3} },
  divide_clear:      ->{ s=big; s.divide{|x| s.clear rescue nil; x%3} },
  collect_clear:     ->{ s=big; s.collect!{|x| s.add(x+1) rescue nil; x} },
  delete_if_add:     ->{ s=big; s.delete_if{|x| s.add(x+500000) rescue nil; false} },
  keep_if_add:       ->{ s=big; s.keep_if{|x| s.add(x+500000) rescue nil; true} },
  reject_add:        ->{ s=big; s.reject!{|x| s.add(x+500000) rescue nil; false} },
  select_add:        ->{ s=big; s.select!{|x| s.add(x+500000) rescue nil; true} },
  # flatten with evil nested set whose each mutates outer
  flatten_evil:      ->{ inner=Set.new([1,2,3]); outer=Set.new([inner, 4,5]);
                         def inner.each(&b); $o.clear rescue nil; super; end if false;
                         outer.flatten },
  # compare_by_identity reset mid other.each
  cbi_reset:         ->{ s=big; s & CbiEnum.new(s) },
  reset_during_iter: ->{ s=big; s.each{|x| s.compare_by_identity rescue nil} },
}

tests.each do |name, t|
  $log.(name)
  begin; t.call; rescue Exception => e; end
end
puts "SETFUZZ COMPLETE"
