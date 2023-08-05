#!/usr/bin/env python
import os

from toolscake.apps.tpp.searchengines.enzymes import enzymestr_to_engine
from toolscake.apps.tpp.searchengines.modifications import genmodstr_to_engine
from applicake.base.apputils.templates import read_mod_write, get_tpl_of_class
from applicake.base.apputils.validation import check_exitcode, check_xml, check_stdout
from applicake.base.coreutils.arguments import Argument
from applicake.base.coreutils.keys import Keys
from toolscake.apps.tpp.searchengines.searchenginebase import SearchEnginesBase


class Comet(SearchEnginesBase):
    """
    Wrapper for the search engine comet.
    """
    def add_args(self):
        args = super(Comet, self).add_args()
        args.append(Argument('COMET_DIR', 'executable location.', default=''))
        args.append(Argument('COMET_EXE', 'executable name.', default='comet'))

        return args

    def prepare_run(self, log, info):
        wd = info[Keys.WORKDIR]
        basename = os.path.join(wd, os.path.splitext(os.path.split(info[Keys.MZXML])[1])[0])
        info[Keys.PEPXML] = basename + '.pep.xml'

        # need to create a working copy to prevent replacement or generic definitions
        # with app specific definitions
        app_info = info.copy()

        if info['PRECMASSUNIT'] == 'Da':
            app_info['PRECMASSUNIT'] = '0'
        elif info['PRECMASSUNIT'] == 'ppm':
            app_info['PRECMASSUNIT'] = '2'
        else:
            raise RuntimeError("Precmassunit %s unknown" % info['PRECMASSUNIT'])

        if info['FRAGMASSUNIT'] == 'ppm':
            raise RuntimeError("Comet does not support frag mass error unit PPM")

        if not 0.01 < float(app_info['FRAGMASSERR']) < 1.1:
            log.warn('Very high or low fragmasserror ' + app_info['FRAGMASSERR'])

        app_info["STATIC_MODS"], app_info["VARIABLE_MODS"], _ = genmodstr_to_engine(info["STATIC_MODS"],
                                                                                 info["VARIABLE_MODS"], 'Comet')
        app_info['ENZYME'], app_info['NUM_TERM_CLEAVAGES'] = enzymestr_to_engine(info['ENZYME'], 'Comet')

        tplfile = os.path.join(wd, "comet.params")
        template = get_tpl_of_class(self)
        read_mod_write(app_info,template, tplfile)

        exe_path = app_info['COMET_DIR']
        exe = app_info['COMET_EXE']

        command = "{exe} -N{basename} -P{tplfile} {mzxml}".format(exe=os.path.join(exe_path, exe), basename=basename, tplfile=tplfile, mzxml=info[Keys.MZXML])
        return info, command

    def validate_run(self, log, info, exit_code, stdout):
        if "Warning - no spectra searched" in stdout:
            raise RuntimeError("No spectra in mzXML!")
        check_stdout(log,stdout)
        check_exitcode(log, exit_code)
        check_xml(log, info[Keys.PEPXML])
        return info


if __name__ == "__main__":
    Comet.main()