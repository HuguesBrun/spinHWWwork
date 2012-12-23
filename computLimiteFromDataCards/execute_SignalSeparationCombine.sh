#! /bin/bash

### Inputs:
# 1: directory with cards
# 2: card (signal model1 + signal model2)
# 3: what to do (default is run hypothesis test)


if [ $# -lt 2 ]
    then
    echo "Need at least two arguments: "
    echo "    1) directory with cards"
    echo "    2) card name"
    echo "    3) action (not mandatory, default=1)"
    exit 1
fi


cardDir=$1
card1=$2


cp runSignalSeparation.py tdrstyle.cc $cardDir/

cd $cardDir
outDir="output_combine/"

if [ -d $outDir ]
    then
    echo "Output directory ${cardDir}/${outDir}/ already exisiting. I will not overwrite. Please remove it and try again."
    exit 2
fi

mkdir $outDir




action=1
if [ $# -ge 3 ]
    then
    action=$3
fi


# Run hypothesis testing, using nominal value of nuisances and mu for generation
NTOYS=4000 # toys per  job
MH=125  # mass of the signal hypothesis

if [ $action -eq 1 ]
    then 
### FIXED MU: 
    text2workspace.py -m $MH $card1 -P HiggsAnalysis.CombinedLimit.HiggsJPC:twoHypothesisHiggs -o fixedMu.root
    combine -m 125 -M HybridNew --testStat=LEP --generateExt=1 --generateNuis=0 fixedMu.root --singlePoint 1 --saveHybridResult --fork 4 -T $NTOYS -i 1 --clsAcc 0 --fullBToys -S 0 
#make the tree of the test statistics distribution (the macro is under HiggsAnalysis/CombinedLimit/test/plotting)
    root -q -b higgsCombineTest.HybridNew.mH125.root "${CMSSW_BASE}/src/HiggsAnalysis/CombinedLimit/test/plotting/hypoTestResultTree.cxx(\"qmu.root\",125,1,\"x\")"
elif [ $action -eq 2 ]
    then
### Run 1D scan:
### FLOAT MU:
    text2workspace.py -m $MH $card1 -P HiggsAnalysis.CombinedLimit.HiggsJPC:twoHypothesisHiggs  --PO=muFloating -o floatMu.root
    combine -M MultiDimFit floatMu.root --algo=grid --points 100  -m 125 -v 2 -n 1D
#draw the output
###      limit->Draw("2*deltaNLL:x", "deltaNLL > 0","PL")
elif [ $action -eq 3 ]
    then
#Run 2D scan (without profiling nuisances)
### FOR 2D: 
    text2workspace.py -m $MH $card1 -P HiggsAnalysis.CombinedLimit.HiggsJPC:twoHypothesisHiggs --PO=muAsPOI -o twoD.root
    combine -M MultiDimFit twoD.root --algo=grid --points 10000 --fastScan  -m 125 -v 2
###after this open root file qmu.root and do
###     limit->Draw("2*deltaNLL:r:x>>h2d(100,0,1,100,0,4)","deltaNLL >0","PROF COLZ");
###     h2d->SetContour(100);
###and add best fit point
#     limit->Draw("r:x","deltaNLL == 0","P SAME")
#     ((TGraph*) gROOT->FindObject("Graph"))->SetMarkerStyle(20);
#     ((TGraph*) gROOT->FindObject("Graph"))->SetMarkerSize(1.5);
else
    echo "Requested to perform and unrecognized action: "${action}
    echo "action can be 0:hypothesis test  ;   1:1D scan   ;   2:2D scan"
    echo "Exiting."
    exit 3
fi

