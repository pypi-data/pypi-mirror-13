# identification workflow for systeMHC

#!/usr/bin/env python
import glob
import os
import sys
import subprocess
from multiprocessing import freeze_support
import platform

from ruffus import *

from applicake.apps.examples.echobasic import EchoBasic
from applicake.apps.flow.merge import Merge
from applicake.apps.flow.split import Split

from applicake.base import Argument, Keys, KeyHelp, BasicApp
from applicake.base.coreutils import IniInfoHandler


from searchengines.comet import Comet
from searchengines.iprophetpepxml2csv import IprohetPepXML2CSV
from searchengines.myrimatch import Myrimatch
from searchengines.xtandem import Xtandem


from interprophet import InterProphet
from peptideprophet import PeptideProphetSequence


##basepath = os.path.dirname(__file__) + '/../../'


@files("input.ini", "inputfix.ini")
def biopersdb(infile, outfile):
    sys.argv = ['--INPUT', infile, '--OUTPUT', outfile]
    EchoBasic.main()


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
@files("datasetiprophet.ini", "convert2csv.ini")
def convert2csv(infile, outfile):
    sys.argv = [ '--INPUT', infile, '--OUTPUT', outfile]
    IprohetPepXML2CSV.main()


def remove_ini_log():
    for fl in glob.glob("*.ini"):
        os.remove(fl)
    for fl in glob.glob("*.log"):
        os.remove(fl)


def setupLinux():
    print 'Starting from scratch by creating new input.ini'
    remove_ini_log()
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
    with open("input.ini", 'w+') as f:
        f.write("""
LOG_LEVEL = DEBUG
COMMENT = WFTEST - newUPS TPP

# Search parameters
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
DECOY = DECOY_
IPROPHET_ARGS = MINPROB=0


## Parameters
MZXML=../SystemMHC_Data/mzXML/PBMC1_Tubingen_120724_CB_Buffy18_W_20_Rep1_msms1_c.mzXML,../SystemMHC_Data/mzXML/PBMC1_Tubingen_120724_CB_Buffy18_W_20_Rep2_msms2_c.mzXML,../SystemMHC_Data/mzXML/PBMC1_Tubingen_120724_CB_Buffy18_W_20_Rep3_msms3_c.mzXML,../SystemMHC_Data/mzXML/PBMC1_Tubingen_120724_CB_Buffy18_W_20_Rep4_msms4_c.mzXML,../SystemMHC_Data/mzXML/PBMC1_Tubingen_120724_CB_Buffy18_W_20_Rep5_msms5_c.mzXML


DBASE=../SystemMHC_Data/fasta/CNCL_05640_2015_09_DECOY.fasta
COMET_DIR=../SearchCake_Binaries/Comet/windows/windows_64bit/
COMET_EXE=comet.exe
MYRIMATCH_DIR=../SearchCake_Binaries/MyriMatch/windows/windows_64bit/
MYRIMATCH_EXE=myrimatch.exe
TPPDIR=../SearchCake_Binaries/tpp/windows/windows_64bit/

""")

#def runPipline():
#    freeze_support()
#    pipeline_run([convert2csv],multiprocess=3)


class PeptideIdentificationWorkflow(BasicApp):
    """
    Let's wrap a ruffus workflow in an app
    """
    def add_args(self):
        return [
            Argument(Keys.WORKDIR, KeyHelp.WORKDIR),
            Argument(Keys.THREADS, KeyHelp.THREADS, default=1),

            Argument('COMMENT', 'tpp workflow test'),
            #inter prophet
            Argument('IPROPHET_ARGS', 'Arguments for InterProphetParser', default='MINPROB=0'),
            ##  peptide prophet
            Argument('ENZYME', 'Enzyme used for digest'),
            Argument('DBASE', 'FASTA dbase'),
            Argument('MZXML', 'Path to the original MZXML inputfile'),
            Argument('DECOY', 'Decoy pattern', default='DECOY_'),
            Argument('TPPDIR', 'Path to the tpp',  default=''),

            ## searchengines
            Argument('FRAGMASSERR', 'Fragment mass error', default=0.4),
            Argument('FRAGMASSUNIT', 'Unit of the fragment mass error',default='Da'),
            Argument('PRECMASSERR', 'Precursor mass error',default=15),
            Argument('PRECMASSUNIT', 'Unit of the precursor mass error',default='ppm'),
            Argument('MISSEDCLEAVAGE', 'Number of maximal allowed missed cleavages', default=1),
            Argument('ENZYME', 'Enzyme used to digest the proteins',default='Trypsin'),
            Argument('STATIC_MODS', 'List of static modifications',default='Carbamidomethyl (C)'),
            Argument('VARIABLE_MODS', 'List of variable modifications'),
            Argument('DBASE', 'Sequence database file with target/decoy entries'),

            ## system config
            Argument("TPPDIR",  KeyHelp.EXECDIR, default=''),
            Argument('COMET_DIR', 'executable location.', default=''),
            Argument('COMET_EXE', 'executable name.', default='comet'),
            Argument('MYRIMATCH_DIR', 'executable location.', default=''),
            Argument('MYRIMATCH_EXE', KeyHelp.EXECUTABLE, default='myrimatch')
        ]

    def run(self, log, info):
        #write ini for workflow, contains BASEDIR + JOBID
        pipeline_info = info.copy()
        pipeline_info['BASEDIR'] = info['WORKDIR']

        path = os.path.join(pipeline_info["WORKDIR"],"input.ini")
        IniInfoHandler().write(info,path)

        #run workflow
        os.chdir(pipeline_info['BASEDIR'])

        freeze_support()
        pipeline_run([convert2csv],multiprocess=int(pipeline_info[Keys.THREADS]))

        #parse "important information"
        pipeline_info = IniInfoHandler().read("convert2csv.ini")
        pipeline_info['BASEDIR'] = info['BASEDIR']

        info = pipeline_info
        log.debug("NOW THIS IS THE REAL RESULT. I FETCHED FROM SUBWORKFLOW %s" % info['COPY'])

        return info


if __name__ == '__main__':
    if platform.system() == 'Linux':
        setupLinux()
    else:
        setupWindows()
    PeptideIdentificationWorkflow.main()

#pipeline_printout_graph ('flowchart.png','png',[copy2dropbox],no_key_legend = False) #svg
