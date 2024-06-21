import numpy as np
import matplotlib.pyplot as plt
from noiseEst import toimp_dist, toimp_speed

from data.thrust_points.thrust_coefficient import thrust_coefficient
from utility.plotting import show, save

Vcruise = 200/3.6  # [m/s]
D = 2.1


Jtot = np.array([
    7.0861678, 5.66893424, 4.724111867, 4.049238743, 3.5430839, 3.149407911, 2.83446712, 2.576788291,
    2.362055933, 2.180359323, 2.024619372, 1.889644747, 1.77154195, 1.6673336, 1.574703956, 1.4918248,
    1.41723356, 1.349746248, 1.288394146, 1.232377009, 1.181027967, 1.133786848, 1.090179662, 1.049802637,
    1.012309686, 0.977402455, 0.944822373, 0.914344232, 0.885770975, 0.85892943, 0.8336668, 0.809847749,
    0.787351978, 0.766072195, 0.7459124, 0.726786441, 0.70861678, 0.691333444, 0.674873124, 0.6591784,
    0.644197073, 0.629881582, 0.616188504, 0.603078111, 0.590513983, 0.578462678, 0.566893424, 0.555777867,
    0.545089831, 0.534805117, 0.524901319, 0.515357658, 0.506154843, 0.497274933, 0.488701228, 0.480418156,
    0.472411187, 0.464666741, 0.457172116, 0.449915416, 0.442885488, 0.436071865, 0.429464715, 0.423054794,
    0.4168334, 0.410792336, 0.404923874, 0.399220721, 0.393675989, 0.388283167, 0.383036097, 0.377928949,
    0.3729562, 0.368112613, 0.363393221, 0.358793306, 0.35430839, 0.349934212, 0.345666722, 0.341502063,
    0.337436562, 0.33346672, 0.3295892, 0.325800818, 0.322098536, 0.318479452, 0.314940791, 0.311479903,
    0.308094252, 0.304781411, 0.301539055, 0.29836496, 0.295256992, 0.292213105, 0.289231339, 0.28630981,
    0.283446712, 0.280640309, 0.277888933, 0.275190983, 0.272544915, 0.26994925, 0.267402559, 0.264903469,
    0.262450659, 0.260042855, 0.257678829, 0.255357398, 0.253077421, 0.250837798, 0.248637467, 0.246475402,
    0.244350614, 0.242262147, 0.240209078, 0.238190514, 0.236205593, 0.234253481, 0.232333371, 0.230444481,
    0.228586058, 0.22675737, 0.224957708, 0.223186387, 0.221442744, 0.219726133, 0.218035932, 0.216371536,
    0.214732358, 0.213117829, 0.211527397, 0.209960527, 0.2084167, 0.20689541, 0.205396168, 0.203918498,
    0.202461937, 0.201026037, 0.199610361, 0.198214484, 0.196837994, 0.195480491, 0.194141584, 0.192820893,
    0.191518049, 0.190232693, 0.188964475, 0.187713054, 0.1864781, 0.185259289, 0.184056307, 0.182868846,
    0.18169661, 0.180539307, 0.179396653, 0.178268372, 0.177154195, 0.176053858, 0.174967106, 0.173893688,
    0.172833361
])

# with pitch increase from 20deg to 65deg, +5deg at each step
# obviously 35deg is optimal here
CtsHover = np.array([
    .27, .30, .31, .33, .32, .31, .27, .26, .22, .19
])


n = np.linspace(50, 6000, 1000)  # [rpm]
beta = np.linspace(20, 65, 10)  # [deg]


maxvalue = [1, 1.25, 1.5, 1.84, 2.19, 2.6, 3.11, 3.8, 4.64, 5.76]

# plt.figure()
# w = 0
# for b in beta:
#     Jcurrent = Jtot[(Jtot >= 0.3) & (Jtot <= maxvalue[w])]
#     current = 'J'+str(int(b))
#     n = 1/(Jcurrent*D/Vcruise*0.02)
#     T = 1.225*thrust_coefficient(Jcurrent, b)*(n*0.02)**2*D**4
#     plt.plot(n, thrust_coefficient(Jcurrent, b), label=current)
#     w += 1
# plt.legend()
# plt.show()
# w = 0
# for b in beta:
#     Jcurrent = Jtot[(Jtot >= 0.3) & (Jtot <= maxvalue[w])]
#     current = 'J'+str(int(b))
#     n = 1/(Jcurrent*D/Vcruise*0.02)
#     T = 1.225*thrust_coefficient(Jcurrent, b)*(n*0.02)**2*D**4
#     plt.plot(n, T, label=current)
#     w += 1
# plt.legend()
# plt.ylim(0, 6000)
# plt.xlim(125, 2000)
# plt.show()
# w = 0
# for b in beta:
#     Jcurrent = Jtot[(Jtot >= 0.3) & (Jtot <= maxvalue[w])]
#     current = 'J'+str(int(b))
#     n = 1/(Jcurrent*D/Vcruise*0.02)
#     T = 1.225*thrust_coefficient(Jcurrent, b)*(n*0.02)**2*D**4
#     plt.plot(Jcurrent, thrust_coefficient(Jcurrent, b), label=current)
#     w += 1

#
# plt.legend()
# plt.show()

@show
@save
def plot_thrust_coefficient_over_beta() -> (plt.Figure, plt.Axes):
    fig, ax = plt.subplots(figsize=(6, 4))
    beta = np.linspace(20, 65, 101)
    cts = thrust_coefficient(0.3, beta)
    ax.plot(beta, cts)
    ax.set_xlabel(r'Pitch angle, $\beta$ [deg]')
    ax.set_ylabel(r'Thrust coefficient, $C_T$ [-]')

    opt_beta = beta[np.argmax(cts)]
    opt_cts = np.max(cts)
    ax.plot(opt_beta, opt_cts, 'ro')
    # add a textbox
    ax.annotate(
        r'$\beta_{\text{opt}} = %.1f\degree$' % opt_beta + '\n' + r'$C_{\text{T}_{\text{opt}}} = %.2f$' % opt_cts,
        (opt_beta, opt_cts),
        (opt_beta + 3, opt_cts - 0.15),
        arrowprops=dict(arrowstyle='->'),
        bbox=dict(boxstyle='round,pad=0.5', facecolor='white', edgecolor='black', alpha=0.8)
    )

    ax.set_ylim(bottom=0)
    ax.grid()
    return fig, ax

if __name__ == '__main__':
    plot_thrust_coefficient_over_beta()
