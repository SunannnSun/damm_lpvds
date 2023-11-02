import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

from matplotlib.ticker import MaxNLocator
from matplotlib.ticker import FormatStrFormatter


font = {'family' : 'Times',
         'size'   : 18
        #  'serif':  'cmr10'
         }
mpl.rc('font', **font)
mpl.rc('text', usetex = True)



size = np.array([100, 200, 500, 700, 1000, 2000, 3000, 5000, 7000])

time_damm = np.array([0.31, 0.5, 1.5, 3, 5, 8, 12, 15, 18])
err_damm = np.array([0.1, 0.3, 0.6, 1, 1.5, 3, 4, 5, 6])

time_pcgmm = np.array([1, 3, 5, 10, 50, 350, 900, 2100, 3800])
err_pcgmm_top = np.array([0.8, 2, 3, 8, 30, 250, 760, 1900, 3600])
err_pcgmm_bot = np.array([2.5, 6, 8, 15, 85, 650, 1500, 3100, 4500])



time_gmm_p = np.array([0.2, 0.3, 0.6, 0.8, 1, 1.5, 2, 2.5, 3])
# err_gmm_p =  np.random.randn(time_damm.shape[0]) * time_damm/5


time_gmm_pv = np.array([0.3, 0.4, 1, 1, 1.2, 1.8, 2.2, 3, 3.3])
# err_gmm_pv =  np.random.randn(time_damm.shape[0]) * time_damm/5


fig, ax = plt.subplots(figsize=(12, 6))

ax.plot(size, time_damm, '-', c='seagreen', linewidth=3, label ='DAMM')
ax.plot(size, time_pcgmm, '-', c='darkslateblue', linewidth=3, label ='PC-GMM')
ax.plot(size, time_gmm_p, '-', c='peru', linewidth=3, label='GMM-P')
ax.plot(size, time_gmm_pv, '-', c='firebrick', linewidth=3, label='GMM-PV')



ax.fill_between(size, time_damm - err_damm, time_damm + err_damm,  facecolor = 'seagreen', alpha=0.3)

ax.fill_between(size, err_pcgmm_bot, err_pcgmm_top,  facecolor = 'darkslateblue', alpha=0.3)

# ax.fill_between(size, time_gmm_p - err_gmm_p, time_gmm_p + err_gmm_p,  facecolor = 'darkslateblue', alpha=0.3)

# ax.fill_between(size, time_gmm_pv - err_gmm_pv, time_gmm_pv + err_gmm_pv,  facecolor = 'firebrick', alpha=0.3)


ax.set_yscale('log')

ax.set_title("Comparison of Time vs. Observation Size", fontsize=25)
ax.set_xlabel('Observation Size', fontsize=22)
ax.set_ylabel("Time (Sec)", fontsize=22)

ax.legend(loc='upper left', fontsize=18)


# ax.xaxis.set_major_locator(MaxNLocator(nbins=5))
# ax.yaxis.set_major_locator(MaxNLocator(nbins=5))
# ax.xaxis.set_major_formatter(FormatStrFormatter('%.1f'))
# ax.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.spines['left'].set_visible(True)
ax.spines['bottom'].set_visible(True)

plt.grid( color = 'k', linestyle = '--', linewidth = 0.5, alpha = 0.5)


plt.show()