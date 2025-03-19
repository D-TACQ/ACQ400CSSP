import time
from java.util.logging import Logger
from org.phoebus.framework.macros import Macros
from org.csstudio.display.builder.runtime.script import PVUtil

""" Init macros and local pvs """

# Startup
t0 = time.time()
logger = Logger.getLogger('init_main')
widget = locals()['widget']
pvs = locals()['pvs']
display = widget.getTopDisplayModel()
timeout = 2 * 1000

# Functions
class DotDict(dict):
    __delattr__ = dict.__delitem__
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__

def get_macros(widget):
    macros = widget.getEffectiveMacros()
    return DotDict({key: macros.getValue(key) for key in macros.names})

def set_macros(widget, macros):
    new_macros = Macros()
    for key in macros:
        new_macros.add(key, str(macros[key]))
    widget.setPropertyValue("macros", new_macros)

def read_pv(pvname):
    try: PV = PVUtil.createPV(pvname, timeout)
    except: return False
    return PVUtil.getVType(PV).getValue()

def get_model(uutname):
    uut_model = read_pv("{}:0:MODEL".format(uutname))
    if uut_model:
        for model in model_def:
            if uut_model.startswith(model):
                return model
    return None

model_def = {
    'acq1001': {
        'sites': 1,
    },
    'acq1002': {
        'sites': 2,
    },
    'acq1102': {
        'sites': 2,
    },
    'acq2106': {
        'sites': 6,
    },
    'acq2206': {
        'sites': 6,
    },
    'z7io'   : {
        'sites': 2,
    },
}

# Main
logger.info("Start")

uutname = PVUtil.getString(pvs[0]).lower()
model = get_model(uutname)


if model:
    time.sleep(0.3)
    macros = get_macros(display)
    macros.UUT = uutname

    PVUtil.writePV('loc://MODEL', model, timeout)
    macros.MODEL = model

    nsites = model_def[model]['sites']
    PVUtil.writePV('loc://NSITES', nsites, timeout)
    macros.NSITES = nsites

    sites = {}
    sitelist = read_pv("{}:SITELIST".format(uutname))

    if sitelist:
        sites = {int(k): v for k, v in (site.split('=') for site in sitelist.split(',', 1)[1].split(','))}
        site_str = ','.join(map(str, sites.keys()))
        PVUtil.writePV('loc://SITES', site_str, timeout)
        macros.SITES = site_str

    for site in range(1, 6 + 1):
        pvname = "SITE_{}_MODEL".format(site)
        site_model = sites[site] if site in sites else "none"
        PVUtil.writePV("loc://{}".format(pvname), str(site_model), timeout)
        macros[pvname] = site_model

    set_macros(display, macros)

logger.info("Complete {:0.2f}s".format(time.time() - t0))
