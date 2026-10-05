<?php
class E { public $data; function __construct(){ $this->data = range(0,500);} function __sleep(){ static $n=0; if($n++<3){ $this->data[]=range(0,100);} return ['data']; } }
$arr=[]; for($i=0;$i<50;$i++)$arr[]=new E();
echo strlen(serialize($arr)),"\n";
echo "OK\n";
