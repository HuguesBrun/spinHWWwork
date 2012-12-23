TChain *chain = new TChain("latino");
TFile *myOutFile; 

TString theWeights = "*(baseW*puW60ABC*effW*triggW*12.1)";

doTheHisto(TString variable, int bin, float theMin, float theMax){
    TH1F *histo = new TH1F(variable,"",bin, theMin, theMax);
    
    
    chain->Draw(variable+">>"+variable, "(trigger==1. && pfmet>20. && mll>12 && (zveto==1||!sameflav) && mpmet>20. && bveto_mu==1 && nextra==0 && (bveto_ip==1 && (nbjettche==0 || njet>3)  ) && ptll>45. && (njet==0 || njet==1 || (dphilljetjet<pi/180.*165. || !sameflav )  ) && ( !sameflav || ( (njet!=0 || dymva1>0.88) && (njet!=1 || dymva1>0.84) && ( njet==0 || njet==1 || (pfmet > 45.0)) ) ) && mth>80 && mth<280 && mll<200 && (channel==2 || channel==3) && njet==0)"+theWeights);
    
    histo->Write();
    
}




prepSigHisto(TString path, TString outName){
    chain->Add(path);
    myOutFile = new TFile("finalhisto_"+outName,"RECREATE");
    
    doTheHisto("mth",40,0,200);
    doTheHisto("dphill",40,0,3.15);
    doTheHisto("mtAsym",30,-0.2,1.);
    doTheHisto("mt2",30,10,120.);
    doTheHisto("diffMW1MT2",30,0,200.);
    doTheHisto("diffMW2MT2",30,-10,100.);
    doTheHisto("drll",30,0,3.);
    doTheHisto("mll",40,0,200);
    
    myOutFile->Close();
}

