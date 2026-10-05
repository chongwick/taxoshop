# Auto-fuzz: call many Array methods with a block/arg that clears the receiver mid-op.
# Prints method name to STDERR before each call; an ASan abort pins the culprit.
def fresh; (1..4000).to_a; end
$log = ->(m){ STDERR.puts("TRY #{m}") }

# block methods: block clears receiver on first call
block_methods = %i[
  each each_index each_with_index each_with_object map map! flat_map collect_concat
  select select! filter filter! reject reject! find_all find find_index index rindex
  detect count sum min max min_by max_by minmax minmax_by sort sort! sort_by sort_by!
  group_by partition chunk_while slice_when each_cons each_slice take_while drop_while
  cycle find_index all? any? none? one? tally_by filter_map collect collect!
  delete_if keep_if reduce inject each_entry
]
block_methods.each do |m|
  a = fresh
  $log.(m)
  begin
    case m
    when :each_cons, :each_slice then a.send(m, 2){ a.clear }
    when :reduce, :inject then a.send(m){|x,y| a.clear; x }
    when :each_with_object then a.each_with_object([]){|x,o| a.clear }
    else a.send(m){|*x| a.clear; true } rescue a.send(m){|*x| a.clear; 0 }
    end
  rescue Exception
  end
end

# arg methods with an evil to_ary/to_int/hash that clears receiver
class ToAry; def to_ary; $a.clear; [1,2,3]; end; end
class ToInt; def to_int; $a.clear; 2000; end; end
class Hsh;   def hash; $a.clear; 1; end; def eql?(o); false; end; end

arg_specs = {
  :+       => ->(a){ a + ToAry.new },
  :-       => ->(a){ a - ToAry.new },
  :&       => ->(a){ a & ToAry.new },
  :|       => ->(a){ a | ToAry.new },
  :concat  => ->(a){ a.concat(ToAry.new) },
  :replace => ->(a){ a.replace(ToAry.new) },
  :zip     => ->(a){ a.zip(ToAry.new) },
  :product => ->(a){ a.product(ToAry.new) },
  :flatten_e => ->(a){ a2=a.dup; a2 << ToAry.new; $a=a2; a2.flatten },
  :fill    => ->(a){ a.fill(9, 0, ToInt.new) },
  :first   => ->(a){ a.first(ToInt.new) },
  :last    => ->(a){ a.last(ToInt.new) },
  :take    => ->(a){ a.take(ToInt.new) },
  :drop    => ->(a){ a.drop(ToInt.new) },
  :sample  => ->(a){ a.sample(ToInt.new) },
  :rotate  => ->(a){ a.rotate(ToInt.new) },
  :assoc   => ->(a){ a2=a.map{|x|[x,x]}; a2 << ToAry.new; $a=a2; a2.assoc(1) },
  :aref2   => ->(a){ a[ToInt.new, 50] },
  :aref_len => ->(a){ a[2, ToInt.new] },
  :insert  => ->(a){ a.insert(ToInt.new, 1,2,3) },
  :vat     => ->(a){ a.values_at(ToInt.new, 0) },
  :dig     => ->(a){ a.dig(ToInt.new) },
  :pack    => ->(a){ a2=a.dup; a2[100]=ToInt.new; a2.pack("C*") },
  :uniq_h  => ->(a){ a2=a.dup; a2 << Hsh.new; a2.uniq },
}
arg_specs.each do |name, blk|
  $a = fresh
  a = $a
  $log.(name)
  begin; blk.(a); rescue Exception; end
end
puts "AUTOFUZZ COMPLETE"
