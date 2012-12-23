#! /usr/bin/env python
import os
import re
import math
import ROOT
from array import array
import commands
import subprocess 
import glob

from optparse import OptionParser

ROOT.gROOT.ProcessLine(".L tdrstyle.cc")
from ROOT import setTDRStyle
ROOT.setTDRStyle(True)
ROOT.gStyle.SetPalette(1)
ROOT.gStyle.SetOptStat(0000)

m_cmssw_base=commands.getoutput("echo $CMSSW_BASE")
m_curdir=commands.getoutput("pwd")
#print m_cmssw_base,",",m_curdir

############################################
#            Job steering                  #
############################################
parser = OptionParser()

# ---- main modes
parser.add_option('-b', action='store_true', dest='noX', default=False,
                  help='no X11 windows')
parser.add_option('-g', '--generateToys',
                  action='store_true', dest='generateToys',default=False,
                  help='generate toys')
parser.add_option('-f', '--fitToys',
                  action='store_true', dest='fitToys',default=False,
                  help='fit toys')
parser.add_option('-p', '--plotResults',
                  action='store_true', dest='plotResults',default=False,
                  help='plot toy results')
parser.add_option('-m', '--multiJob',
                  action='store_true', dest='multiJob',default=False,
                  help='run in parallelization mode')
parser.add_option('-t', '--tool',
                  action='store', type='string', dest='tool',default='combine',
                  help='string: combine or lands')


# ----
# ---- run options
parser.add_option('-o', '--outputDir',
                  action='store', type='string', dest='outputDir',default='testOutput',
                  help='string: directory where all outputs go')
parser.add_option( '--inputCardDir',
                  action='store', type='string', dest='inputCardDir',default='./',
                  help='string: directory where all cards are')
parser.add_option('--card1',
                  action='store', type='string', dest='card1',default='dir/datacards/card',
                  help='string: datacard for hypothesis 1')
parser.add_option('--card2',
                  action='store', type='string', dest='card2',default='dir/datacards/card',
                  help='string: datacard for hypothesis 2')

parser.add_option('--seed',
                  action='store', type='int', dest='seed',default='12345',
                  help='int: seed')
parser.add_option('--toysPerJob',
                  action='store', type='int', dest='toysPerJob',default='5',
                  help='int: toys per job')
parser.add_option('--nParallelJobs',
                  action='store', type='int', dest='nParallelJobs',default='40',
                  help='int: number of parallel jobs')
parser.add_option('-a', '--addOutput',
                  action='store_true', dest='addOutput',default=False,
                  help='bool: when plotting, hadd up root files')

(options, args) = parser.parse_args()
############################################
############################################

###########################################################
## U T I L   U T I L   U T I L   U T I L   U T I L
###########################################################

def haddLands( newfile, listnames, offset ):

    fo = ROOT.TFile( newfile, "recreate" )
    to = ROOT.TTree("T", "T")    
    limit_ = array( 'f', [ 0. ] )
    rmean_ = array( 'f', [ 0. ] )
    to.Branch("limit", limit_ , "limit/F")
    to.Branch("rmean", rmean_ , "rmean/F")

    print listnames, ","

    for i in range(nParallelJobs):

        print "Seed ",seed
        if seed==12386  : continue
      
        seedd = seed+(i*4)   
        print "Seedd ",seedd
       # if seedd==12389 or seedd==12425 or seedd==12377 or seedd==12381 or seedd==12385 or seedd==12397 or seedd==12429 or seedd==12409 or seedd==12413 or seedd==12433: continue
        if seedd==12437 or seedd==12397 or seedd==12381 or seedd==12405 or seedd==12425   : continue
        
        for jj in range(toys):

            curfile = outputDir+"/"+listnames+"_"+str(seedd+offset)+"_"+str(jj)+"_maxllfit.root"
            print curfile
            fcur = ROOT.TFile( curfile )
            tcur = fcur.Get("T")
            nentries = int( tcur.GetEntries() )
            for i in range(nentries):
                tcur.GetEntry(i)
                limit_[0] = tcur.limit
                rmean_[0] = tcur.rmean
                print limit_[0],rmean_[0]
                to.Fill()
            fcur.Close()
    
    fo.cd()
    to.Write()
    fo.Close()

#    myfiles = []
#    allfiles = os.listdir(outputDir)
#    for files in allfiles:
##        print files
##        print outputDir+"/"+files
##        m = re.match("_testPS_testPS",outputDir+"/"+files)
#        if files.find(listnames) >= 0 and files.find("maxllfit.root") >= 0:
##            print m," ",listnames
#            myfiles.append( files )
#            print files

def getSeparationStats( l1, l2 ):
    
    print len(l1)
    print len(l2)    
    
    median1 = sorted(l1)[len(l1)/2]
    median2 = sorted(l2)[len(l2)/2]

    mean1 = sum(l1) / float(len(l1))
    mean2 = sum(l2) / float(len(l2))
    
    valsq = 0
    l1_lt_median2 = 0
    for i in range(len(l1)): 
        valsq = valsq + l1[i]*l1[i]
        if l1[i] < median2: l1_lt_median2 = l1_lt_median2 + 1
    rms1 = math.sqrt(valsq/float(len(l1)))

    valsq = 0
    l2_gt_median1 = 0
    for i in range(len(l2)): 
        valsq = valsq + l2[i]*l2[i]
        if l2[i] > median1: l2_gt_median1 = l2_gt_median1 + 1
    rms2 = math.sqrt(valsq/float(len(l2)))
    
    tailprob1 = float(l1_lt_median2)/float(len(l1))
    tailprob2 = float(l2_gt_median1)/float(len(l2))  

    sigma1 = ROOT.Math.normal_quantile_c(tailprob1, 1.0)
    sigma2 = ROOT.Math.normal_quantile_c(tailprob2, 1.0)

    print "median 1: ", median1, ", ",mean1,", ",rms1,", ",tailprob1,", ",sigma1
    print "median 2: ", median2, ", ",mean2,", ",rms2,", ",tailprob2,", ",sigma2

def getSestimator( fit1, fit2, hname ):

    h = ROOT.TH1F( hname,";S = -2 #times ln(L_{1}/L_{2});Number of Toys",40,-40,40 )
    
    print fit1,",",fit2
    f1 = ROOT.TFile(fit1)
    f2 = ROOT.TFile(fit2)
    treename = ""
    if options.tool == "combine": treename = "tree_fit_sb"
    elif options.tool == "lands": treename = "T"    
    t1 = f1.Get(treename)
    t2 = f2.Get(treename)

    nt1 = t1.GetEntries()
    nt2 = t2.GetEntries()

    if nt1 != nt2: 
        print "mismatch in number of entries!"
        return
    else:
        for i in range(nt1):
            t1.GetEntry(i)
            t2.GetEntry(i)
            
            nll1 = 0.; nll2 = 0.;
            if options.tool == "combine":
                nll1 = t1.nll_min
                nll2 = t2.nll_min
            elif options.tool == "lands":
                nll1 = t1.limit
                nll2 = t2.limit
        
            Sestimator = -2.0*(nll1 - nll2)
            h.Fill( Sestimator )

    return h

def getSestimatorList( fit1, fit2, hname ):
        
    list = []
    
    print fit1,",",fit2
    f1 = ROOT.TFile(fit1)
    f2 = ROOT.TFile(fit2)
    treename = ""
    if options.tool == "combine": treename = "tree_fit_sb"
    elif options.tool == "lands": treename = "T"    
    t1 = f1.Get(treename)
    t2 = f2.Get(treename)
    
    nt1 = t1.GetEntries()
    nt2 = t2.GetEntries()
    
    if nt1 != nt2: 
        print "mismatch in number of entries!"
        return
    else:
        for i in range(nt1):
            t1.GetEntry(i)
            t2.GetEntry(i)
            
            nll1 = 0.; nll2 = 0.;
            if options.tool == "combine":
                nll1 = t1.nll_min
                nll2 = t2.nll_min
            elif options.tool == "lands":
                nll1 = t1.limit
                nll2 = t2.limit
            
            Sestimator = -2.0*(nll1 - nll2)
            list.append( Sestimator )
    
    return list

## --------------

def getSignificanceAndMu( fit1, hname ):

    h = ROOT.TH1F( hname+"_sig",";sigma = sqrt[ 2*ln(L1/L2) ]; count",50,0,10 )
    hb = ROOT.TH1F( hname+"_musb","; #mu_b; count",30,0,5 )
    hsb = ROOT.TH1F( hname+"_mub","; #mu_sb; count",30,0,5 )

    f1 = ROOT.TFile(fit1)
    t1 = f1.Get("tree_fit_sb")
    t2 = f1.Get("tree_fit_b")

    nt1 = t1.GetEntries()
    nt2 = t2.GetEntries()
    
    if nt1 != nt2: 
        print "mismatch in number of entries!"
        return
    else:
        for i in range(nt1):
            t1.GetEntry(i)
            t2.GetEntry(i)
            
            nll1 = t1.nll_min
            nll2 = t2.nll_min
            

            sig_2 = 2*(-nll1 + nll2)
            sigma = 0.
            if sig_2 < 0: sigma = math.sqrt( -sig_2 )
            else: sigma = math.sqrt( sig_2 )
            
            h.Fill( sigma )
            hb.Fill( t2.mu )
            hsb.Fill( t1.mu )
    
    histos = [h,hsb,hb]
    return histos

## --------------

def submitToPBS( cmd, seed, toyN, oname, outputDir ):
    
    file = open("submitToPBS_tpl.csh.pbs")

    prefix="q"
    if cmd.find("saveToys") >= 0 or cmd.find("bWriteToys") >= 0: prefix = "gen"
    if cmd.find("toysFile") >= 0: prefix = "fit"
    pbsname = outputDir+"/"+prefix+"_submitToPBS_"+str(seed)+"_"+str(toyN)+".csh.pbs"
    fout = open(pbsname,'w')

    acmd = cmd.split()
    print acmd[2]
    doRemove = False
    if cmd.find("MaxLikelihoodFit") >= 0: doRemove = True
    # replace the tpl file with the right command, directories
    for line in file:
        curline0 = line
        curline1 = curline0.replace("CMSSWBASE",m_cmssw_base)
        curline2 = curline1.replace("WORKDIR",m_curdir).strip()
        curline3 = curline2.replace("COMMAND",cmd).strip()        
        curline4 = curline3.replace("ONAME",oname).strip()        
        curline5 = curline4.replace("ODIR",outputDir).strip()   
        curline = curline5
        if options.tool == "lands" and doRemove: curline = curline5.replace("###REMOVE###","rm "+acmd[2])
        print >> fout,curline

    # then submit!
    print "submitting to PBS ... "    
#    pbsCmd = "qsub -v "+"InputDir="+m_curdir+"/"+outputDir+" "+pbsname
    fout.close()
    pbsCmd = "qsub -v InputDir="+m_curdir+"/"+outputDir+" "+pbsname
    print pbsCmd
    os.system( pbsCmd )

## --------------

def submitToPBS_lands( cmd, seed, toyN, oname, outputDir ):
    
    file = open("submitToPBS_tpl.csh.pbs")
    
    prefix="fit"
    pbsname = outputDir+"/"+prefix+"_submitToPBS_"+str(seed)+"_"+str(toyN)+".csh.pbs"
    fout = open(pbsname,'w')
    
    # replace the tpl file with the right command, directories
    for line in file:
        
        if line.find("COMMAND") >= 0:
            for kk in range(len(cmd)): print >> fout, cmd[kk].strip()
        elif line.find("mv ONAME ODIR/ONAME") >= 0:
            for kk in range(len(cmd)): print >> fout, "mv "+oname[kk]+" "+outputDir+"/."
        elif line.find("###REMOVE###") >= 0:
            for kk in range(len(cmd)): 
                acmd = cmd[kk].split()
                print acmd[2]
                print >> fout, "rm "+acmd[2].strip()
        else:
            curline0 = line
            curline1 = curline0.replace("CMSSWBASE",m_cmssw_base)
            curline2 = curline1.replace("WORKDIR",m_curdir).strip()
            curline = curline2
            print >> fout,curline
    
    # then submit!
    print "submitting LandS to PBS ... "    
    #    pbsCmd = "qsub -v "+"InputDir="+m_curdir+"/"+outputDir+" "+pbsname
    fout.close()
    pbsCmd = "qsub -v InputDir="+m_curdir+"/"+outputDir+" "+pbsname
    print pbsCmd
    os.system( pbsCmd )

## --------------

def submitToLXB( cmd, seed, toyN, oname, outputDir ,stemDir ):
    
    file = open("submitToLXB_tpl.sh")

    prefix="q"
    if cmd.find("saveToys") >= 0 or cmd.find("bWriteToys") >= 0: prefix = "gen"
    if cmd.find("toysFile") >= 0: prefix = "fit"
    pbsname = outputDir+"/"+prefix+"_submitToLXB_"+str(seed)+"_"+str(toyN)+".sh"
    fout = open(pbsname,'w')

    acmd = cmd.split()
    print acmd[2]
    doRemove = False
    if cmd.find("MaxLikelihoodFit") >= 0: doRemove = True
    # replace the tpl file with the right command, directories
    for line in file:
        curline0 = line
        curline1 = curline0.replace("CMSSWBASE",m_cmssw_base)
        curline2 = curline1.replace("WORKDIR",m_curdir).strip()
        curline3 = curline2.replace("COMMAND",cmd).strip()        
        curline4 = curline3.replace("ONAME",oname).strip()        
        curline5 = curline4.replace("ODIR",outputDir).strip()   
        curline = curline5
        if options.tool == "lands" and doRemove: curline = curline5.replace("###REMOVE###","rm "+acmd[2])
        print >> fout,curline

    # then submit!
    print "submitting to LXBatch ... "    
    fout.close()
    os.system( "chmod u+x "+m_curdir+"/"+pbsname )
    pbsCmd = "bsub -q 1nh -J "+ str(seed)+"_"+str(toyN) +" "+ m_curdir+"/"+pbsname +" "+stemDir+" "+m_curdir+"/"+outputDir
    print "The submission command is "+pbsCmd
    os.system( pbsCmd )

## --------------

def submitToLXB_lands( cmd, seed, toyN, oname, outputDir ,stemDir):
    
    file = open("submitToLXB_tpl.sh")
    
    prefix="fit"
    pbsname = outputDir+"/"+prefix+"_submitToLXB_"+str(seed)+"_"+str(toyN)+".sh"
    fout = open(pbsname,'w')
    
    # replace the tpl file with the right command, directories
    for line in file:
        
        if line.find("COMMAND") >= 0:
            for kk in range(len(cmd)): print >> fout, cmd[kk].strip()
        elif line.find("cp ONAME ODIR/ONAME") >= 0:
            for kk in range(len(cmd)): print >> fout, "cp "+oname[kk]+" "+outputDir+"/."
        elif line.find("mv ONAME ${workdir}/ODIR/ONAME") >= 0:
            for kk in range(len(cmd)): print >> fout, "mv "+oname[kk]+" ${workdir}/"+outputDir+"/."
        elif line.find("mv ONAME ${workdir}/ODIR/ONAME") >= 0:
            for kk in range(len(cmd)): print >> fout, "mv "+oname[kk]+" ${workdir}/"+outputDir+"/."
        elif line.find("if [ ! -f ${workdir}/ODIR/ONAME ]") >=0 :
       #     for kk in range(len(cmd)):
             print >> fout, "if [ ! -f ${workdir}/ "+outputDir+"/"+oname[kk]+" ]"
        elif line.find("###REMOVE###") >= 0:
            for kk in range(len(cmd)): 
                acmd = cmd[kk].split()
                print acmd[2]
                print >> fout, "rm "+acmd[2].strip()
        else:
            curline0 = line
            curline1 = curline0.replace("CMSSWBASE",m_cmssw_base)
            curline2 = curline1.replace("WORKDIR",m_curdir).strip()
            curline = curline2
            print >> fout,curline
    
    # then submit!
    print "submitting LandS to LXBatch ... "    
    #    pbsCmd = "qsub -v "+"InputDir="+m_curdir+"/"+outputDir+" "+pbsname
    fout.close()
    os.system( "chmod u+x "+m_curdir+"/"+pbsname )
    pbsCmd = "bsub -q 1nh -J "+ str(seed)+"_"+str(toyN) +" "+ m_curdir+"/"+pbsname +" "+stemDir+" "+m_curdir+"/"+outputDir
    print "The submission command is "+pbsCmd
    os.system( pbsCmd )


## --------------

def makeDCcopy_lands(dc_model1_copy, dc_model1, toys, name1, seed1):
#    print "makeDCcopy_lands with arguments ",dc_model1_copy," ",dc_model1,
    file = open( dc_model1 )
    filenew = open( dc_model1_copy, 'w' )
    previousline = ""
    for line in file:
        if previousline.find("--------") >= 0 and line.find("shapes") >= 0:
            print >> filenew, "shapes data_obs * "+outputDir+"/"+name1+"_PseudoData_sb_seed"+str(seed1)+".root w:$CHANNEL_sbData_"+str(jj)
            print >> filenew, line.strip()
        elif line.find("observation") >= 0:
            splitline = line.split()
            newline = "observation"
            for kk in range(len(splitline)-1): newline = newline + " -1.0"
#            print newline
            print >> filenew, newline
        else:
            print >> filenew, line.strip()
        
        previousline = line    
    file.close()
    filenew.close()

###########################################################
## M A I N   M A I N   M A I N   M A I N   M A I N
###########################################################

if __name__ == '__main__':

    parallelizeToys = options.multiJob
    generateToys = options.generateToys
    runFits = options.fitToys
    addFiles = options.addOutput
    doPlots = options.plotResults
    
    ## ----------------------------------------------------------------------------------
    ## parameters              
    outputDir=options.outputDir
#    dc_model1="SignalSeparation_SM_7p8TeV/datacards/hzz4l_4lS.126.0_7p8TeV.txt"
#    dc_model2="SignalSeparation_PS_7p8TeV/datacards/hzz4l_4lS.126.0_7p8TeV.txt"
    dc_model1=options.card1
    dc_model2=options.card2

    m0=dc_model1.find("/")
    c1a=dc_model1[:m0]
    m1=dc_model1.rfind("/")
    c1b=dc_model1[m0:m1:]
    c1c=dc_model1[m1+1:]
    dc_stem1=c1a
    dc_dir1=c1a+"/"+c1b
    dc_card1=c1c
    
    m0=dc_model2.find("/")
    c2a=dc_model2[:m0]
    m1=dc_model2.rfind("/")
    c2b=dc_model2[m0:m1:]
    c2c=dc_model2[m1+1:]
    dc_stem2=c2a
    dc_dir2=c2a+"/"+c2b
    dc_card2=c2c
    
    mass=126
    toys=options.toysPerJob
    name1="_testSM"
    name2="_testPS"
    seed=options.seed
    nParallelJobs=options.nParallelJobs
    
    if parallelizeToys: print "Running in parallel mode with",toys,"toys per job for",nParallelJobs,"parallel jobs..."
    else: print "Running in serial mode, it might take a while..."
    print "card1: ",options.card1
    print "card2: ",options.card2    
    print "Output directory is: ",outputDir
    if generateToys: print "Generating toys..."
    if runFits: print "Running fits on toys..."
    if doPlots: print "Plot the good stuff..."

    if os.path.isfile(options.card1) == False :
        raise SystemExit( "Card 1 does not exist!  Exiting..." )
    if  os.path.isfile(options.card2) == False :
        raise SystemExit( "Card 2 does not exist!  Exiting..." )
    if os.path.exists(outputDir) == False :
        raise SystemExit( "Output directory does not exist!  Exiting..." )
    
    ## ----------------------------------------------------------------------------------

    ## ----------------------------------------------------------------------------------
    ## generate toys              

    if generateToys:
        
        if not parallelizeToys:

            if options.tool == "combine":
                i = 0
                seed1 = seed+((i*2)-1)
                seed2 = seed+(i*2)
                
                generateCmd1 = "combine --verbose 2 -M GenerateOnly -n \""+name1+"\" -d "+dc_model1+" -t "+str(toys)+" --expectSignal=0 --saveToys -m "+str(mass)+" --seed "+str(seed1)
                print generateCmd1
                generateCmd2 = "combine --verbose 2 -M GenerateOnly -n \""+name2+"\" -d "+dc_model2+" -t "+str(toys)+" --expectSignal=0 --saveToys -m "+str(mass)+" --seed "+str(seed2)
                print generateCmd2
                
                oname1 = "higgsCombine"+name1+".GenerateOnly.mH"+str(mass)+"."+str(seed1)+".root"
                oname2 = "higgsCombine"+name2+".GenerateOnly.mH"+str(mass)+"."+str(seed2)+".root"            

                os.system(generateCmd1)
                # move output file
                os.system("mv "+oname1+" "+outputDir+"/.")
                oname1 = outputDir+"/"+oname1
                
                os.system(generateCmd2)
                # move output file
                os.system("mv "+oname2+" "+outputDir+"/.")
                oname2 = outputDir+"/"+oname2

                print "------------------------------"
                print "generated file 1: "+oname1
                print "generated file 2: "+oname2
            
            elif options.tool == "lands":
                i = 0
                seed1 = seed+((i*2)-1)
                seed2 = seed+(i*2)
                                
#                generateCmd1 = "lands.exe -d "+dc_model1+" -M Hybrid --freq -m "+str(mass)+" --rMin 0 --rMax 3 --minuitSTRATEGY 0 --bMultiSigProcShareSamePDF -L $CMSSW_BASE/lib/*/libHiggsAnalysisCombinedLimit.so --GenerateToysAtBestFitSB --bWriteToys 1 -n \""+name1+"\" -tH "+str(toys)+" --seed "+str(seed1)
                generateCmd1 = "lands.exe -d "+dc_model1+" -M Hybrid --freq -m "+str(mass)+" --minuitSTRATEGY 0 --bMultiSigProcShareSamePDF -L $CMSSW_BASE/lib/*/libHiggsAnalysisCombinedLimit.so --bWriteToys 1 -n \""+name1+"\" --nToysForCLsb "+str(toys)+" --nToysForCLb 1 --singlePoint 1 --seed "+str(seed1)

                print generateCmd1
#                generateCmd2 = "lands.exe -d "+dc_model2+" -M Hybrid --freq -m "+str(mass)+" -rMin 0 -rMax 3 --minuitSTRATEGY 0 --bMultiSigProcShareSamePDF -L $CMSSW_BASE/lib/*/libHiggsAnalysisCombinedLimit.so --GenerateToysAtBestFitSB --bWriteToys 1 -n \""+name2+"\" -tH "+str(toys)+" --seed "+str(seed2)
                generateCmd2 = "lands.exe -d "+dc_model2+" -M Hybrid --freq -m "+str(mass)+" --minuitSTRATEGY 0 --bMultiSigProcShareSamePDF -L $CMSSW_BASE/lib/*/libHiggsAnalysisCombinedLimit.so --bWriteToys 1 -n \""+name2+"\" --nToysForCLsb "+str(toys)+" --nToysForCLb 1 --singlePoint 1 --seed "+str(seed2)
                print generateCmd2

                os.system(generateCmd1)
                os.system(generateCmd2)
        
                os.system("mv "+name1+"_PseudoData_sb_seed"+str(seed1)+".root "+outputDir+"/.")
                os.system("mv "+name2+"_PseudoData_sb_seed"+str(seed2)+".root "+outputDir+"/.")
                os.system("rm "+name1+"_PseudoData_b_seed"+str(seed1)+".root "+outputDir+"/.")
                os.system("rm "+name2+"_PseudoData_b_seed"+str(seed2)+".root "+outputDir+"/.")
        
            else: 
                print "Wrong tool!"
    
        else:
                
            if options.tool == "combine":

                for i in range(nParallelJobs):
                    
                    seed1 = seed+((i*2)-1)
                    seed2 = seed+(i*2)
                    
                    generateCmd1 = "combine -M GenerateOnly -n \""+name1+"\" -d "+dc_model1+" -t "+str(toys)+" --expectSignal=0 --saveToys -m "+str(mass)+" --seed "+str(seed1)
                    generateCmd2 = "combine -M GenerateOnly -n \""+name2+"\" -d "+dc_model2+" -t "+str(toys)+" --expectSignal=0 --saveToys -m "+str(mass)+" --seed "+str(seed2)
                    
                    oname1 = "higgsCombine"+name1+".GenerateOnly.mH"+str(mass)+"."+str(seed1)+".root"
                    oname2 = "higgsCombine"+name2+".GenerateOnly.mH"+str(mass)+"."+str(seed2)+".root"            
                    
                    print "i: ",i
                    submitToLXB( generateCmd1, seed1, i, oname1, outputDir,dc_stem1 )
                    submitToLXB( generateCmd2, seed2, i, oname2, outputDir,dc_stem2 )

            elif options.tool == "lands":

                for i in range(nParallelJobs):

                    seed1 = seed+((i*2)-1)
                    seed2 = seed+(i*2)
                    
                    generateCmd1 = "lands.exe -d "+dc_model1+" -M Hybrid --freq -m "+str(mass)+" --minuitSTRATEGY 0 --bMultiSigProcShareSamePDF -L $CMSSW_BASE/lib/*/libHiggsAnalysisCombinedLimit.so --bWriteToys 1 -n \""+name1+"\" --nToysForCLsb "+str(toys)+" --nToysForCLb 1 --singlePoint 1 --seed "+str(seed1)+" -v 2"
                    generateCmd2 = "lands.exe -d "+dc_model2+" -M Hybrid --freq -m "+str(mass)+" --minuitSTRATEGY 0 --bMultiSigProcShareSamePDF -L $CMSSW_BASE/lib/*/libHiggsAnalysisCombinedLimit.so --bWriteToys 1 -n \""+name2+"\" --nToysForCLsb "+str(toys)+" --nToysForCLb 1 --singlePoint 1 --seed "+str(seed2)+" -v 2"
                    
                    oname1 = name1+"_PseudoData_sb_seed"+str(seed1)+".root"
                    oname2 = name2+"_PseudoData_sb_seed"+str(seed2)+".root"            
                    
                    print "i: ",i
                    submitToLXB( generateCmd1, seed1, i, oname1, outputDir,dc_stem1 )
                    submitToLXB( generateCmd2, seed2, i, oname2, outputDir,dc_stem2 )
                    
            else: 
                print "Wrong tool!"


    ## ----------------------------------------------------------------------------------
    ## run fits
    
    if runFits:

        if not parallelizeToys:
            
            if options.tool == "combine":
                
                i = 0
                seeda = seed+((i*4)-3)
                seedb = seed+((i*4)-2)
                seedc = seed+((i*4)-1)
                seedd = seed+(i*4)   
                seed1 = seed+((i*2)-1)
                seed2 = seed+(i*2)
                
                oname1 = outputDir+"/"+"higgsCombine"+name1+".GenerateOnly.mH"+str(mass)+"."+str(seed1)+".root"
                oname2 = outputDir+"/"+"higgsCombine"+name2+".GenerateOnly.mH"+str(mass)+"."+str(seed2)+".root"   
                
                fitCmd11 = "combine -M MaxLikelihoodFit -n \""+name1+"_fit"+name1+"_"+str(seeda)+"\" -d "+dc_model1+" -t "+str(toys)+" --toysFile \""+oname1+"\" -m "+str(mass)+" --seed "+str(seeda)+" --out "+outputDir
                fitCmd12 = "combine -M MaxLikelihoodFit -n \""+name1+"_fit"+name2+"_"+str(seedb)+"\" -d "+dc_model2+" -t "+str(toys)+" --toysFile \""+oname1+"\" -m "+str(mass)+" --seed "+str(seedb)+" --out "+outputDir
                fitCmd21 = "combine -M MaxLikelihoodFit -n \""+name2+"_fit"+name1+"_"+str(seedc)+"\" -d "+dc_model1+" -t "+str(toys)+" --toysFile \""+oname2+"\" -m "+str(mass)+" --seed "+str(seedc)+" --out "+outputDir
                fitCmd22 = "combine -M MaxLikelihoodFit -n \""+name2+"_fit"+name2+"_"+str(seedd)+"\" -d "+dc_model2+" -t "+str(toys)+" --toysFile \""+oname2+"\" -m "+str(mass)+" --seed "+str(seedd)+" --out "+outputDir
                
                fitname11 = "higgsCombine"+name1+"_fit"+name1+"_"+str(seeda)+".MaxLikelihoodFit.mH"+str(mass)+"."+str(seeda)+".root"
                fitname12 = "higgsCombine"+name1+"_fit"+name2+"_"+str(seedb)+".MaxLikelihoodFit.mH"+str(mass)+"."+str(seedb)+".root"
                fitname21 = "higgsCombine"+name2+"_fit"+name1+"_"+str(seedc)+".MaxLikelihoodFit.mH"+str(mass)+"."+str(seedc)+".root"
                fitname22 = "higgsCombine"+name2+"_fit"+name2+"_"+str(seedd)+".MaxLikelihoodFit.mH"+str(mass)+"."+str(seedd)+".root"

                os.system(fitCmd11)
                os.system(fitCmd12)
                os.system(fitCmd21)
                os.system(fitCmd22)

                os.system("mv "+fitname11+" "+outputDir+"/.")
                os.system("mv "+fitname12+" "+outputDir+"/.")
                os.system("mv "+fitname21+" "+outputDir+"/.")
                os.system("mv "+fitname22+" "+outputDir+"/.")
            
            elif options.tool == "lands":
                
                i = 0
                seeda = seed+((i*4)-3)
                seedb = seed+((i*4)-2)
                seedc = seed+((i*4)-1)
                seedd = seed+(i*4)   
                seed1 = seed+((i*2)-1)
                seed2 = seed+(i*2)
                
                for jj in range(toys):
                    
                    dc_model11_copy = dc_model1+".copy_"+name1+"_"+str(seed1)+"_"+str(jj)+".txt"
                    dc_model12_copy = dc_model1+".copy_"+name2+"_"+str(seed2)+"_"+str(jj)+".txt"
                    dc_model21_copy = dc_model2+".copy_"+name1+"_"+str(seed1)+"_"+str(jj)+".txt"
                    dc_model22_copy = dc_model2+".copy_"+name2+"_"+str(seed2)+"_"+str(jj)+".txt"
                    
    #                os.system("cp "+dc_model1+" "+dc_model1_copy)
                    print "Preparing card ",str(jj)            
                    makeDCcopy_lands( dc_model11_copy, dc_model1, toys, name1, seed1 )
                    makeDCcopy_lands( dc_model12_copy, dc_model1, toys, name2, seed2 )
                    makeDCcopy_lands( dc_model21_copy, dc_model2, toys, name1, seed1 )
                    makeDCcopy_lands( dc_model22_copy, dc_model2, toys, name2, seed2 )
                    
                    fitCmd11 = "lands.exe -d "+dc_model11_copy+" -M MaxLikelihoodFit -m "+str(mass)+" --NoErrorEstimate --rMin 0 --rMax 5 --minuitSTRATEGY 0 --bMultiSigProcShareSamePDF -L $CMSSW_BASE/lib/*/libHiggsAnalysisCombinedLimit.so -n \""+name1+name1+"_"+str(seeda)+"_"+str(jj)+"\""
                    fitCmd12 = "lands.exe -d "+dc_model12_copy+" -M MaxLikelihoodFit -m "+str(mass)+" --NoErrorEstimate --rMin 0 --rMax 5 --minuitSTRATEGY 0 --bMultiSigProcShareSamePDF -L $CMSSW_BASE/lib/*/libHiggsAnalysisCombinedLimit.so -n \""+name1+name2+"_"+str(seedb)+"_"+str(jj)+"\""
                    fitCmd21 = "lands.exe -d "+dc_model21_copy+" -M MaxLikelihoodFit -m "+str(mass)+" --NoErrorEstimate --rMin 0 --rMax 5 --minuitSTRATEGY 0 --bMultiSigProcShareSamePDF -L $CMSSW_BASE/lib/*/libHiggsAnalysisCombinedLimit.so -n \""+name2+name1+"_"+str(seedc)+"_"+str(jj)+"\""
                    fitCmd22 = "lands.exe -d "+dc_model22_copy+" -M MaxLikelihoodFit -m "+str(mass)+" --NoErrorEstimate --rMin 0 --rMax 5 --minuitSTRATEGY 0 --bMultiSigProcShareSamePDF -L $CMSSW_BASE/lib/*/libHiggsAnalysisCombinedLimit.so -n \""+name2+name2+"_"+str(seedd)+"_"+str(jj)+"\""

                    print "LandS command : ",fitCmd11
                    
                    os.system( fitCmd11 )                    
                    os.system( fitCmd12 )                    
                    os.system( fitCmd21 )
                    os.system( fitCmd22 )
                    # Run fit
                    os.system("rm "+dc_model11_copy+" "+dc_model12_copy+" "+dc_model21_copy+" "+dc_model22_copy)
                    os.system("mv "+name1+name1+"_"+str(seeda)+"_"+str(jj)+"_maxllfit.root "+outputDir+"/.")
                    os.system("mv "+name1+name2+"_"+str(seedb)+"_"+str(jj)+"_maxllfit.root "+outputDir+"/.")
                    os.system("mv "+name2+name1+"_"+str(seedc)+"_"+str(jj)+"_maxllfit.root "+outputDir+"/.")
                    os.system("mv "+name2+name2+"_"+str(seedd)+"_"+str(jj)+"_maxllfit.root "+outputDir+"/.")                        

            else: 
                print "wrong tool!"
    
        else:
            
            if options.tool == "combine":

                for i in range(nParallelJobs):
                    
                    seeda = seed+((i*4)-3)
                    seedb = seed+((i*4)-2)
                    seedc = seed+((i*4)-1)
                    seedd = seed+(i*4)                
                    seed1 = seed+((i*2)-1)
                    seed2 = seed+(i*2)
                    
                    oname1 = outputDir+"/"+"higgsCombine"+name1+".GenerateOnly.mH"+str(mass)+"."+str(seed1)+".root"
                    oname2 = outputDir+"/"+"higgsCombine"+name2+".GenerateOnly.mH"+str(mass)+"."+str(seed2)+".root"   
                    
                    fitCmd11 = "combine -M MaxLikelihoodFit -n \""+name1+"_fit"+name1+"_"+str(seeda)+"\" -d "+dc_model1+" -t "+str(toys)+" --toysFile \""+oname1+"\" -m "+str(mass)+" --seed "+str(seeda)+" --out "+outputDir
                    fitCmd12 = "combine -M MaxLikelihoodFit -n \""+name1+"_fit"+name2+"_"+str(seedb)+"\" -d "+dc_model2+" -t "+str(toys)+" --toysFile \""+oname1+"\" -m "+str(mass)+" --seed "+str(seedb)+" --out "+outputDir
                    fitCmd21 = "combine -M MaxLikelihoodFit -n \""+name2+"_fit"+name1+"_"+str(seedc)+"\" -d "+dc_model1+" -t "+str(toys)+" --toysFile \""+oname2+"\" -m "+str(mass)+" --seed "+str(seedc)+" --out "+outputDir
                    fitCmd22 = "combine -M MaxLikelihoodFit -n \""+name2+"_fit"+name2+"_"+str(seedd)+"\" -d "+dc_model2+" -t "+str(toys)+" --toysFile \""+oname2+"\" -m "+str(mass)+" --seed "+str(seedd)+" --out "+outputDir

                    fitname11 = "higgsCombine"+name1+"_fit"+name1+"_"+str(seeda)+".MaxLikelihoodFit.mH"+str(mass)+"."+str(seeda)+".root"
                    fitname12 = "higgsCombine"+name1+"_fit"+name2+"_"+str(seedb)+".MaxLikelihoodFit.mH"+str(mass)+"."+str(seedb)+".root"
                    fitname21 = "higgsCombine"+name2+"_fit"+name1+"_"+str(seedc)+".MaxLikelihoodFit.mH"+str(mass)+"."+str(seedc)+".root"
                    fitname22 = "higgsCombine"+name2+"_fit"+name2+"_"+str(seedd)+".MaxLikelihoodFit.mH"+str(mass)+"."+str(seedd)+".root"
                    
                    submitToLXB( fitCmd11, seeda, i, fitname11, outputDir,dc_stem1 )
                    submitToLXB( fitCmd12, seedb, i, fitname12, outputDir,dc_stem1 )
                    submitToLXB( fitCmd21, seedc, i, fitname21, outputDir,dc_stem2 )
                    submitToLXB( fitCmd22, seedd, i, fitname22, outputDir,dc_stem2 )

            elif options.tool == "lands":

                for i in range(nParallelJobs):
                    
                    seeda = seed+((i*4)-3)
                    seedb = seed+((i*4)-2)
                    seedc = seed+((i*4)-1)
                    seedd = seed+(i*4)   
                    seed1 = seed+((i*2)-1)
                    seed2 = seed+(i*2)
                    
                    list_fitCmd11 = []; list_fitname11 = [];
                    list_fitCmd12 = []; list_fitname12 = [];
                    list_fitCmd21 = []; list_fitname21 = [];
                    list_fitCmd22 = []; list_fitname22 = [];
                    list_seeda = []; list_seedb = []; list_seedc = []; list_seedd = [];
                    
                    for jj in range(toys):
                        
                        dc_model11_copy = dc_model1+".copy_"+name1+"_"+str(seed1)+"_"+str(jj)+".txt"
                        dc_model12_copy = dc_model1+".copy_"+name2+"_"+str(seed2)+"_"+str(jj)+".txt"
                        dc_model21_copy = dc_model2+".copy_"+name1+"_"+str(seed1)+"_"+str(jj)+".txt"
                        dc_model22_copy = dc_model2+".copy_"+name2+"_"+str(seed2)+"_"+str(jj)+".txt"
                        
                        #                os.system("cp "+dc_model1+" "+dc_model1_copy)
                        
                        makeDCcopy_lands( dc_model11_copy, dc_model1, toys, name1, seed1 )
                        makeDCcopy_lands( dc_model12_copy, dc_model1, toys, name2, seed2 )
                        makeDCcopy_lands( dc_model21_copy, dc_model2, toys, name1, seed1 )
                        makeDCcopy_lands( dc_model22_copy, dc_model2, toys, name2, seed2 )
                        
                        fitCmd11 = "lands.exe -d "+dc_model11_copy+" -M MaxLikelihoodFit -m "+str(mass)+" --NoErrorEstimate --rMin 0 --rMax 5 --minuitSTRATEGY 0 --bMultiSigProcShareSamePDF -L $CMSSW_BASE/lib/*/libHiggsAnalysisCombinedLimit.so -n \""+name1+name1+"_"+str(seeda)+"_"+str(jj)+"\""
                        fitCmd12 = "lands.exe -d "+dc_model12_copy+" -M MaxLikelihoodFit -m "+str(mass)+" --NoErrorEstimate --rMin 0 --rMax 5 --minuitSTRATEGY 0 --bMultiSigProcShareSamePDF -L $CMSSW_BASE/lib/*/libHiggsAnalysisCombinedLimit.so -n \""+name1+name2+"_"+str(seedb)+"_"+str(jj)+"\""
                        fitCmd21 = "lands.exe -d "+dc_model21_copy+" -M MaxLikelihoodFit -m "+str(mass)+" --NoErrorEstimate --rMin 0 --rMax 5 --minuitSTRATEGY 0 --bMultiSigProcShareSamePDF -L $CMSSW_BASE/lib/*/libHiggsAnalysisCombinedLimit.so -n \""+name2+name1+"_"+str(seedc)+"_"+str(jj)+"\""
                        fitCmd22 = "lands.exe -d "+dc_model22_copy+" -M MaxLikelihoodFit -m "+str(mass)+" --NoErrorEstimate --rMin 0 --rMax 5 --minuitSTRATEGY 0 --bMultiSigProcShareSamePDF -L $CMSSW_BASE/lib/*/libHiggsAnalysisCombinedLimit.so -n \""+name2+name2+"_"+str(seedd)+"_"+str(jj)+"\""

                        list_fitCmd11.append(fitCmd11)
                        list_fitCmd12.append(fitCmd12)
                        list_fitCmd21.append(fitCmd21)
                        list_fitCmd22.append(fitCmd22)
                                    
                        list_fitname11.append(name1+name1+"_"+str(seeda)+"_"+str(jj)+"_maxllfit.root")
                        list_fitname12.append(name1+name2+"_"+str(seedb)+"_"+str(jj)+"_maxllfit.root")
                        list_fitname21.append(name2+name1+"_"+str(seedc)+"_"+str(jj)+"_maxllfit.root")
                        list_fitname22.append(name2+name2+"_"+str(seedd)+"_"+str(jj)+"_maxllfit.root")
                        
                    submitToLXB_lands( list_fitCmd11, seeda, i, list_fitname11, outputDir,dc_stem1 )
                    submitToLXB_lands( list_fitCmd12, seedb, i, list_fitname12, outputDir,dc_stem1 )
                    submitToLXB_lands( list_fitCmd21, seedc, i, list_fitname21, outputDir,dc_stem2 )
                    submitToLXB_lands( list_fitCmd22, seedd, i, list_fitname22, outputDir,dc_stem2 )

            else: 
                print "wrong tool!"                


    ## ----------------------------------------------------------------------------------
    ## do plots
    
    if doPlots:

        if addFiles:
            hcmd11 = ""; hcmd12 = ""; hcmd21 = ""; hcmd22 = "";
            if options.tool == "combine":
                hcmd11 = "hadd -f "+outputDir+"/"+"mlfit"+name1+"_fit"+name1+".root "+outputDir+"/"+"mlfit"+name1+"_fit"+name1+"_[0-9]*.root"
                hcmd12 = "hadd -f "+outputDir+"/"+"mlfit"+name2+"_fit"+name1+".root "+outputDir+"/"+"mlfit"+name2+"_fit"+name1+"_[0-9]*.root"
                hcmd21 = "hadd -f "+outputDir+"/"+"mlfit"+name1+"_fit"+name2+".root "+outputDir+"/"+"mlfit"+name1+"_fit"+name2+"_[0-9]*.root"
                hcmd22 = "hadd -f "+outputDir+"/"+"mlfit"+name2+"_fit"+name2+".root "+outputDir+"/"+"mlfit"+name2+"_fit"+name2+"_[0-9]*.root"            

                os.system( hcmd11 )
                os.system( hcmd12 )
                os.system( hcmd21 )
                os.system( hcmd22 )

            elif options.tool == "lands":
                
                haddLands( outputDir+"/"+name1+name1+"_maxllfit.root", name1+name1, -3 )
                haddLands( outputDir+"/"+name1+name2+"_maxllfit.root", name1+name2, -2 )
                haddLands( outputDir+"/"+name2+name1+"_maxllfit.root", name2+name1, -1 )
                haddLands( outputDir+"/"+name2+name2+"_maxllfit.root", name2+name2, 0 )                          

            else:
                print "Wrong tool!"        

        mlfitname11 = outputDir+"/"+"mlfit"+name1+"_fit"+name1+".root"
        mlfitname12 = outputDir+"/"+"mlfit"+name1+"_fit"+name2+".root"
        mlfitname21 = outputDir+"/"+"mlfit"+name2+"_fit"+name1+".root"
        mlfitname22 = outputDir+"/"+"mlfit"+name2+"_fit"+name2+".root"
        if options.tool == "lands":
            mlfitname11 = outputDir+"/"+name1+name1+"_maxllfit.root"
            mlfitname21 = outputDir+"/"+name1+name2+"_maxllfit.root"
            mlfitname12 = outputDir+"/"+name2+name1+"_maxllfit.root"
            mlfitname22 = outputDir+"/"+name2+name2+"_maxllfit.root"

        print mlfitname11,",",mlfitname12
        print mlfitname21,",",mlfitname22
        
        h1 = getSestimator( mlfitname11, mlfitname12, "h_SM" )
        h2 = getSestimator( mlfitname21, mlfitname22, "h_PS" )

        h1l = getSestimatorList( mlfitname11, mlfitname12, "h_SM" )
        h2l = getSestimatorList( mlfitname21, mlfitname22, "h_PS" )
        getSeparationStats( h1l, h2l );
    

        pt = ROOT.TPaveText(0.16,0.95,0.45,0.99,"NDC")
        pt.SetFillColor(0)
        pt.AddText("CMS Preliminary 2012")
        pt2 = ROOT.TPaveText(0.58,0.95,0.99,0.99,"NDC")
        pt2.SetFillColor(0)
        pt2.AddText(" #sqrt{s} = 7,8 TeV, L = 8.68 fb^{-1}")
        
        arrow1 = ROOT.TArrow(.26, 50, .26, 0 )
        arrow1.SetLineWidth( 7 )
        arrow1.SetLineColor( ROOT.kCyan )

        leg = ROOT.TLegend(0.2,0.6,0.45,0.9)
        leg.SetFillColor(0)
        leg.SetBorderSize(0)
        leg.AddEntry(h1,"  SM, 0+","f")
        leg.AddEntry(h2,"  PS, 0-","f")
        
        leg2 = ROOT.TLegend(0.65,0.7,0.95,0.9)
        leg2.SetFillColor(0)
        leg2.SetBorderSize(0)
        leg2.AddEntry(arrow,"CMS data","l");

        c = ROOT.TCanvas("c","c",800,800)
        h1.SetLineWidth(2)
        h1.SetLineColor( ROOT.kMagenta - 3 )
        h1.SetFillColor( ROOT.kMagenta - 3 )
        h1.SetFillStyle( 3605 )
        h2.SetLineWidth(2)

        h1.Draw()
        h2.SetLineColor( ROOT.kBlue + 1 )
        h2.SetFillColor( ROOT.kBlue + 1 )
        h2.SetFillStyle( 3695 )
        h2.Draw("sames")

        pt.Draw("same")
        pt2.Draw("same")
        
        if h1.GetMaximum() < h2.GetMaximum(): h1.SetMaximum( h2.GetMaximum() * 1.1 );
        leg.Draw()
        leg2.Draw()
        arrow.Draw()
        c.SaveAs("figs/sigsep.eps")
        c.SaveAs("figs/sigsep.root")

        print "h1: mean = ",h1.GetMean(),", RMS = ",h1.GetRMS()
        print "h2: mean = ",h2.GetMean(),", RMS = ",h2.GetRMS()

        #/////////
 #       norm0 = h2.Integral( 1, int(h2.GetEntries()) );
#        norm1 = h1.Integral( 1, int(h1.GetEntries()) );
        nBins = h2.GetNbinsX()
        norm0 = h2.Integral( 1, nBins );
        norm1 = h1.Integral( 1, nBins );
        print "Histo stats: ",h1.GetEntries(),", ",h2.GetEntries(),", ",norm0,", ",norm1,", ",nBins
        
        diff = 10.;
        coverage = 0.;
#        for (int i = 1; i <= nBins; i++){
        for i in range(1,nBins+1):    
            
            
            int0 = h2.Integral(1,i)/norm0;
            int1 = h1.Integral(i,nBins)/norm1;
            
#            print "At bin ",i," center ",h2.GetBinCenter(i)," partial Integral of signif histo2 is ",h2.Integral(1,i),"/",norm0,"=",int0
            
            if math.fabs(int0-int1) < diff:
                diff = math.fabs(int0-int1);
#                print "Old coverage is ",coverage
                coverage = 0.5*(int0+int1);
#                print "New coverage at ",h2.GetBinCenter(i)," is ",coverage,"   , ",int0," , ",int1," , ",diff

        sepH = 2*ROOT.Math.normal_quantile_c(1.0 - coverage, 1.0);
        print "histogram separation is ", sepH ," sigma with coverage: ", coverage
        #/////////

        if options.tool == "combine":

            histos = getSignificanceAndMu( mlfitname11, "h_smsm" )
            c0 = ROOT.TCanvas("c0","c0",800,800)
            histos[1].Draw()
    #        histos[2].SetLineStyle(2)
    #        histos[2].Draw("sames")
            c0.SaveAs("figs/mufit_sb.eps")
            c0.SaveAs("figs/mufit_sb.root")
            print "hsb: mean = ",histos[1].GetMean(),", RMS = ",histos[1].GetRMS()

            cS = ROOT.TCanvas("cS","cS",800,800)
            histos[0].Draw()
            cS.SaveAs("figs/signif.eps")
            cS.SaveAs("figs/signif.root")

            print "hsb: mean = ",histos[0].GetMean(),", RMS = ",histos[0].GetRMS()

        elif options.tool == "lands":
            
            fin = ROOT.TFile(mlfitname11)
            tin = fin.Get("T")
            nt1 = tin.GetEntries()
            hmu = ROOT.TH1F("hmu","hmu",40,0,2.5)
            x = []
            for i in range(nt1):
                tin.GetEntry(i)
                hmu.Fill(tin.rmean)
                x.append( tin.rmean )

            c0 = ROOT.TCanvas("c0","c0",800,800)
            hmu.Draw()
            c0.SaveAs("figs/mufit_lands.eps")
            c0.SaveAs("figs/mufit_lands.root")
            print "hmu: median = ",sorted(x)[len(x)/2]
            print "hmu: RMS = ",hmu.GetRMS()



