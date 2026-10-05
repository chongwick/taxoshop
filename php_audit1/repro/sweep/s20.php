<?php try{ $p=new DatePeriod("R100000000/2000-01-01T00:00:00Z/P1D"); }catch(\Throwable $e){} @date_create_from_format("Y","999999999999999"); echo "ok\n";
