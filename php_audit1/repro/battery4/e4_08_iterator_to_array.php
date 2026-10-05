<?php
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
echo "OK\n";
