<?php
// generator writes many reentrancy triggers, each a standalone file
$T = [];

// ---- multi-callback set ops: comparator clears/shrinks an input mid-sort ----
$T['e4_01_udiff_uassoc_clear'] = <<<'P'
$GLOBALS['b'] = array_map(fn($i)=>"v$i", range(0,2000));
$a = array_map(fn($i)=>"v$i", range(0,2000));
$cmp = function($x,$y){ static $n=0; if($n++==5){ $GLOBALS['b']=[]; gc_collect_cycles(); } return strcmp((string)$x,(string)$y); };
$k = function($x,$y){ return strcmp((string)$x,(string)$y); };
var_dump(count(array_udiff_uassoc($a,$GLOBALS['b'],$cmp,$k)));
P;

$T['e4_02_uintersect_uassoc_clear'] = <<<'P'
$GLOBALS['b'] = array_map(fn($i)=>"v$i", range(0,2000));
$a = array_map(fn($i)=>"v$i", range(0,2000));
$cmp = function($x,$y){ static $n=0; if($n++==5){ $GLOBALS['b']=[]; gc_collect_cycles(); } return strcmp((string)$x,(string)$y); };
$k = fn($x,$y)=>strcmp((string)$x,(string)$y);
var_dump(count(array_uintersect_uassoc($a,$GLOBALS['b'],$cmp,$k)));
P;

$T['e4_03_udiff_clear_self'] = <<<'P'
$a = array_map(fn($i)=>"v$i", range(0,3000));
$GLOBALS['a'] =& $a;
$b = ['x'];
$cmp = function($x,$y){ static $n=0; if($n++==3){ $GLOBALS['a']=[]; gc_collect_cycles(); } return strcmp((string)$x,(string)$y); };
var_dump(count(array_udiff($a,$b,$cmp)));
P;

$T['e4_04_diff_ukey_clear'] = <<<'P'
$GLOBALS['b'] = array_fill_keys(range(0,2000),1);
$a = array_fill_keys(range(0,2000),1);
$k = function($x,$y){ static $n=0; if($n++==5){ $GLOBALS['b']=[]; gc_collect_cycles(); } return $x<=>$y; };
var_dump(count(array_diff_ukey($a,$GLOBALS['b'],$k)));
P;

$T['e4_05_intersect_ukey_clear'] = <<<'P'
$GLOBALS['b'] = array_fill_keys(range(0,2000),1);
$a = array_fill_keys(range(0,2000),1);
$k = function($x,$y){ static $n=0; if($n++==5){ $GLOBALS['b']=[]; gc_collect_cycles(); } return $x<=>$y; };
var_dump(count(array_intersect_ukey($a,$GLOBALS['b'],$k)));
P;

// ---- object __toString clears an input during set-op sort ----
$T['e4_06_udiff_tostring_free'] = <<<'P'
class E { public $i; function __construct($i){$this->i=$i;} function __toString(){ static $n=0; if($n++==4){ $GLOBALS['a']=[]; gc_collect_cycles(); } return "v".$this->i; } }
$a=[]; for($i=0;$i<2000;$i++)$a[]=new E($i);
$GLOBALS['a']=&$a;
$b=[new E(999999)];
var_dump(count(array_udiff($a,$b,fn($x,$y)=>strcmp((string)$x,(string)$y))));
P;

// ---- array_multisort by-ref, __toString grows/clears a parallel column ----
$T['e4_07_multisort_clear'] = <<<'P'
class E { public $i; function __construct($i){$this->i=$i;} function __toString(){ static $n=0; if($n++==4){ $GLOBALS['col2']=[]; gc_collect_cycles(); } return sprintf("%05d",$this->i%7); } }
$col1=[]; for($i=0;$i<2000;$i++)$col1[]=new E($i);
$col2=range(0,1999); $GLOBALS['col2']=&$col2;
array_multisort($col1, SORT_STRING, $col2);
var_dump(count($col2));
P;

// ---- iterator_to_array: Iterator::current mutates a shared source ----
$T['e4_08_iterator_to_array'] = <<<'P'
class It implements Iterator {
  public $i=0; public $arr;
  function __construct(){ $this->arr = range(0,3000); }
  function rewind():void{$this->i=0;}
  function valid():bool{return $this->i < 3000;}
  function key():mixed{return $this->i;}
  function current():mixed{ if($this->i==5){ $this->arr=[]; gc_collect_cycles(); } return $this->i; }
  function next():void{$this->i++;}
}
var_dump(count(iterator_to_array(new It())));
P;

// ---- ArrayObject / ArrayIterator sorts with mutating comparator ----
$T['e4_09_arrayiterator_uasort'] = <<<'P'
$it = new ArrayIterator(range(0,2000));
$it->uasort(function($x,$y) use($it){ static $n=0; if($n++==3){ for($k=0;$k<50;$k++)$it[]="x$k"; } return $x<=>$y; });
var_dump($it->count());
P;

$T['e4_10_arrayobject_natsort'] = <<<'P'
class E { public $i; function __construct($i){$this->i=$i;} function __toString(){ static $n=0; if($n++==4){ $GLOBALS['ao']->exchangeArray([]); } return "v".$this->i; } }
$data=[]; for($i=0;$i<2000;$i++)$data[]=new E($i);
$ao = new ArrayObject($data); $GLOBALS['ao']=$ao;
$ao->natsort();
var_dump($ao->count());
P;

// ---- SplFixedArray reentrancy ----
$T['e4_11_splfixed_tostring'] = <<<'P'
class E { public $fa; public $i; function __construct($fa,$i){$this->fa=$fa;$this->i=$i;} function __toString(){ static $n=0; if($n++==2){ $this->fa->setSize(2); gc_collect_cycles(); } return "v".$this->i; } }
$fa = new SplFixedArray(2000);
for($i=0;$i<2000;$i++)$fa[$i]=null;
for($i=0;$i<2000;$i++)$fa[$i]=new E($fa,$i);
$s=''; foreach($fa as $v){ $s.=(string)$v; }
var_dump(strlen($s));
P;

// ---- SplObjectStorage offsetGet/attach reentrancy ----
$T['e4_12_splobjectstorage'] = <<<'P'
$s = new SplObjectStorage();
$objs=[]; for($i=0;$i<2000;$i++){ $o=new stdClass; $objs[]=$o; $s->attach($o,$i); }
$n=0;
foreach($s as $o){ if($n++==5){ foreach($objs as $o2)$s->detach($o2); gc_collect_cycles(); } $x=$s->getInfo(); }
var_dump($s->count());
P;

// ---- in_array/array_search loose compare of object mutating haystack (ref) ----
$T['e4_13_in_array_ref'] = <<<'P'
class E { function __toString(){ $GLOBALS['a']=[]; gc_collect_cycles(); return "zzz"; } }
$a = array_map(fn($i)=>"v$i", range(0,3000)); $a[]= "match";
$GLOBALS['a']=&$a;
var_dump(in_array(new E(), $a));
P;

// ---- array_reduce callback clears input ----
$T['e4_14_array_reduce'] = <<<'P'
$a = range(0,3000); $GLOBALS['a']=&$a;
$r = array_reduce($a, function($c,$v){ static $n=0; if($n++==5){ $GLOBALS['a']=[]; gc_collect_cycles(); } return $c+$v; }, 0);
var_dump($r);
P;

// ---- usort comparator replaces array with references defeating COW ----
$T['e4_15_usort_ref_defeat'] = <<<'P'
$a = range(0,3000);
$ref =& $a; $GLOBALS['a'] =& $a;
usort($a, function($x,$y){ static $n=0; if($n++==3){ $GLOBALS['a'][0]="poison"; } return $x<=>$y; });
var_dump(count($a));
P;

// ---- serialize with __sleep returning growing / __toString ----
$T['e4_16_serialize_sleep'] = <<<'P'
class E { public $data; function __construct(){ $this->data = range(0,500);} function __sleep(){ static $n=0; if($n++<3){ $this->data[]=range(0,100);} return ['data']; } }
$arr=[]; for($i=0;$i<50;$i++)$arr[]=new E();
echo strlen(serialize($arr)),"\n";
P;

// ---- array_walk_recursive structural mutation of parent ----
$T['e4_17_walk_recursive'] = <<<'P'
$a = ['x'=>range(0,1000), 'y'=>range(0,1000), 'z'=>range(0,1000)];
$GLOBALS['a']=&$a;
$n=0;
array_walk_recursive($a, function(&$v,$k) use(&$n){ if($n++==5){ unset($GLOBALS['a']['y']); $GLOBALS['a']['x']=[1]; gc_collect_cycles(); } $v=$v; });
var_dump(count($a));
P;

// ---- array_map multi-array, callback clears one ----
$T['e4_18_array_map_multi'] = <<<'P'
$a = range(0,3000); $b = range(0,3000); $GLOBALS['b']=&$b;
$r = array_map(function($x,$y){ static $n=0; if($n++==5){ $GLOBALS['b']=[]; gc_collect_cycles(); } return $x+$y; }, $a, $b);
var_dump(count($r));
P;

// ---- min/max with mutating compare ----
$T['e4_19_max_compare'] = <<<'P'
class E { public $i; function __construct($i){$this->i=$i;} function __toString(){ static $n=0; if($n++==4){ $GLOBALS['a']=[]; gc_collect_cycles(); } return sprintf("%05d",$this->i); } }
$a=[]; for($i=0;$i<3000;$i++)$a[]=new E($i);
$GLOBALS['a']=&$a;
var_dump((string)max($a));
P;

// ---- json_encode jsonSerialize returns huge growing + destruct ----
$T['e4_20_json_serialize'] = <<<'P'
class E implements JsonSerializable { public $i; function __construct($i){$this->i=$i;} function jsonSerialize():mixed{ static $n=0; if($n++==4){ $GLOBALS['a']=[]; gc_collect_cycles(); } return $this->i; } }
$a=[]; for($i=0;$i<3000;$i++)$a[]=new E($i);
$GLOBALS['a']=&$a;
echo strlen(json_encode($a)),"\n";
P;

foreach ($T as $name=>$body) {
  file_put_contents(__DIR__."/$name.php", "<?php\n".$body."\necho \"OK\\n\";\n");
}
echo "wrote ".count($T)." files\n";
