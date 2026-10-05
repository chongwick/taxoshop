<?php
// more natural: no explicit &, haystack is an object property (by-ref via prop table? test)
class E { public $box; function __toString(){ $this->box->h = []; return "zzz"; } }
$h = array_map(fn($i)=>"v$i", range(0,2000)); $h[]="needle";
$box = new stdClass; $box->h = $h;
$e = new E(); $e->box = $box;
var_dump(in_array($e, $box->h));
echo "done\n";
