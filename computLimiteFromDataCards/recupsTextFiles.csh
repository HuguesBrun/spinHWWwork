#!/bin/csh

set list = (`ls | grep datacards | tr -d ":"`)

mkdir allSigniResults

foreach i ($list)
	echo $i
	cp $i/separationResult.txt allSigniResults/${i}_results.txt
end

