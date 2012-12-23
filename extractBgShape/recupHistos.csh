#!/bin/csh


set list = `cat list | awk -F "&" '{print $1}'`

mkdir theHistos

foreach i ($list)
    echo "hello on va faire $i"
    cp $i/merged/*.root theHistos/histo_$i.root
end

