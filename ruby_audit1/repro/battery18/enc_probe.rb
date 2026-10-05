%w[US-ASCII ISO-8859-1 EUC-JP Shift_JIS Windows-1252 ASCII-8BIT UTF-16BE].each do |e|
  begin
    "あA".encode(e)
    STDERR.puts "#{e}: converted OK (no undef)"
  rescue Encoding::UndefinedConversionError => ex
    STDERR.puts "#{e}: UNDEF (good, transcoder exists)"
  rescue Encoding::ConverterNotFoundError
    STDERR.puts "#{e}: NO CONVERTER"
  rescue => ex
    STDERR.puts "#{e}: #{ex.class}"
  end
end
