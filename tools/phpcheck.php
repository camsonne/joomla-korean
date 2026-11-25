<?php
// Parse every ko-KR .ini exactly the way Joomla's LanguageHelper::parseIniFile() does:
// parse_ini_file(..., INI_SCANNER_RAW) with every PHP warning turned into an error.
set_error_handler(static function ($errno, $err) { throw new \Exception($err); }, E_WARNING);
$bad = 0; $n = 0;
foreach (['site', 'admin', 'api'] as $d) {
    foreach (glob(dirname(__DIR__) . "/$d/*.ini") as $f) {
        try {
            $r = parse_ini_file($f, false, INI_SCANNER_RAW);
            if (!is_array($r)) { throw new \Exception('not an array'); }
            $n += count($r);
        } catch (\Throwable $e) { echo "FAIL $f: {$e->getMessage()}\n"; $bad++; }
    }
}
echo $bad ? "$bad file(s) fail\n" : "all parse, $n keys\n";
exit($bad ? 1 : 0);
