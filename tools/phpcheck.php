<?php
// Parse every ko-KR .ini the way Joomla does (Language::parse uses parse_ini_file, INI_SCANNER_RAW).
$bad = 0; $n = 0;
foreach (['site', 'admin', 'api'] as $d) {
    foreach (glob(dirname(__DIR__) . "/$d/*.ini") as $f) {
        $r = @parse_ini_file($f, false, INI_SCANNER_RAW);
        if ($r === false) { echo "FAIL $f\n"; $bad++; continue; }
        $n += count($r);
    }
}
echo $bad ? "$bad file(s) fail\n" : "all parse, $n keys\n";
exit($bad ? 1 : 0);
