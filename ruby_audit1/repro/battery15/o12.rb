begin; "aaaa".unpack("@#{2**62}C"); rescue Exception; end; puts 'ok'
