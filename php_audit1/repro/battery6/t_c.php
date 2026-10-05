<?php
$s = new SplObjectStorage();
class D { public function __serialize(): array { global $s, $victim; $s->detach($victim); return []; } }
$a = new D();
$victim = new stdClass();
$s->attach($a, "1");
$s->attach($victim, "2");
$s->attach(new stdClass(), "3");
var_dump(strlen($s->serialize()));
echo "C done\n";
