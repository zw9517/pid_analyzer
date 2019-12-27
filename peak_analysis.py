import csv
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import scipy as scipy
from scipy import optimize
from matplotlib.ticker import AutoMinorLocator
from matplotlib import gridspec
import matplotlib.ticker as ticker

data = []
T = []
with open('data_log.csv', mode='r') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    line_count = 0
    for row in csv_reader:
        if line_count == 0:
            print(f'Column names are {", ".join(row)}')
            line_count += 1
        T.append(float(row["Time"]))
        data.append(float(row["Sensor1"]))
        line_count += 1
    print(f'Processed {line_count} lines.')

fig = plt.figure(figsize=(4,3))
gs = gridspec.GridSpec(1,1)
ax1 = fig.add_subplot(gs[0])
ax1.plot(T,data,"ro")
fig.tight_layout()
fig.savefig("rawData.png", format="png",dpi=200)


amp1 = 500
sigma1 = 20
cen1 = 13
wid1 = 10

amp2 = 350
sigma2 = 10
cen2 = 20
wid2 = 1


def _1gaussian(x, amp1,cen1,sigma1):
    return amp1*(1/(sigma1*(np.sqrt(2*np.pi))))*(np.exp((-1.0/2.0)*(((T-cen1)/sigma1)**2)))


def _2gaussian(x, amp1,cen1,sigma1, amp2,cen2,sigma2):
    return amp1*(1/(sigma1*(np.sqrt(2*np.pi))))*(np.exp((-1.0/2.0)*(((T-cen1)/sigma1)**2))) + \
            amp2*(1/(sigma2*(np.sqrt(2*np.pi))))*(np.exp((-1.0/2.0)*(((T-cen2)/sigma2)**2)))


def _1Lorentzian(x, amp, cen, wid):
    return amp*wid**2/((x-cen)**2+wid**2)

def _3Lorentzian(x, amp1, cen1, wid1, amp2,cen2,wid2):
    return (amp1*wid1**2/((x-cen1)**2+wid1**2)) +\
            (amp2*wid2**2/((x-cen2)**2+wid2**2))


popt_2gauss, pcov_2gauss = scipy.optimize.curve_fit(_2gaussian, T, data, p0=[amp1, cen1, sigma1, amp2, cen2, sigma2])

perr_2gauss = np.sqrt(np.diag(pcov_2gauss))

pars_1 = popt_2gauss[0:3]
pars_2 = popt_2gauss[3:6]
gauss_peak_1 = _1gaussian(T, *pars_1)
gauss_peak_2 = _1gaussian(T, *pars_2)

# ax1.plot(T, _2gaussian(T, *popt_2gauss), 'k--')#,\
# fig.tight_layout()
# fig.savefig("fit2Gaussian.png", format="png",dpi=200)


popt_3lorentz, pcov_3lorentz = scipy.optimize.curve_fit(_3Lorentzian, T, data, p0=[amp1, cen1, wid1, \
                                                                                    amp2, cen2, wid2])

perr_3lorentz = np.sqrt(np.diag(pcov_3lorentz))

pars_1 = popt_3lorentz[0:3]
pars_2 = popt_3lorentz[3:6]
lorentz_peak_1 = _1Lorentzian(T, *pars_1)
lorentz_peak_2 = _1Lorentzian(T, *pars_2)


ax1.plot(T, _3Lorentzian(T, *popt_3lorentz), 'k--')
# peak 1
ax1.plot(T, lorentz_peak_1, "g")
ax1.fill_between(T, lorentz_peak_1.min(), lorentz_peak_1, facecolor="green", alpha=0.5)

# peak 2
ax1.plot(T, lorentz_peak_2, "y")
ax1.fill_between(T, lorentz_peak_2.min(), lorentz_peak_2, facecolor="yellow", alpha=0.5)
fig.tight_layout()
fig.savefig("fit3Lorentzian_peaks_resid.png", format="png",dpi=200)