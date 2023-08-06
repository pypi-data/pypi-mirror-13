# identification workflow for systeMHC

#!/usr/bin/env python
import sys

from ruffus import *

from applicake.apps.examples.echobasic import EchoBasic
from applicake.apps.flow.merge import Merge
from applicake.apps.flow.split import Split

from searchengines.comet import Comet
from searchengines.iprophetpepxml2csv import IprohetPepXML2CSV
from searchengines.myrimatch import Myrimatch
from searchengines.xtandem import Xtandem


from interprophet import InterProphet
from peptideprophet import PeptideProphetSequence

from multiprocessing import freeze_support
from ruffus import pipeline_run

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


def run_peptide_WF(nrthreads = 2):
    freeze_support()
    pipeline_run([convert2csv], multiprocess=nrthreads)




