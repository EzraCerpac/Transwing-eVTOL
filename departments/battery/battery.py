from aircraft_models import rot_wing

#print(rot_wing.data.mission_profile.

Nominal_Voltage = 3.7 #V
Cut_Off_Voltage = 2.8 #V
System_Voltage = 710 #V
SOC_end = 20 # %
SOC_start = 80 #%
rho_E = 0.3 #kWh/Kg
n_pack = 6 #justufy
Total_Energy = rot_wing.data.mission_profile.energy #KWh
W_tot = Total_Energy / rho_E
print(W_tot)

C_pack = (W_tot * rho_E)/(System_Voltage * n_pack)
Power =