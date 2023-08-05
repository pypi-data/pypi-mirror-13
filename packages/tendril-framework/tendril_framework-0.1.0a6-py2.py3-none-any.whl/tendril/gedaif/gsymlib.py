# Copyright (C) 2015 Chintalagiri Shashank
#
# This file is part of Tendril.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
gEDA gsymlib Module documentation (:mod:`gedaif.gsymlib`)
=========================================================
"""

import os
import csv

import yaml
import jinja2

import iec60063

from tendril.utils.config import GEDA_SYMLIB_ROOT
from tendril.utils.config import AUDIT_PATH
from tendril.utils.config import TENDRIL_ROOT
from tendril.utils.config import INSTANCE_CACHE
from tendril.utils.config import MAKE_GSYMLIB_IMG_CACHE

import tendril.utils.fsutils
import tendril.conventions.electronics

from tendril.utils.types.electromagnetic import Resistance
from tendril.utils.types.electromagnetic import Capacitance

from gschem import conv_gsch2png

from tendril.utils import log
logger = log.get_logger(__name__, log.INFO)


class GedaSymbol(object):
    def __init__(self, fpath):
        self.fpath = fpath
        self.fname = os.path.split(fpath)[1]
        self.device = ''
        self.value = ''
        self.footprint = ''
        self.description = ''
        self.status = ''
        self.package = ''
        self._is_virtual = ''
        self._img_repr_path = ''
        self._img_repr_fname = ''
        self._acq_sym(fpath)
        self._img_repr()

    def _acq_sym(self, fpath):
        with open(fpath, 'r') as f:
            for line in f.readlines():
                if line.startswith('device='):
                    self.device = line.split('=')[1].strip()
                if line.startswith('value='):
                    self.value = line.split('=')[1].strip()
                if line.startswith('footprint'):
                    self.footprint = line.split('=')[1].strip()
                    if self.footprint[0:3] == 'MY-':
                        self.footprint = self.footprint[3:]
                if line.startswith('description'):
                    self.description = line.split('=')[1].strip()
                if line.startswith('status'):
                    self.status = line.split('=')[1].strip()
                if line.startswith('package'):
                    self.package = line.split('=')[1].strip()
            if self.status == '':
                self.status = 'Active'

    def _img_repr(self):
        outfolder = os.path.join(INSTANCE_CACHE, 'gsymlib')
        self._img_repr_fname = os.path.splitext(self.fname)[0] + '.png'
        self._img_repr_path = os.path.join(outfolder, self._img_repr_fname)
        if not os.path.exists(outfolder):
            os.makedirs(outfolder)
        if os.path.exists(self._img_repr_path):
            if tendril.utils.fsutils.get_file_mtime(self._img_repr_path) > tendril.utils.fsutils.get_file_mtime(self.fpath):  # noqa
                return
        if MAKE_GSYMLIB_IMG_CACHE:
            conv_gsch2png(self.fpath, outfolder)

    @property
    def img_repr_fname(self):
        return self._img_repr_fname

    @property
    def ident(self):
        return tendril.conventions.electronics.ident_transform(self.device,
                                                               self.value,
                                                               self.footprint)

    @property
    def sym_ok(self):
        rval = False
        if self.device in tendril.conventions.electronics.DEVICE_CLASSES:
            rval = True
        return rval

    @property
    def is_generator(self):
        if self.status == 'Generator':
            return True
        return False

    @property
    def is_virtual(self):
        if self.status == 'Virtual':
            return True
        return False

    @property
    def is_deprecated(self):
        if self.status == 'Deprecated':
            return True
        return False

    @property
    def is_experimental(self):
        if self.status == 'Experimental':
            return True
        return False

    @is_virtual.setter
    def is_virtual(self, value):
        if self.status == 'Generator':
            if value is True:
                self.status = 'Virtual'
        else:
            raise AttributeError

    @property
    def is_wire(self):
        return tendril.conventions.electronics.fpiswire(self.device)

    @property
    def is_modlen(self):
        return tendril.conventions.electronics.fpismodlen(self.device)

    @property
    def datasheet_url(self):
        # TODO This can be cached
        try:
            from tendril.sourcing.electronics import vendor_list
            from tendril.inventory.guidelines import electronics_qty
            dkv = vendor_list[0]
            vsinfo = dkv.get_optimal_pricing(self.ident, electronics_qty.get_compliant_qty(self.ident, 5))  # noqa
            dkvpno = vsinfo[1]
            dkdsurl = dkv.get_vpart(dkvpno).datasheet
            return dkdsurl
        except Exception:
            return None

    @property
    def genident(self):
        return os.path.splitext(self.fname)[0] + '.gen'

    @property
    def genpath(self):
        if self.is_generator:
            return os.path.splitext(self.fpath)[0] + '.gen.yaml'
        else:
            raise AttributeError

    @property
    def generator(self):
        if not self.is_generator:
            raise AttributeError
        return GSymGeneratorFile(self.fpath)

    @property
    def idents(self):
        if not self.is_generator:
            raise AttributeError
        if not self.generator.values:
            return None
        return [tendril.conventions.electronics.ident_transform(self.device, v, self.footprint)  # noqa
                for v in self.generator.values]

    def __repr__(self):
        return '{0:40}'.format(self.ident)


class GSymGeneratorFile(object):
    def __init__(self, sympath):
        self._genpath = os.path.splitext(sympath)[0] + '.gen.yaml'
        self._type = None
        self._ivalues = []
        self._igen = []
        self._iunits = []
        data = self._get_data()
        self._values = []
        for value in data:
            if value is not None:
                self._values.append(value)

    @property
    def type(self):
        return self._type

    @property
    def igenerators(self):
        return self._igen

    @property
    def ivalues(self):
        return self._ivalues

    @property
    def iunits(self):
        return self._iunits

    def _get_data(self):
        with open(self._genpath) as genfile:
            gendata = yaml.load(genfile)
        if gendata["schema"]["name"] == "gsymgenerator" and \
           gendata["schema"]["version"] == 1.0:

            if gendata['type'] == 'simple':
                self._type = 'Simple'
                self._ivalues = [v for v in gendata['values']
                                 if v is not None and v.strip() is not None]
                return gendata['values']
            values = []

            if gendata['type'] == 'resistor':
                self._type = 'Resistor'
                for resistance in gendata['resistances']:
                    if resistance is not None:
                        values.append(resistance)
                        self._iunits.append(resistance)
                if 'generators' in gendata.keys():
                    for generator in gendata['generators']:
                        self._igen.append(generator)
                        if generator['std'] == 'iec60063':
                            rvalues = iec60063.gen_vals(
                                generator['series'], iec60063.res_ostrs,
                                start=generator['start'], end=generator['end']
                            )
                            for rvalue in rvalues:
                                values.append(tendril.conventions.electronics.construct_resistor(rvalue, generator['wattage']))  # noqa
                        else:
                            raise ValueError
                if 'values' in gendata.keys():
                    if gendata['values'][0].strip() != '':
                        values += gendata['values']
                        self._ivalues.extend(gendata['values'])
                return values

            if gendata['type'] == 'capacitor':
                self._type = 'Capacitor'
                for capacitance in gendata['capacitances']:
                    if capacitance is not None:
                        values.append(capacitance)
                        self._iunits.append(capacitance)
                if 'generators' in gendata.keys():
                    for generator in gendata['generators']:
                        self._igen.append(generator)
                        if generator['std'] == 'iec60063':
                            cvalues = iec60063.gen_vals(
                                generator['series'], iec60063.cap_ostrs,
                                start=generator['start'], end=generator['end']
                            )
                            for cvalue in cvalues:
                                values.append(tendril.conventions.electronics.construct_capacitor(cvalue, generator['voltage']))  # noqa
                        else:
                            raise ValueError
                if 'values' in gendata.keys():
                    if gendata['values'][0].strip() != '':
                        values += gendata['values']
                        self._ivalues.append(gendata['values'])
                return values
        else:
            logger.ERROR("Config file schema is not supported")

    @property
    def values(self):
        if len(self._values) > 0:
            return self._values
        return None


def get_folder_symbols(path, template=None,
                       resolve_generators=True, include_generators=False):
    if template is None:
        template = _jinja_init()
    symbols = []
    files = [f for f in os.listdir(path)
             if os.path.isfile(os.path.join(path, f))]
    for f in files:
        if f.endswith(".sym"):
            symbol = GedaSymbol(os.path.join(path, f))
            if symbol.is_generator:
                generators.append(symbol)
                if include_generators is True:
                    symbols.append(symbol)
                if resolve_generators is True:
                    genpath = os.path.splitext(symbol.fpath)[0] + '.gen.yaml'
                    if os.path.exists(genpath):
                        genfile = GSymGeneratorFile(symbol.fpath)
                        values = genfile.values
                        if values is not None:
                            for value in values:
                                if value is not None:
                                    vsymbol = GedaSymbol(symbol.fpath)
                                    vsymbol.is_virtual = True
                                    vsymbol.value = value
                                    symbols.append(vsymbol)
                    else:
                        stage = {'symbolfile': os.path.split(symbol.fpath)[1],
                                 'value': symbol.value.strip(),
                                 'description': symbol.description}
                        with open(genpath, 'w') as gf:
                            gf.write(template.render(stage=stage))
            else:
                symbols.append(symbol)
    return symbols


def gen_symlib(path=GEDA_SYMLIB_ROOT, recursive=True,
               resolve_generators=True, include_generators=False):
    symbols = []
    template = _jinja_init()
    if recursive:
        for root, dirs, files in os.walk(path):
            symbols += get_folder_symbols(
                root, template,
                resolve_generators=resolve_generators,
                include_generators=include_generators
            )
    else:
        symbols = get_folder_symbols(
            path, template,
            resolve_generators=resolve_generators,
            include_generators=include_generators
        )
    return symbols


def gen_index(symlist, upper=False):
    lindex = {}
    for symbol in symlist:
        ident = symbol.ident
        if upper:
            ident = ident.upper()
        if ident in lindex.keys():
            lindex[ident].append(symbol)
        else:
            lindex[ident] = [symbol]
    return lindex


def _jinja_init():
    templates_path = os.path.join(TENDRIL_ROOT, 'gedaif', 'templates')
    logger.debug("Loading templates from " + templates_path)
    loader = jinja2.FileSystemLoader(
        searchpath=templates_path
    )
    renderer = jinja2.Environment(loader=loader)
    template_file = 'generator.gen.yaml'
    template = renderer.get_template(template_file)
    return template


generators = []
gsymlib = []
index = {}
index_upper = {}
generator_names = []
gsymlib_idents = []


def regenerate_symlib():
    global generators
    generators = []
    global gsymlib
    gsymlib = gen_symlib(GEDA_SYMLIB_ROOT)
    global index
    index = gen_index(gsymlib)
    global index_upper
    index_upper = gen_index(gsymlib, upper=True)
    global generator_names
    generator_names = [os.path.splitext(x.fname)[0] + '.gen'
                       for x in generators]
    global gsymlib_idents
    gsymlib_idents = sorted(index.keys())


regenerate_symlib()


def get_generator(gen):
    for generator in generators:
        if os.path.splitext(generator.fname)[0] + '.gen' == gen:
            return generator


def is_recognized(ident):
    if ident in gsymlib_idents:
        return True
    return False


def get_symbol(ident, case_insensitive=False, get_all=False):
    if case_insensitive is False:
        if ident in index.keys():
            if not get_all:
                return index[ident][0]
            else:
                return index[ident]
    else:
        if ident.upper() in index_upper.keys():
            if not get_all:
                return index_upper[ident.upper()][0]
            else:
                return index_upper[ident.upper()]
    raise ValueError(ident)


def get_symbol_folder(ident, case_insensitive=False):
    symobj = get_symbol(ident, case_insensitive=case_insensitive)
    sympath = symobj.fpath
    symfolder = os.path.split(sympath)[0]
    return os.path.relpath(symfolder, GEDA_SYMLIB_ROOT)


def find_capacitor(capacitance, footprint, device='CAP CER SMD', voltage=None):
    if isinstance(capacitance, str):
        capacitance = Capacitance(capacitance)
    if isinstance(capacitance, Capacitance):
        capacitance = capacitance._value
    if footprint[0:3] == "MY-":
        footprint = footprint[3:]
    for symbol in gsymlib:
        if symbol.device == device and symbol.footprint == footprint:
            cap, volt = tendril.conventions.electronics.parse_capacitor(symbol.value)  # noqa
            sym_capacitance = tendril.conventions.electronics.parse_capacitance(cap)  # noqa
            if capacitance == sym_capacitance:
                return symbol
    raise ValueError


def find_resistor(resistance, footprint, device='RES SMD', wattage=None):
    if isinstance(resistance, str):
        resistance = Resistance(resistance)
    if isinstance(resistance, Resistance):
        resistance = resistance._value
    if footprint[0:3] == "MY-":
        footprint = footprint[3:]
    if device == 'RES THRU':
        if resistance in [tendril.conventions.electronics.parse_resistance(x)  # noqa
                          for x in iec60063.gen_vals(iec60063.get_series('E24'), iec60063.res_ostrs)]:  # noqa
            return tendril.conventions.electronics.construct_resistor(tendril.conventions.electronics.normalize_resistance(resistance), '0.25W')  # noqa
        else:
            raise ValueError(resistance, device)
    for symbol in gsymlib:
        if symbol.device == device and symbol.footprint == footprint:
            res, watt = tendril.conventions.electronics.parse_resistor(symbol.value)  # noqa
            sym_resistance = tendril.conventions.electronics.parse_resistance(res)  # noqa
            if resistance == sym_resistance:
                return symbol.value
    raise ValueError(resistance)


def export_gsymlib_audit():
    auditfname = os.path.join(AUDIT_PATH, 'gsymlib-audit.csv')
    outf = tendril.utils.fsutils.VersionedOutputFile(auditfname)
    outw = csv.writer(outf)
    outw.writerow(['filename', 'status', 'ident', 'device', 'value',
                   'footprint', 'description', 'path', 'package'])
    for symbol in gsymlib:
        outw.writerow(
            [symbol.fname, symbol.status, symbol.ident, symbol.device,
             symbol.value, symbol.footprint, symbol.description,
             symbol.fpath, symbol.package]
        )
    outf.close()
