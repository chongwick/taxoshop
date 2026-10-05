require 'date'
inputs = []
# pathological date strings
inputs << ("9"*100000)
inputs << ("-" * 5000)
inputs << ("Mon " * 3000)
inputs << ("2020-" + "9"*10000 + "-01")
inputs << (":"*10000)
inputs << ("T"*10000)
inputs << ("+0900" * 2000)
inputs << ("1000000000000000000000000-01-01")
inputs << ("\x00" * 1000)
inputs << ("2020-01-01T00:00:00." + "0"*100000)
inputs << ("th " * 5000)
inputs << ("2020" + "e" * 100000)
count=0
inputs.each do |s|
  [:_parse, :parse].each do |m|
    begin; Date.send(m, s); rescue Exception; end
    count+=1
  end
  begin; Date.strptime(s, "%Y-%m-%d"); rescue Exception; end
  begin; DateTime.parse(s); rescue Exception; end
  begin; Time.parse(s) if defined?(Time.parse); rescue Exception; end
  count+=3
end
puts "DT FUZZ DONE #{count}"
