import re, os

fileName="shape.py"

file = open("list","r")
variables = file.readlines()
file.close()

file = open(fileName,"r")
scriptLine = file.readlines()
file.close()

for laVariable in variables:
    nomVar = re.split("&",laVariable[:-1])[0]
    nomTag = re.split("&",laVariable[:-1])[1]
    xlabelTag = re.split("&",laVariable[:-1])[2]
    print "on fait ",nomVar
    if  not os.path.isdir(nomVar):
        os.makedirs(nomVar, 0777)
    file = open(nomVar+"/shape.py","w")
    for ligne in scriptLine:
        if len(re.split("#",ligne))>1:
            continue
        if len(re.split("variable",ligne))>1:
            file.write("variable='"+nomVar+"'\n")
            continue
        if len(re.split("tag",ligne))>1:
            file.write("tag='"+nomTag+"'\n")
            continue
        if len(re.split("xlabel",ligne))>1:
            file.write("xlabel='"+xlabelTag+"'\n")
            continue
        file.write(ligne)
    file.close()




#for lines in scriptLine:

#file = open(fileToCopy,"w")
#re.split("$",laVariable[:1])

