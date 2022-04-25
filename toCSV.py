#! /usr/bin/python3

import subprocess as sub
import re
import sys
import os.path

from decimal import *

from datevCSV import datevBuchungszeileBuchungsstapelformat
 
def toDatevCSV(completifyTempfileName, outfileName):
    infile = open(completifyTempfileName, "r")
    outfile = open(outfileName, "w")
    linesOfInfile = infile.readlines()
    for line in linesOfInfile:
        #                          A   ;  B    ;  C    ;  D    ;  E    ;   F   ;   G   ;   H   ;   I   ;   J   ;   K   ;   L
        matcherObj=re.compile("^([^;]*);([^;]*);([^;]*);([^;]*);([^;]*);([^;]*);([^;]*);([^;]*);([^;]*);([^;]*);([^;]*);([^;]*)$").match(line)
        bz = datevBuchungszeileBuchungsstapelformat()
        bz.umsatz = matcherObj.group(4).replace(".",",")

        if bz.umsatz.__contains__("-"):
            bz.umsatz = bz.umsatz.replace("-","")
            bz.sollHabenKZ = "H"
        else:
            bz.sollHabenKZ = "S"
        bz.waehrungsKZUmsatz = matcherObj.group(5)
        bz.konto = "60000" # fixed

        if matcherObj.group(7) == "DE": # arrival country == "DE"
            if matcherObj.group(3) == "0.07": # price of items vat rate percent = 0.07
                bz.gegenkonto = "8300"
            else:
                bz.gegenkonto = "8400"
        else:
            if not(matcherObj.group(11) == ""): # buyer_vat_number != ""
                bz.gegenkonto = "8125"
            else:
                if matcherObj.group(10) == "ATU75273847": # seller arrival country vat number
                    bz.gegenkonto = "8326"
                else :
                    bz.gegenkonto = "8329"
        
        if (
                   (bz.gegenkonto == "8329")
                or (bz.gegenkonto == "8326")
           ):
            bz.buSchluessel = "10"
        else:
            pass

        matcherDate = re.compile("([0-9]{2})-([0-9]{2})-([0-9]{4})").match(matcherObj.group(2))
        if matcherDate:
            bz.belegdatum = matcherDate.group(1) + matcherDate.group(2)
        else:
            pass

        bz.belegfeld1 = matcherObj.group(12).replace("\n","") # vat_inv_number
        bz.belegfeld2 = matcherObj.group(1) # transaction event id
        
        if bz.gegenkonto == "8400":
            pass
        else:
            if bz.gegenkonto == "8125":
                bz.EUSteuersatzBestimmungsland = matcherObj.group(11) # buyer vat number
            else:
                if(
                       (bz.gegenkonto == "8329")
                    or (bz.gegenkonto == "8326")
                  ):
                    bz.USTIdBestimmungsland = matcherObj.group(7) # arrival country ?!?!
                else:
                    pass

        if bz.buSchluessel == "10":
            pct = matcherObj.group(3) # price of items vat rate percent
            if pct == "":
                pct = "0.0"
            else:
                pass
            pct = (Decimal(float(str(pct)))*100).quantize(Decimal("1"))
            bz.EUSteuersatzBestimmungsland = str(float(pct))
        else:
            pass
        
        outfile.write(bz.toCSV_String() + "\n")

def completify(infileName,completifyTempfileName):
    infile = open(infileName, "r")
    outfile = open(completifyTempfileName, "w")
    linesOfInfile = infile.readlines()
    for line in linesOfInfile:
        #                          A  ;  B  ;  C  ;  D  ;  E   ;   F   ;   G   ;   H   ;   I   ;toEOL
        matcherObj=re.compile("^([^;]*;[^;]*;[^;]*;[^;]*;[^;]*);([^;]*);([^;]*);([^;]*);([^;]*);(.*)$").match(line)
        preDepartureCountry = matcherObj.group(1)
        departureCountry = matcherObj.group(2)
        arrivalCountry = matcherObj.group(3)
        saleDepartureCountry = matcherObj.group(4)
        saleArrivalCountry = matcherObj.group(5)
        postSaleArrivalCountry = matcherObj.group(6)

        if (
                    (departureCountry == "")
                and not((saleDepartureCountry == ""))
           ):
            departureCountry = saleDepartureCountry
        else:
            pass # either departurecountry is filled or can not be filled based on saledeparture country

        if (
                    (arrivalCountry == "")
                and not((saleArrivalCountry == ""))
           ):
            arrivalCountry = saleArrivalCountry
        else:
            pass # either arrivalCountry is filled or can not be filled based on salearrivalcountry
        
        outfile.write(preDepartureCountry + ";" + departureCountry + ";" + arrivalCountry + ";" + saleDepartureCountry + ";" + saleArrivalCountry + ";" + postSaleArrivalCountry + "\n")

def main():
    if(len(sys.argv) != 3):
        print("Calling convention: completifier.py infile outfile")
        exit()
    else:
        pass

    if  (
                (not os.path.isfile(sys.argv[1]))
            or  (
                       (os.path.isfile(sys.argv[1]))
                    and(re.compile("^.*\.(.*)$").match(sys.argv[1]).group(1) != "csv")
                )
        ):
        print("infile not found or invalid (was "+sys.argv[1]+")")
        exit()
    else:
        pass

    if os.path.isfile(sys.argv[2]):
        overwrite=input("Overwrite Outfile? (y/n) : ")
        if (
                (overwrite != "y")
             and(overwrite != "n")
           ):
            print("invalid answer, terminating")
            exit()
        elif (overwrite == "y"):
            pass
        else:
            print("Outfile exists and is not allowed to be overwritten, call again with different outfile")
    else:
        pass

    #if everything ok (program did not prematurely terminate
    infile = sys.argv[1]
    outfile = sys.argv[2]
    os.system("./preprocess.sh " + infile + " pre_" + infile)
    completify("pre_"+infile,"comp_" + infile)
    os.system("rm pre_"+infile)
    toDatevCSV("comp_" + infile, outfile)
    os.system("rm comp_"+infile)

main() # use call to main in production anything else otherwise
