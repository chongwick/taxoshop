begin; [1,2,3].pack("C#{2**31}"); rescue Exception; end; puts 'ok'
