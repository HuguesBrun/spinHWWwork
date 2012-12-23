#!/bin/csh

#root -l -b -q 'prepSigHisto.C("tree_skim_wwcommon_newvars/nominals/latino_1125_ggToH125toWWTo2LAndTau2Nu.root","ggToH125toWWTo2LAndTau2Nu.root")'
root -l -b -q 'prepSigHisto.C("tree_skim_wwcommon_newvars/nominals/latino_8001_SMH125ToWW2L2Nu.root","SMH125ToWW2L2Nu.root")'
root -l -b -q 'prepSigHisto.C("tree_skim_wwcommon_newvars/nominals/latino_8002_Higgs0M125ToWW2L2Nu.root","Higgs0M125ToWW2L2Nu.root")'
root -l -b -q 'prepSigHisto.C("tree_skim_wwcommon_newvars/nominals/latino_8003_Graviton2PM.root","Graviton2PM.root")'
