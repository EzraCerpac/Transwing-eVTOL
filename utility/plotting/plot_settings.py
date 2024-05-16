import matplotlib.pyplot as plt

# Define Standard Units
fsize = 14
tsize = 10
tdir = 'in'
major = 5.0
minor = 3.0
style = 'default'

# Set all parameters for the plot
def set_plot_params():
    """
    Set all parameters for the plot.
    """
    plt.style.use(style)
    # plt.rcParams['text.usetex'] = True
    plt.rcParams['font.size'] = fsize
    plt.rcParams['legend.fontsize'] = tsize
    # plt.rcParams['mathtext.fontset'] = 'stix'
    # plt.rcParams['font.family'] = 'times'
    plt.rcParams['xtick.direction'] = tdir
    plt.rcParams['ytick.direction'] = tdir
    plt.rcParams['xtick.major.size'] = major
    plt.rcParams['xtick.minor.size'] = minor
    plt.rcParams['ytick.major.size'] = major
    plt.rcParams['ytick.minor.size'] = minor
