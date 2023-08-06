'''
The Bohr model of positronium
'''
import positronium.constants as constants

def En(n1=1, n2=float('inf'), **kwargs):
    '''
    Calculate the interval between energy levels n1 and n2
    according to the Bohr model, i.e. the Rydberg formula.
    
    kwargs:
        unit:
            J, eV, meV, ueV, au (Hartree),          [energy]
            Hz, kHz, MHz, GHz, THz, PHz, EHz,       [frequency]
            m, cm, mm, um, nm, A, pm, fm,           [vacuum wavelength]
            m^-1, cm^-1.                            [wavenumber] 

    defaults:
        n1 = 1
        n2 = infinity
        unit='eV'
            
    '''
    rescale = {'J': (lambda x: x*constants.h*constants.c),
               'eV': (lambda x: x*constants.h*constants.c/ constants.e),
               'meV': (lambda x: x*constants.h*constants.c/ (constants.e * 1e-3)),
               'ueV': (lambda x: x*constants.h*constants.c/ (constants.e * 1e-6)),
               'au': (lambda x: x / (2 * constants.Rydberg)),
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
    unit = kwargs.get('unit', 'eV')
    if unit not in rescale:
        raise KeyError('"' + unit + '" is not recognised as a suitable unit. See' +
                               ' docstring for unit list.')
    else:
        En = (constants.Ryd_Ps) * (1.0/(n1**2) - 1.0/(n2**2))
        try:
            result = rescale[unit](En)
        except ZeroDivisionError:
            result = float('inf')
        return result
    
def radius(n=1, **kwargs):
    '''
    Return n^2 * a_Ps, where a_Ps is the Bohr radius for positronium (2 * a_0). 
    
    kwargs:
        unit:
            m, cm, mm, um, nm, A, pm, fm, (SI)
            au (atomic units).
    
    defaults:
        n = 1
        unit = 'm'
    
    '''
    rescale = {'m': (lambda x: x),
               'cm': (lambda x: x * 1e2),
               'mm': (lambda x: x * 1e3),
               'um': (lambda x: x * 1e6),
               'nm': (lambda x: x * 1e9),
               'A': (lambda x: x * 1e10),
               'pm': (lambda x: x * 1e12),
               'fm': (lambda x: x * 1e15), 
               'au': (lambda x: x / constants.a_0)
                }
    unit = kwargs.get('unit', 'm')
    if unit not in rescale:
        raise KeyError('"' + unit + '" is not recognised as a suitable unit. See' +
                               ' docstring for unit list.')
    else:
        return rescale[unit](n**2 * constants.a_Ps)