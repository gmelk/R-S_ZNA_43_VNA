"""
Measuer the S-parameters on the VNA
"""

# S12 and S11 measuement


from RsInstrument import *
import numpy as np
import matplotlib.pyplot as plt
import time

def ToComplex(Data):
    Data = np.array(Data)
    if len(Data) % 2 == 0:
        Real = Data[::2]
        Imag = Data[1::2]
        return Real + 1j * Imag
    else:
        print('Odd')
        return Data

f1 = 0.3e9
f2 = 6.5e9

IFBW  = 1000 # Hz
POWER = 0   # dBm
PREAMP = 0  # dB
STEPSIZE = 1e6 # Hz

resource_string = 'TCPIP::169.254.212.142::hislip0::INSTR'
vna = RsInstrument(resource_string, id_query=True, reset=False) 
print('Connected to VNA:', vna.query('*IDN?'))
vna.visa_timeout = 60*60*1e3 # En time før programmet stopper

# 3. Setting the settings
vna.write(f'SENSe:FREQuency:STARt {f1}')        # Start freq
vna.write(f'SENSe:FREQuency:Stop  {f2}')       # Stopp freq
vna.write(f'SENSe:SWEep:STEP {STEPSIZE}')       # Step  size
vna.write(f'SENS:BAND {IFBW}Hz')                # Set the IFBW
# vna.write('OUTPut:DPOR PORT1')                  # Set the output port
# vna.write(f'SOUR:POW {POWER}dBm')               # Set the Power
# vna.write('SENSe:PAMPlifier2 On')               # Turn on pre-amplifier 2
# vna.write(f'SENSe:PAMPlifier2:VALue {PREAMP}')  # Sets pre-amp 2 
vna.write('INIT:CONT ON')                      # Set continuous sweep mode


freq = np.arange(f1, f2+STEPSIZE, STEPSIZE)
S_Param = ['S11', 'S21', 'S12', 'S22']
S_Results = np.zeros((len(S_Param), len(freq)), dtype=complex)

# Metode 1 
if True:
    t0 = time.time()
    for i, S in enumerate(S_Param):
        vna.write(f'CALCulate1:PARameter:SDEFine "Trc1", "{S}"')
        vna.write('INIT:IMM')                   # Start measurement
        vna.write('DISPlay:WINDow:TRACe1:FEED "Trc1"') # Shows the screen
        vna.write('INIT; *WAI')
        data = vna.query_bin_or_ascii_float_list('CALC:DATA? SDATA')
        S_Results[i, :] = ToComplex(data) # Complex Samples

        t1 = time.time()
        print(f"\tMeasurement time {S}:", t1 - t0, "seconds")

    print(f'Metode 1 tid: \t{ t1 - t0} sekunder')
# Metode 2
else:
    t0 = time.time()
    for i, S in enumerate(S_Param):
        Trace = f'Trc{i}'
        # vna.write(f'CALC:PAR:SDEF "{Trace}", "{S}"')
        vna.write(f'CALCulate1:PARameter:SDEFine "{Trace}", "{S}"')
        # vna.write('DISPlay:WINDow:TRACe1:FEED "Trc1"') # Shows the screen
    vna.write('INIT:IMM')                   # Start measurement
    vna.query_opc()                         # Wait for sweep to finish
    
    for i, S in enumerate(S_Param):
        Trace = f'Trc{i}'
        vna.write(f'CALC:PAR:SEL "{Trace}"')        # Select trace 
        data = vna.query_bin_or_ascii_float_list('CALC:DATA? SDATA')
        S_Results[i, :] = ToComplex(data) # Complex Samples
        t1 = time.time()
        print(f"Measurement time {S}:", t1 - t0, "seconds")
    print(f'Metode 2 tid: \t{ t1 - t0} sekunder')


np.save('Data_Til_Lewis/Data4.97m_Port1Serie8_Port2Serie11.npy', S_Results)

if 1:
    # Plot Amplitude
    plt.figure('Sparam - Amplitude')
    amplitude = 20*np.log10(np.abs(S_Results))
    for i in range(amplitude.shape[0]):
        plt.plot(freq, amplitude[i], label=S_Param[i])
    plt.title("Amplitude of S-parameters")
    plt.xlabel("Frequency (GHz)")
    plt.ylabel("Amplitude")
    plt.legend(loc='upper right', bbox_to_anchor=(1.2, 1.0), fontsize='small')
    plt.tight_layout()
    plt.grid(True)
    plt.show()

    # Plot Phase
    plt.figure('Sparam - Phase')
    phase = np.angle(S_Results)
    for i in range(phase.shape[0]):
        plt.plot(freq, phase[i], label=S_Param[i])
    plt.title("Phase of S-parameters")
    plt.xlabel("Frequency (GHz)")
    plt.ylabel("Phase (radians)")
    plt.legend(loc='upper right', bbox_to_anchor=(1.2, 1.0), fontsize='small')
    plt.tight_layout()
    plt.grid(True)
    plt.show()