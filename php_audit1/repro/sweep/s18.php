<?php @iconv("UTF-8","ISO-2022-JP//TRANSLIT", str_repeat("あ",50)); @iconv_mime_decode("=?UTF-8?B?".base64_encode("test")."?= =?x?Q?=FF?=", 0, "UTF-8"); echo "ok\n";
