class L; def self._load(s); s.clear if s.respond_to?(:clear); new; end; end
data = Marshal.dump(L.new)
Marshal.load(data) rescue (puts "raised"); puts "m01 ok"
