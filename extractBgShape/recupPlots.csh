#!/bin/csh


set list = `cat list | awk -F "&" '{print $1}'`

mkdir thePlots

foreach i ($list)
    echo "hello on va faire $i"
    cp $i/stacks/*.png thePlots/plot_$i.png
end

