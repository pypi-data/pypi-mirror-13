import os
import glob
import platform
import searchWFini as swi
from applicake.base.apputils import dicts
import pepidentWF
from multiprocessing import freeze_support
from ruffus import pipeline_run


from applicake.base import get_handler


def write_ini(ini, dest="."):
    print 'Starting from scratch by creating new input.ini'
    with open(os.path.join(dest,"input.ini"), 'w+') as f:
        f.write(ini)


def remove_ini_log():
    for fl in glob.glob("*.ini"):
        os.remove(fl)
    for fl in glob.glob("*.log"):
        os.remove(fl)


def peptidesearch_overwriteInfo(overwrite):
    # construct info from defaults < info < commandlineargs
    inifile = overwrite['INPUT']
    ih = get_handler(inifile)
    fileinfo = ih.read(inifile)
    info = dicts.merge(overwrite, fileinfo)
    ih.write(info,'input.ini')
    return info



if __name__ == '__main__':


    remove_ini_log()
    tmp = swi.setup_general() + swi.setup_search()
    if platform.system() == 'Linux':
        tmp += swi.setup_linux()
    else:
        tmp += swi.setup_windows()
    write_ini(tmp)

    peptidesearch_overwriteInfo({'INPUT' : "input.ini", 'MZXML': swi.getMZXML(), 'DBASE' : swi.getDB(),'OUTPUT' : 'output.ini'})
    pepidentWF.run_peptide_WF()


#pipeline_printout_graph ('flowchart.png','png',[copy2dropbox],no_key_legend = False) #svg
