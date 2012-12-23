#!/bin/csh

set list = `ls datacards/dataCard_*.txt`

foreach i ($list)
    echo $i
    set nameVar = `echo $i | awk -F "_" '{ print $2 }' | awk -F "." '{print $1}'`
    mkdir datacards/$nameVar
    mv $i datacards/$nameVar
end

