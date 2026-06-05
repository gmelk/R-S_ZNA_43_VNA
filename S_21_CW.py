from RsInstrument import *
import numpy as np
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



resource_string = 'TCPIP::169.254.212.142::hislip0::INSTR'
START_FREQ = 0.5e9
STOPP_FREQ = 30e9
STEP       = 10e6
SAMPLES    = 3
freq = np.arange(START_FREQ, STOPP_FREQ+STEP, STEP)





vna = RsInstrument(resource_string, id_query=True, reset=False) 




print('VNA name:', vna.query('*IDN?'))

# 2. Reseting the VNA to basic fundamentals
vna.write('*CLS')
vna.write('*RST')
vna.write('SYSTem:PRESet')   # Set the VNA to its preset
vna.visa_timeout = 60*60*1e3 # En time

# 3. Setting the settings
vna.write(f'CALCulate1:PARameter:SDEFine "Trc1", "S21"') # Set up the trace
vna.write('OUTPut:DPOR PORT1')            # Set the output port
vna.write('SENS:SWE:TYPE POIN')           # Set CW sweep mode
vna.write(f'SENS:SWE:POIN {SAMPLES}')     # Set the number of sweep points
vna.write(f'SENS:BAND {10e0}Hz')          # Set the IFBW
vna.write(f'SOUR:POW {12}dBm')            # Set the Power
vna.write('SENSe:PAMPlifier2 ON')         # Turn on pre-amplifier 2
vna.write('SENSe:PAMPlifier2:VALue 25')   # Sets pre-amp 2 


vna.write('INIT:CONT ON')              # Set continuous sweep mode
# vna.write('DISPlay:WINDow:TRACe1:FEED "Trc1"')



# 4. Measuerment 
Result = np.zeros(np.size(freq), dtype=complex)
t0 = time.time()
for i, f in enumerate(freq):
    vna.write(f'SENS:FREQ:CW {f}') # Set CW frequency to 1 GHz
    vna.write('INIT:IMM')                   # Start measurement
    vna.write('INIT; *WAI')                 # Weight    
    data = vna.query_bin_or_ascii_float_list('CALC:DATA? SDATA')
    Meas = ToComplex(data) # Complex Samples
    Result[i] = np.mean(Meas)
t1 = time.time()

print("Measurement time:", t1 - t0, "seconds")

# 5. Plot
freq = np.linspace(0.5, 18, len(Result))
plt.figure(1)
plt.plot(freq, 20*np.log10(np.abs(Result)))
plt.title('S21')
plt.xlabel('Frequency')
plt.ylabel('dB')
plt.show()


# 6. Save data
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") 
filename = f"S11_{timestamp}" 
np.save(f"{filename}.npy", Result)  # saves as binary .npy file 