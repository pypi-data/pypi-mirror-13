#! python
from __future__ import print_function, division
'''
Physical constants
'''
from scipy.constants import m_e, e, epsilon_0, mu_0, c, h, hbar, alpha, Rydberg

# mass
m_Ps = 2.0 * m_e           # neglects binding energy
# Rydberg
Ryd_Ps = Rydberg / 2.0
# Bohr radius
a_0 = hbar / (m_e * c * alpha)
# Ps Bohr raidus
a_Ps = 2.0 * a_0
# ground-state decay rate
decay_pPs = 7.9896178e9    # Phys. Rev. A 68 (2003) 032512
decay_oPs = 7.039968e6     # Phys. Rev. Lett. 85 (2000) 3065
# ground-state lifetime
tau_pPs = 1.0/decay_pPs
tau_oPs = 1.0/decay_oPs
# ground-state hyperfine splitting
nu_hfs = 2.033942e11       # Phys. Lett. B 734 (2014) 338
En_hfs = h * nu_hfs
