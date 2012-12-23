
rm -rf datacards
mkdir datacards
root -b -q "buildDataCard.C(1)"
./shapeDatacards.sh
