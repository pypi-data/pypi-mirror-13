'''
Physical constants
'''
from scipy.constants import m_e, e, epsilon_0, mu_0, c, h, hbar, alpha, Rydberg

# mass
m_Ps = 2.0 * m_e
# Rydberg
Ryd_Ps = Rydberg / 2.0
# Bohr radius
a_0 = hbar / (m_e * c * alpha)
# Ps Bohr raidus
a_Ps = 2 * a_0