
def setup_windows():
    return '''
COMET_DIR=c:/users/wewol/prog/SearchCake_Binaries/Comet/windows/windows_64bit/
COMET_EXE=comet.exe
MYRIMATCH_DIR=c:/users/wewol/prog/SearchCake_Binaries/MyriMatch/windows/windows_64bit/
MYRIMATCH_EXE=myrimatch.exe
TPPDIR=c:/users/wewol/prog/SearchCake_Binaries/tpp/windows/windows_64bit/
'''


def setup_linux():
    return '''
COMET_DIR=/home/witold/prog/SearchCake_Binaries/Comet/linux
COMET_EXE=comet.exe

MYRIMATCH_DIR=/home/witold/prog/SearchCake_Binaries/MyriMatch/linux/linux_64bit
MYRIMATCH_EXE=myrimatch

TPPDIR=/home/witold/prog/SearchCake_Binaries/tpp/ubuntu14.04/bin/
'''

def setup_general():
    return """
LOG_LEVEL = DEBUG
COMMENT = WFTEST - newUPS TPP
"""


def setup_search():
    return '''
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
MZXML =
DBASE =
    '''

def getMZXML():
    return ['/home/witold/prog/SysteMHC_Data/mzXML/PBMC1_Tubingen_120724_CB_Buffy18_W_20_Rep1_msms1_c.mzXML',
            '/home/witold/prog/SysteMHC_Data/mzXML/PBMC1_Tubingen_120724_CB_Buffy18_W_20_Rep2_msms2_c.mzXML',
            '/home/witold/prog/SysteMHC_Data/mzXML/PBMC1_Tubingen_120724_CB_Buffy18_W_20_Rep3_msms3_c.mzXML',
            '/home/witold/prog/SysteMHC_Data/mzXML/PBMC1_Tubingen_120724_CB_Buffy18_W_20_Rep4_msms4_c.mzXML',
            '/home/witold/prog/SysteMHC_Data/mzXML/PBMC1_Tubingen_120724_CB_Buffy18_W_20_Rep5_msms5_c.mzXML']

def getDB():
    return '/home/witold/prog/SysteMHC_Data/fasta/CNCL_05640_2015_09_DECOY.fasta'
