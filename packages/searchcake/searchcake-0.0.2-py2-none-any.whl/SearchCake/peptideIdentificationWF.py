# identification workflow for systeMHC

#!/usr/bin/env python
import glob
import os
import sys
import subprocess
from multiprocessing import freeze_support
import platform

from ruffus import *

from applicake.apps.examples.a_pyecho import PythonEcho
from applicake.apps.flow.merge import Merge
from applicake.apps.flow.split import Split
from interprophet import InterProphet
from peptideprophet import PeptideProphetSequence
from searchengines.comet import Comet
from searchengines.iprophetpepxml2csv import IprohetPepXML2CSV
from searchengines.myrimatch import Myrimatch

from SearchCake.searchengines.xtandem import Xtandem

basepath = os.path.dirname(__file__) + '/../../'



@files("input.ini", "inputfix.ini")
def biopersdb(infile, outfile):
    sys.argv = ['--INPUT', infile, '--OUTPUT', outfile]
    PythonEcho.main()

@follows(biopersdb)
@split("inputfix.ini", "split.ini_*")
def split_dataset(infile, unused_outfile):
    sys.argv = ['--INPUT', infile, '--SPLIT', 'split.ini', '--SPLIT_KEY', 'MZXML']
    Split.main()


###################################################################################

@transform(split_dataset, regex("split.ini_"), "rawmyri.ini_")
def myri(infile, outfile):
    sys.argv = ['--INPUT', infile, '--OUTPUT', outfile, '--THREADS', '4']
    Myrimatch.main()


@transform(myri, regex("rawmyri.ini_"), "myrimatch.ini_")
def peppromyri(infile, outfile):
    sys.argv = ['--INPUT', infile, '--OUTPUT', outfile, '--NAME', 'pepmyri']
    PeptideProphetSequence.main()


### TANDEM ###################################################################

@transform(split_dataset, regex("split.ini_"), "rawtandem.ini_")
def tandem(infile, outfile):
    sys.argv = ['--INPUT', infile, '--OUTPUT', outfile, '--THREADS', '4']
    Xtandem.main()


@transform(tandem, regex("rawtandem.ini_"), "tandem.ini_")
def pepprotandem(infile, outfile):
    sys.argv = ['--INPUT', infile, '--OUTPUT', outfile, '--NAME', 'peptandem']
    PeptideProphetSequence.main()


###################################################################################

@transform(split_dataset, regex("split.ini_"), "rawcomet.ini_")
def comet(infile, outfile):
    sys.argv = ['--INPUT', infile, '--OUTPUT', outfile, '--THREADS', '4']
    Comet.main()


@transform(comet, regex("rawcomet.ini_"), "comet.ini_")
def pepprocomet(infile, outfile):
    sys.argv = ['--INPUT', infile, '--OUTPUT', outfile, '--NAME', 'pepcomet']
    PeptideProphetSequence.main()

############################# TAIL: PARAMGENERATE ##################################

@merge([pepprocomet,peppromyri], "ecollate.ini")
def merge_datasets(unused_infiles, outfile):
    sys.argv = ['--MERGE', 'comet.ini', '--MERGED', outfile]
    Merge.main()

@follows(merge_datasets)
@files("ecollate.ini_0", "datasetiprophet.ini")
def datasetiprophet(infile, outfile):
    sys.argv = ['--INPUT', infile, '--OUTPUT', outfile]
    InterProphet.main()

@follows(datasetiprophet)
@files("datasetiprophet.ini", "copy2dropbox.ini")
def convert2csv(infile, outfile):
    sys.argv = [ '--INPUT', infile, '--OUTPUT', outfile]
    IprohetPepXML2CSV.main()


def setupLinux():
    print 'Starting from scratch by creating new input.ini'
    for fl in glob.glob("*.ini"):
        print fl
        os.remove(fl)
    for fl in glob.glob("*.log"):
        print fl
        os.remove(fl)

    with open("input.ini", 'w+') as f:
            f.write("""
LOG_LEVEL = DEBUG
COMMENT = WFTEST - newUPS TPP

# Search parameters
FDR_CUTOFF = 0.01
FDR_TYPE = iprophet-pepFDR
FRAGMASSERR = 0.5
FRAGMASSUNIT = Da
PRECMASSERR = 15
PRECMASSUNIT = ppm
MISSEDCLEAVAGE = 0
ENZYME = Nonspecific
STATIC_MODS =
VARIABLE_MODS = Oxidation (M)

## TPP
DECOY_STRING = DECOY_
IPROPHET_ARGS = MINPROB=0


## Parameters
MZXML=/home/witold/prog/SysteMHC_Data/mzXML/PBMC1_Tubingen_120724_CB_Buffy18_W_20_Rep1_msms1_c.mzXML,/home/witold/prog/SysteMHC_Data/mzXML/PBMC1_Tubingen_120724_CB_Buffy18_W_20_Rep2_msms2_c.mzXML,/home/witold/prog/SysteMHC_Data/mzXML/PBMC1_Tubingen_120724_CB_Buffy18_W_20_Rep3_msms3_c.mzXML,/home/witold/prog/SysteMHC_Data/mzXML/PBMC1_Tubingen_120724_CB_Buffy18_W_20_Rep4_msms4_c.mzXML,/home/witold/prog/SysteMHC_Data/mzXML/PBMC1_Tubingen_120724_CB_Buffy18_W_20_Rep5_msms5_c.mzXML

DBASE=/home/witold/prog/SysteMHC_Data/fasta/CNCL_05640_2015_09_DECOY.fasta

COMET_DIR=/home/witold/prog/SearchCake_Binaries/Comet/linux
COMET_EXE=comet.exe
MYRIMATCH_DIR=/home/witold/prog/SearchCake_Binaries/MyriMatch/linux/linux_64bit
MYRIMATCH_EXE=myrimatch
TPPDIR=/home/witold/prog/SearchCake_Binaries/tpp/ubuntu14.04/bin/

""")


def setupWindows():
    print 'Starting from scratch by creating new input.ini'
    subprocess.call("rm *ini* *.log", shell=True)
    with open("input.ini", 'w+') as f:
        f.write("""
LOG_LEVEL = DEBUG
COMMENT = WFTEST - newUPS TPP

# Search parameters
FDR_CUTOFF = 0.01
FDR_TYPE = iprophet-pepFDR
FRAGMASSERR = 0.5
FRAGMASSUNIT = Da
PRECMASSERR = 15
PRECMASSUNIT = ppm
MISSEDCLEAVAGE = 0
ENZYME = Nonspecific
STATIC_MODS =
VARIABLE_MODS = Oxidation (M)

## TPP
DECOY_STRING = DECOY_
IPROPHET_ARGS = MINPROB=0


## Parameters
MZXML=D:/projects/p1958/data/datafiles/mzXML/PBMC1_Tubingen_120724_CB_Buffy18_W_20_Rep1_msms1_c.mzXML,D:/projects/p1958/data/datafiles/mzXML/PBMC1_Tubingen_120724_CB_Buffy18_W_20_Rep2_msms2_c.mzXML,D:/projects/p1958/data/datafiles/mzXML/PBMC1_Tubingen_120724_CB_Buffy18_W_20_Rep3_msms3_c.mzXML,D:/projects/p1958/data/datafiles/mzXML/PBMC1_Tubingen_120724_CB_Buffy18_W_20_Rep4_msms4_c.mzXML,D:/projects/p1958/data/datafiles/mzXML/PBMC1_Tubingen_120724_CB_Buffy18_W_20_Rep5_msms5_c.mzXML


DBASE=D:/projects/p1958/data/databases/CNCL_05640_2015_09_DECOY.fasta
COMET_DIR=C:/Users/wolski/prog/applicake-tools/SearchCake_Binaries/Comet/windows/windows_64bit
COMET_EXE=comet.exe
MYRIMATCH_DIR=C:/Users/wolski/prog/applicake-tools/SearchCake_Binaries/MyriMatch/windows/windows_64bit
MYRIMATCH_EXE=myrimatch.exe
TPPDIR=C:/Users/wolski/prog/applicake-tools/SearchCake_Binaries/tpp/windows/windows_64bit

""")

def runPipline():
    freeze_support()
    pipeline_run([convert2csv],multiprocess=3)

if __name__ == '__main__':
    if platform.system() == 'Linux':
        setupLinux()
    else:
        setupWindows()
    runPipline()

#pipeline_printout_graph ('flowchart.png','png',[copy2dropbox],no_key_legend = False) #svg
