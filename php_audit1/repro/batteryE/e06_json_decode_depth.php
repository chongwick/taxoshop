<?php $s=str_repeat('[',600).str_repeat(']',600); json_decode($s); echo json_last_error_msg(),"\n";
