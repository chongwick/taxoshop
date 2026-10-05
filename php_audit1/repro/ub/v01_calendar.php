<?php
function t($lbl,$fn){ try{ $fn(); }catch(\Throwable $e){ /*ignore*/ } echo "$lbl\n"; }
// easter_days accepts up to 7378697629483820644 -> internal Gauss math overflows
t('easter_days_max', fn()=>easter_days(7378697629483820644));
t('easter_days_big', fn()=>easter_days(1000000000000000000));
t('easter_date_big', fn()=>easter_date(2000000000));
// gregoriantojd/jdtogregorian accepted large values
t('greg2jd', fn()=>gregoriantojd(1,1,32767));
t('greg2jd_big', fn()=>gregoriantojd(12,31,2000000000));
t('jd2greg_big', fn()=>jdtogregorian(536838867));
t('jewish', fn()=>jdtojewish(347998));
t('jewishtojd_big', fn()=>jewishtojd(12,29,6000000));
t('frenchtojd', fn()=>frenchtojd(13,5,14));
t('jdtofrench', fn()=>jdtofrench(2375840));
t('cal_from_jd_jewish', fn()=>cal_from_jd(347998, CAL_JEWISH));
t('cal_days_jewish', fn()=>cal_days_in_month(CAL_JEWISH, 13, 6000000));
echo "v01 done\n";
