import matplotlib.pyplot as plt

from fft import fft, fft_power, ifft
from numpy import array, real
import math
import time
import cpt
import numpy


# data downloaded from http://www.sidc.be/DATA/yearssn.dat
print ' Moana Loa CO2 data from NOAA'
data_file_name = 'co2_mm_mlo.txt'
file = open(data_file_name, 'r')
lines = file.readlines()
file.close()
print ' read', len(lines), 'lines from', data_file_name

window = True   

yinput = []
xinput = []

for line in lines :
    if line[0] != '#' :
        try:
            words = line.split()
            xval = float(words[2])
            yval = float( words[4] )
            yinput.append( yval )
            xinput.append( xval )
        except ValueError :
            print 'bad data:',line
            
#Do a fit of the data

ecks= numpy.linspace(1960,2020,1000)
fit,co=numpy.polyfit(xinput,yinput,2,cov=True)
why= fit[0]*ecks**2+fit[1]*ecks+fit[2]
#plt.plot(ecks,why,label='Quadratic')
#variance = sum((data[i] - (fit[0]*dates[i]**2+fit[1]*dates[i]+fit[2]))**2 for i in range(len(data)))
#variance = math.sqrt(variance)/(len(data)-2)


#print numpy.sqrt(numpy.diag(co))
#print variance
#plt.legend(loc='upper left')

ydata=yinput
yinput= [yinput[i]-(fit[0]*xinput[i]**2+xinput[i]*fit[1]+fit[2]) for i in xrange(len(yinput))]

        




                       
yorig=yinput
padlength=0
N = len(yinput)
log2N = math.log(N, 2)
if log2N - int(log2N) > 0.0 :
    print 'Padding with zeros!'
    pads = [0.0] * (pow(2, int(log2N)+1) - N)
    yinput = yinput + pads
    
    N = len(yinput)
    print 'Padded : '
    print len(yinput)
    padlength=len(pads)
    # Apply a window to reduce ringing from the 2^n cutoff
    
    if window : 
        for iy in xrange(len(yinput)) :
            yinput[iy] = yinput[iy] * (0.5 - 0.5 * math.cos(2*math.pi*iy/float(N-1)))

            

y = array( yinput ) 
x = array([ float(i) for i in xrange(len(y)) ] )
Y = fft(y)


maxfreq = 50
# Now smooth the data
for iY in range(maxfreq, len(Y)-maxfreq ) :
    Y[iY] = complex(0,0)
    #Y[iY] = Y[iY] * (0.5 - 0.5 * math.cos(2*math.pi*iY/float(N-1))) 

    #for iY in range(0,N) : 
    #    Y[iY] = Y[iY] * math.exp(-1.0*iY / 50.0)

powery = fft_power(Y)
powerx = array([ float(i) for i in xrange(len(powery)) ] )

Yre = [math.sqrt(Y[i].real**2+Y[i].imag**2) for i in xrange(len(Y))]


            

ysmoothed = ifft(Y)
ysmoothedreal = real(ysmoothed)






if window : 
    for iy in range(1,len(yinput)-1) :
        ysmoothedreal[iy] = ysmoothedreal[iy] / (0.5 - 0.5 * math.cos(2*math.pi*iy/float(N-1)))
        y[iy]= y[iy] / (0.5 - 0.5 * math.cos(2*math.pi*iy/float(N-1)))


ax1 = plt.subplot(2, 1, 1)
y= y[:(N-padlength)]
ysmoothedreal= ysmoothedreal[:(N-padlength)]
yinput=yinput[:(N-padlength)]

ysmoothedreal= [ysmoothedreal[i]+(fit[0]*xinput[i]**2+xinput[i]*fit[1]+fit[2]) for i in xrange(len(ysmoothedreal))]
y= [y[i]+(fit[0]*xinput[i]**2+xinput[i]*fit[1]+fit[2]) for i in xrange(len(ysmoothedreal))]

p1, = plt.plot( xinput, y )
p2, = plt.plot( xinput, ysmoothedreal )
#p3, = plt.plot(xinput,ydata)
plt.xlim([1960,2013])
plt.ylim([300,400])
ax1.legend( [p1,p2], ['Original', 'Smoothed'], loc='lower right' )

ax2 = plt.subplot(2, 1, 2)
p3, = plt.plot( powerx, powery )
p4, = plt.plot( x, Yre )
ax2.legend( [p3, p4], ["Power", "Magnitude"] )
plt.yscale('log')


plt.show()
#fits
'''
ecks= numpy.linspace(1960,2020,1000)
fit,co=numpy.polyfit(dates,data,2,cov=True)
why= fit[0]*ecks**2+fit[1]*ecks+fit[2]
plt.plot(ecks,why,label='Quadratic')
variance = sum((data[i] - (fit[0]*dates[i]**2+fit[1]*dates[i]+fit[2]))**2 for i in range(len(data)))
variance = math.sqrt(variance)/(len(data)-2)
print fit
print numpy.sqrt(numpy.diag(co))
print variance
plt.legend(loc='upper left')
'''