from RsInstrument import *
import numpy as np
import scipy as sp
import pandas as pd
import math
import matplotlib.pyplot as plt
import time
from datetime import datetime

def ToComplex(Data):
    Data = np.array(Data)
    if len(Data) % 2 == 0:
        Real = Data[::2]
        Imag = Data[1::2]
        return Real + 1j * Imag
    else:
        print('Odd')
        return Data

# For å koble til VNA kan det være greit å skrive IP adressen inn i browsern (http://169.254.212.142/)

ANT = 'Antenne2'
IFBW  = 1000      # Hz
POWER = 12   # dBm
PREAMP = 30  # dB
STEPSIZE = 1e6 # Hz

resource_string = 'TCPIP::169.254.212.142::hislip0::INSTR'
vna = RsInstrument(resource_string, id_query=True, reset=False) 


print('VNA name:', vna.query('*IDN?'))

# 2. Reseting the VNA to basic fundamentals
# vna.write('*CLS')
# vna.write('*RST')
# vna.write('SYSTem:PRESet')   # Set the VNA to its preset
vna.visa_timeout = 60*60*1e3 # En time før programmet stopper


# 3. Setting the settings
vna.write('SENSe:FREQuency:STARt 5.5e9')        # Start freq
vna.write('SENSe:FREQuency:Stop  6e9')       # Stopp freq
vna.write(f'SENSe:SWEep:STEP {STEPSIZE}')       # Step  size
vna.write(f'SENS:BAND {IFBW}Hz')                # Set the IFBW
vna.write('OUTPut:DPOR PORT1')                  # Set the output port
vna.write(f'SOUR:POW {POWER}dBm')               # Set the Power
vna.write('SENSe:PAMPlifier2 On')               # Turn on pre-amplifier 2
vna.write(f'SENSe:PAMPlifier2:VALue {PREAMP}')   # Sets pre-amp 2 
vna.write('INIT:CONT ON')              # Set continuous sweep mode



# 4. Measuerment 
t0 = time.time()
vna.write('CALCulate1:PARameter:SDEFine "Trc1", "S21"')
vna.write('INIT:IMM')                   # Start measurement
vna.write('DISPlay:WINDow:TRACe1:FEED "Trc1"') # Shows the screen
vna.write('INIT; *WAI')
data = vna.query_bin_or_ascii_float_list('CALC:DATA? SDATA')
Result = ToComplex(data) # Complex Samples
t1 = time.time()

print("Measurement time:", t1 - t0, "seconds")



# # 5. Plot
freq = np.arange(5500, 6000+STEPSIZE/1e6, STEPSIZE/1e6)
# print(len(freq))
# plt.figure(1)
# plt.plot(freq, 20*np.log10(np.abs(Result)))
# plt.title('|S21|')
# plt.xlabel('Frequency')
# plt.ylabel('dB')


Time = 1/freq
# plt.figure(2)
# plt.plot(Time, 20*np.log10(np.abs(sp.fft.ifft(Result))))
# plt.title('Time domain |S21|')
# plt.xlabel('time [us]')
# plt.ylabel('dB')
# plt.show()


H = Result
h = np.fft.ifft(Result)

# 6. Save data
if 1:
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") 
    # filename = f"Data\S21_{timestamp}_Horn_V_1KHz"
    # filename = f"Data5_4_mars_V/S21_el+90_ho+180_Omnislot" 
    filename = f'Data1_4_mars_V/Horn_Ref'
    np.save(f"{filename}.npy", Result)  # saves as binary .npy file 

    # filename = f"Data\S21_{ANT}_{IFBW}Hz_V.csv"
    data_to_save1 = np.column_stack((freq, 20*np.log10(np.abs(H)), np.angle(H, deg=True)))
    data_to_save2 = np.column_stack((Time, 20*np.log10(np.abs(h)), np.angle(h, deg=True)))
    np.savetxt(f'{filename}.csv', data_to_save1, delimiter=', ', header='Freq[MHz], Mag[dB], Angle[deg]')
    # np.savetxt(f'{filename}.csv', data_to_save2, delimiter=', ', header='Time[us], Mag[dB], Angle[deg]')

print('Ferdig')
