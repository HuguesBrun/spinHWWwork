#!/bin/csh

setenv DIRDATACARDS datacardsGrav_normed 

set list=`ls $DIRDATACARDS`

foreach  i ($list)
	if !(-d $DIRDATACARDS/$i) continue
        ./execute_SignalSeparationCombine.sh $DIRDATACARDS/$i dataCard_$i.txt	
end 




