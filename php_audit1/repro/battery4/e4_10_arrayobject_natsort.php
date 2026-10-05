<?php
class E { public $i; function __construct($i){$this->i=$i;} function __toString(){ static $n=0; if($n++==4){ $GLOBALS['ao']->exchangeArray([]); } return "v".$this->i; } }
$data=[]; for($i=0;$i<2000;$i++)$data[]=new E($i);
$ao = new ArrayObject($data); $GLOBALS['ao']=$ao;
$ao->natsort();
var_dump($ao->count());
echo "OK\n";
