<?php @gzinflate(random_bytes(64)); @gzuncompress("\x78\x9c".random_bytes(64)); @gzdecode(random_bytes(64)); if(function_exists('bzdecompress')) @bzdecompress("BZh9".random_bytes(64)); echo "ok\n";
