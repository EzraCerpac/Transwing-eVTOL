import numpy as np
import matplotlib
import math as m
# matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from aircraft_models import rot_wing
from data.flight_data.mission_data import mission_data, cruise_data

Nominal_Voltage = 3.7 #V
Cut_Off_Voltage = 2.2 #V
System_Voltage = 710 #V
SOC_end = .20 # %
SOC_start = .80 #%
rho_E = 0.3 #kWh/Kg
n_pack = 6 #justufy
power = mission_data['power'].to_numpy()
time = mission_data['time'].to_numpy()
# Total_Energy = rot_wing.data.mission_profile.energy #KWh
W_tot = 400
C_pack_init = (W_tot * rho_E * 10**3)/(System_Voltage * n_pack)
print(C_pack_init)
print("culo")
SOC = np.zeros(time.shape[0])
SOC[0] = SOC_start
Battery_efficiency = np.zeros(time.shape[0])
Battery_efficiency[0] = 1
Voltages = np.zeros(time.shape[0])
Voltages [0] = 760
I = 0
C_rate = 0
n = 192
epsilon = 10**(-6)
Voltage = System_Voltage
Capacities = []
rates = []
flag = True
C_pack_init_2 = 0
count = 0
list = [2.5, 2, 1, 0.05, 0.01]

def voltage():
    c = 0
    soc = np.arange(0.01, 1.01,0.01)
    C_Rates = [29990.4, 59980.8*2, 119961.6*2, 2 * 1000000.66, 1000000.66]
    for l in C_Rates:
        print(l)
        Voltages_1 = []
        for i in soc:
            k = 1
            Voltage = 710
            P_bat_new = []
            P_bat_new.append(1999)
            while k >= 0:
                I = (l / n_pack) / (System_Voltage)
                I_sec = (l) / (System_Voltage * n * n_pack)
                C_rate = (I) / (C_pack_init)
                U_oc = -1.031 * m.e ** (-35 * i) + 3.685 + 0.2156 * i - 0.1178 * i ** 2 + 0.321 * i ** 3
                R_i = 0.1562 * m.e ** (-24.37 * i) + 0.07446
                R_ts = 0.3208 * m.e ** (-29.14 * i) + 0.04669
                R_tl = 6.6030 * m.e ** (-155.2 * i) + 0.04984
                R_tot = R_i + R_tl + R_ts
                U_cell = U_oc - R_tot * I_sec
                U_new = U_cell * n
                if k == 1:
                    P_bat_new.append(I_sec * Voltage)
                if abs((P_bat_new[len(P_bat_new) - 1] - P_bat_new[len(P_bat_new) - 2])) < epsilon:
                    Voltages_1.append(Voltage/n)
                    break
                else:
                    Voltage = U_new
                    P_bat_new.append(I_sec * Voltage)
                    k = k + 1
        soc2 = [1-a for a in soc]
        plt.plot(soc2, Voltages_1, label ="C-Rate = {}".format(list[c]))
        plt.ylim(0,4.5)
        plt.ylabel("Voltage, $U$ [V]")
        plt.xlabel("Depth of Discharge, $DOD$ [%]")
        plt.grid()
        plt.legend()
        c = c + 1
    plt.savefig("DODvVoltage.png", dpi = 500)
    plt.show()
    print("AS")


voltage()
C_RATES = []
current = []
C_act = 0
V = []
for j in time[:-1]:
    k = 1
    Voltage = System_Voltage
    P_bat_new = []
    P_bat_new.append(1999)
    while k>=0:
        I = (power[count]/n_pack)/(Voltage)
        I_sec =  (power[count])/(Voltage*n*n_pack)
        C_rate = (I)/ (C_pack_init)
        U_oc = -1.031 * m.e ** (-35 * SOC[count]) + 3.685 + 0.2156 * SOC[count] - 0.1178 * SOC[count] ** 2 + 0.321 * SOC[count] ** 3
        R_i = 0.1562 * m.e ** (-24.37 * SOC[count]) + 0.07446
        R_ts = 0.3208 * m.e ** (-29.14 * SOC[count]) + 0.04669
        R_tl = 6.6030 * m.e ** (-155.2 * SOC[count]) + 0.04984
        R_tot = R_i + R_tl + R_ts
        U_cell = U_oc - R_tot * I_sec
        U_new = U_cell * n
        #DeltaS = -496.66 * SOC[count]**6 + 1729.4*SOC[count]**5 -2278*SOC[count]**4+1382.2*SOC[count]**3-380.47*SOC[count]**2+46.508*SOC[count]-10.692
        #R_0 = 0.01483 * SOC[count]**2 -0.02518*SOC[count] + 0.1036
        #Q_gen = I_sec*((U_oc - Voltage)-(T_bat*DeltaS)/(F*n_electrons))
        #Q_bat =


        if k==1:
            P_bat_new.append(I_sec * Voltage)
        if abs((P_bat_new[len(P_bat_new)-1] - P_bat_new[len(P_bat_new)-2])) < epsilon:
            print(I * Voltage / n)
            V.append(Voltage)
            current.append(I)
            C_RATES.append(C_rate)
            break
        else:
            Voltage = U_new
            P_bat_new.append(I_sec * Voltage)
            k = k+1
    if Voltage / n > Cut_Off_Voltage:
        if C_rate < 0.4:
            C_act = C_pack_init * (3.3333*C_rate**4 - 3.25*C_rate**3 + 1.1167*C_rate**2- 0.1825*C_rate + 1)
        else:
            C_act = C_pack_init * (-0.0125*C_rate + 0.9875)
        SOC[count+1] = SOC[count]-((I)/(C_act))*(time[count+1]-time[count])*(1/(60*60)) #convert from hours testa di cazzo
        Battery_efficiency[count+1] = 1 - ((I/n)**2 * R_tot)/(U_oc*(I/n))
    else:
        SOC[count+1] = SOC[count] - ((I)/(C_act))*(time[count+1]-time[count])*(1/60*60) #convert to hours testa di cazz
    count = count+1

take_off_start = 0
take_off_finish = 245
climb_start = 245
climb_end = 545
Cruise_Start = 545
Cruise_End = 1725
Descent_Start = 1545
Descent_End = 1916
Back_Transition_Start = 1945
Back_Transition_End = 2125
Landing_Start = 2125
Landing_End = 2165

plt.plot(time,SOC*100)
plt.xlabel("Time, $t$ [s]")
plt.ylabel("State of Charge, $SOC$ [%]")
plt.axvline(x = take_off_finish, linestyle = "dashed", color = "black")
plt.text(take_off_finish-75, 70, "Take-off", rotation = 90, fontsize = 12)
plt.axvline(x = climb_end, linestyle = "dashed", color = "black")
plt.text(climb_end-75, 70, "Climb", rotation = 90, fontsize = 12)
plt.axvline(x = Cruise_End, linestyle = "dashed", color = "black")
plt.text(Cruise_End-75, 70, "Cruise", rotation = 90, fontsize = 12)
plt.axvline(x = Descent_End, linestyle = "dashed", color = "black")
plt.text(Descent_End-75, 70, "Descent", rotation = 90, fontsize = 12)
plt.text(Descent_End+100, 70, "Landing", rotation = 90, fontsize = 12)
plt.grid()
plt.savefig("SOCvTime.png", dpi = 500)
plt.show()
plt.plot(time, Battery_efficiency*100)
plt.xlabel("Time [s]")
plt.ylabel("Efficiency [%]")
plt.show()
plt.plot(time[0:-1], V)
plt.xlabel("Time, $t$ [s]")
plt.ylabel("Voltage, $U$ [V]")
plt.axvline(x = take_off_finish, linestyle = "dashed", color = "black")
plt.text(take_off_finish-75, 745, "Take-off", rotation = 90, fontsize = 12)
plt.axvline(x = climb_end, linestyle = "dashed", color = "black")
plt.text(climb_end-75, 740, "Climb", rotation = 90, fontsize = 12)
plt.axvline(x = Cruise_End, linestyle = "dashed", color = "black")
plt.text(Cruise_End-75, 740, "Cruise", rotation = 90, fontsize = 12)
plt.axvline(x = Descent_End, linestyle = "dashed", color = "black")
plt.text(Descent_End-75, 740, "Descent", rotation = 90, fontsize = 12)
plt.text(Descent_End+100, 740, "Landing", rotation = 90, fontsize = 12)
plt.grid()
plt.savefig("VvTime.png", dpi = 500)
plt.show()
#plt.plot(time,power, color = "b")
#plt.show()
plt.plot(time[0:-1], current, color = "b")
plt.axvline(x = take_off_finish, linestyle = "dashed", color = "black")
plt.text(take_off_finish-75, 30, "Take-off", rotation = 90, fontsize = 12)
plt.axvline(x = climb_end, linestyle = "dashed", color = "black")
plt.text(climb_end-75, 30, "Climb", rotation = 90, fontsize = 12)
plt.axvline(x = Cruise_End, linestyle = "dashed", color = "black")
plt.text(Cruise_End-75, 30, "Cruise", rotation = 90, fontsize = 12)
plt.axvline(x = Descent_End, linestyle = "dashed", color = "black")
plt.text(Descent_End-75, 30, "Descent", rotation = 90, fontsize = 12)
plt.text(Descent_End+100, 30, "Landing", rotation = 90, fontsize = 12)
plt.plot(time[0:-1], C_RATES)
plt.show()
print(power)
plt.plot(time, power)
plt.show()
p = 0
# time finder