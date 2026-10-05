<?php
class It implements Iterator {
  private $i=0;
  function current():mixed{ if($this->i===2) throw new Exception("x"); return $this->i; }
  function key():mixed{ return $this->i; }
  function next():void{ $this->i++; }
  function rewind():void{ $this->i=0; }
  function valid():bool{ return $this->i<5; }
}
try { iterator_to_array(new It()); } catch(\Throwable $e){ echo "caught\n"; }
