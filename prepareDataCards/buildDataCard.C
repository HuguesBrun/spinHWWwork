


buildDataCard(int altModel){
    TString nameAlt;
    if (altModel==0) nameAlt = "Higgs0M125ToWW2L2Nu";
    else nameAlt = "Graviton2PM";
    
    
    TFile *myFile = new TFile("theHistos/finalhisto_bg.root");
    TFile *myFileSig = new TFile("theHistos/finalhisto_SMH125ToWW2L2Nu.root");
    TFile *myFileSigAlt = new TFile("theHistos/finalhisto_"+nameAlt+".root");
    TFile *myShapeFile = new TFile("datacards/hwwof_0j.input_8TeV_forSpin.root","RECREATE");
    
    TIter nextkey(myFile->GetListOfKeys());
    TKey *key;
    while (key = (TKey*)nextkey()) {
        TString theTypeClasse = key->GetClassName();
        TString theNomClasse = key->GetName();
        
        cout << "generation de la datacard pour " << theNomClasse << endl;
        
        TH1D *templateHistoSig = (TH1D*) myFileSig->Get(theNomClasse);
        templateHistoSig->SetName("histo"+theNomClasse+"_signal");
        myShapeFile->cd();
        templateHistoSig->Write();
        
        TH1D *templateHistoSigAlt = (TH1D*) myFileSigAlt->Get(theNomClasse);
        templateHistoSigAlt->SetName("histo"+theNomClasse+"_signal_ALT");
        float normalise = 1.0*templateHistoSig->Integral()/templateHistoSigAlt->Integral();
        templateHistoSigAlt->Scale(normalise);
        myShapeFile->cd();
        templateHistoSigAlt->Write();
        
        TH1D *templateHisto = (TH1D*) myFile->Get(theNomClasse);
        templateHisto->SetName("histo"+theNomClasse+"_allBgs");
       // templateHisto->Scale(0.001);
        myShapeFile->cd();
        templateHisto->Write();
        
        
        TH1D *theSum = (TH1D*) templateHisto->Clone("histo"+theNomClasse+"_data");
        theSum->Add(templateHistoSig,1);
        theSum->Write();
        
        ofstream myfile;
        myfile.open("datacards/dataCard_"+theNomClasse+".txt");
        
        float nomberOfEventTot = templateHistoSig->Integral()+templateHisto->Integral();
        
        myfile << "imax 1 number of channels \n";
        myfile << "jmax * number of background \n";
        myfile << "kmax * number of nuisance parameters \n";
        myfile << "Observation " << nomberOfEventTot << "\n";

        myfile << "shapes *   *   ../hwwof_0j.input_8TeV_forSpin.root  histo"+theNomClasse+"_$PROCESS \n";
        myfile << "shapes data_obs * ../hwwof_0j.input_8TeV_forSpin.root  histo"+theNomClasse+"_data\n";

        myfile << "bin j0of j0of j0of \n";
        myfile << "process signal signal_ALT allBgs\n";
        myfile << "process -1 0 1\n";
        myfile << "rate ";
        myfile << templateHistoSig->Integral() << " ";
        myfile << templateHistoSigAlt->Integral() << " ";
        myfile << templateHisto->Integral()<< " ";
        myfile.close();
        
        
        delete templateHisto;
        delete templateHistoSig;
        delete theSum;

    }
}