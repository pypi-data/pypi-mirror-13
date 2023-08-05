'''
The Bohr model of positronium
'''
import positronium.constants as constants

def En(n1, n2=float('inf'), **kwargs):
    '''
    Calculate the interval between energy levels n1 and n2 (default = infinity)
    according to the Bohr model, i.e. the Rydberg formula.
    
    Return the interval in units of:
        energy (J, eV, meV, ueV),
        frequency (Hz, kHz, MHz, GHz, THz, PHz, EHz),
        wavelength (m, cm, mm, um, nm, A, pm, fm),
        wavenumbers (m^-1, cm^-1). 

        Defaults:
            units='nm'
    '''
    units = kwargs.get('units', 'nm')
    En = (constants.Ryd_Ps) * (1.0/(n1**2) - 1.0/(n2**2))
    rescale = {'J': (lambda x: x*constants.Planck*constants.c),
               'eV': (lambda x: x*constants.Planck*constants.c/ constants.e),
               'meV': (lambda x: x*constants.Planck*constants.c/ (constants.e * 1e-3)),
               'ueV': (lambda x: x*constants.Planck*constants.c/ (constants.e * 1e-6)),
               'Hz': (lambda x: x*constants.c),
               'kHz': (lambda x: x*constants.c / 1e3),
               'MHz': (lambda x: x*constants.c / 1e6),
               'GHz': (lambda x: x*constants.c / 1e9),
               'THz': (lambda x: x*constants.c / 1e12),
               'PHz': (lambda x: x*constants.c / 1e15),
               'EHz': (lambda x: x*constants.c / 1e18),
               'm': (lambda x: 1.0/x),
               'cm': (lambda x: 1.0/(x * 1e-2)),
               'mm': (lambda x: 1.0/(x * 1e-3)),
               'um': (lambda x: 1.0/(x * 1e-6)),
               'nm': (lambda x: 1.0/(x * 1e-9)),
               'A': (lambda x: 1.0/(x * 1e-10)),
               'pm': (lambda x: 1.0/(x * 1e-12)),
               'fm': (lambda x: 1.0/(x * 1e-15)),
               'm^-1': (lambda x: x),
               'cm^-1': (lambda x: x * 1e-2),
              }
    return rescale[units](En)
