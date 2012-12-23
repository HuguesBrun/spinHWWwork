#!/bin/csh

setenv DIRDATACARDS datacardsGrav_normed 
setenv FINALPLOTS plotsFinalsGrav_normed

set list=`ls $DIRDATACARDS`
mkdir $FINALPLOTS

foreach  i ($list)
	if !(-d $DIRDATACARDS/$i) continue
	cp extractSignificanceStats.C $DIRDATACARDS/$i
	cd $DIRDATACARDS/$i
	root -b -q  'extractSignificanceStats.C("'$i'")'
	cd ../..
	cp $DIRDATACARDS/$i/sigsep_combine.png $FINALPLOTS/signif_$i.png
end 




