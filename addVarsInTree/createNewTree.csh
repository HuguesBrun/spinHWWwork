#!/bin/csh

setenv treeDirectory treeDirs
setenv outDirectory myOutDirec

set listDir = (`ls $treeDirectory`)

mkdir $outDirectory

foreach i ($listDir)
#  echo $i
    set listTree = (`ls $treeDirectory/$i | grep latino_ `)
    mkdir $outDirectory/$i
    foreach j ($listTree)
        echo "$treeDirectory/$i/$j"
        echo "now the the macro"
        root -l -b -q  $treeDirectory/$i/$j 'addWantedVars.cxx+("'$outDirectory'/'$i'/'$j'")'
    end
end

