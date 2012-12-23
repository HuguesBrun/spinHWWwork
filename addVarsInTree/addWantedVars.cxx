#include "TTree.h"
#include "TFile.h"
#include "TStopwatch.h"
#include "TSystem.h"
#include <cstdlib>
#include <cmath>
#include "mt2_bisect.h"
#include "mt2_bisect.cpp"



void addWantedVars(TString outname){
    using namespace std;
    
    ///// input tree definition 
    TTree *tIn  = (TTree *) gFile->Get("latino");
    float mtw1, mtw2, pt1, pt2, phi1, phi2, pfmet, pfmetphi, channel;
    tIn->SetBranchAddress("mtw1",&mtw1);
    tIn->SetBranchAddress("mtw2",&mtw2);
    tIn->SetBranchAddress("pt1",&pt1);
    tIn->SetBranchAddress("pt2",&pt2);
    tIn->SetBranchAddress("phi1",&phi1);
    tIn->SetBranchAddress("phi2",&phi2);
    tIn->SetBranchAddress("pfmet",&pfmet);
    tIn->SetBranchAddress("pfmetphi",&pfmetphi);
    tIn->SetBranchAddress("channel",&channel);
    
    
    // output file and tree
    TFile *fOut = new TFile(outname,"RECREATE");
    TTree *tOut = tIn->CloneTree(0);
    float mtAsym, mt2, diffMW1MT2, diffMW2MT2;
    tOut->Branch("mtAsym",&mtAsym,"mtAsym/F");
    tOut->Branch("mt2",&mt2,"mt2/F");
    tOut->Branch("diffMW1MT2",&diffMW1MT2,"diffMW1MT2/F");
    tOut->Branch("diffMW2MT2",&diffMW2MT2,"diffMW2MT2/F");
    
    
    float px1, py1, px2, py2, pmiss1, pmiss2;
    double pa[3];
    double pb[3];
    double pmiss[3];
    double mn    = 10.;
    
    for (int i = 0, n = tIn->GetEntries(); i < n; ++i) {
    //for (int i = 0, n = 20; i < n; ++i) {
        tIn->GetEntry(i);
        if ((mtw1+mtw2)>0) {
            mtAsym = (mtw1-mtw2)/(mtw1+mtw2);
        }
        else mtAsym = -1;
        px1 = pt1*cos(phi1);
        py1 = pt1*sin(phi1);
        px2 = pt2*cos(phi2);
        py2 = pt2*sin(phi2);
        pmiss1 = pfmet*cos(pfmetphi);
        pmiss2 = pfmet*sin(pfmetphi);
        
        int theChannel = (int) channel;
        
        switch (theChannel) {
            case 0:
                pa[0] = 0.1;
                pb[0] = 0.1;
                break;
            case 1:
                pa[0] = 0.0005;
                pb[0] = 0.0005;
                break;
            case 2:
                pa[0] = 0.0005;
                pb[0] = 0.1;
                break;
            case 3:
                pa[0] = 0.1;
                pb[0] = 0.0005;
                break;
        }
        
        pa[1] = px1;
        pa[2] = py1;
        
        pb[1] = px2;
        pb[2] = py2;
        
        pmiss[0] = 0;
        pmiss[1] = pmiss1;
        pmiss[2] = pmiss2;
        
        mt2_bisect::mt2 mt2_event;

        
        mt2_event.set_momenta(pa,pb,pmiss);
        mt2_event.set_mn(mn);
        mt2 = mt2_event.get_mt2();
        
        diffMW1MT2 = mtw1 - mt2;
        diffMW2MT2 = mtw2 - mt2;
        
        
        tOut->Fill();
    }
    
    tOut->AutoSave();
    fOut->Close();
}