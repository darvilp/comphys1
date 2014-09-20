import math
import matplotlib.pyplot as plt
import cpt
import numpy

def sine_transform(data):
    """Return Fourier sine transform of a real data vector"""
    N = len(data)
    transform = [ 0 ] * N
    for k in range(N):
        for j in range(N):
            angle = math.pi * k * j / N
            transform[k] += data[j] * math.sin(angle)
    return transform

file_name = "co2_mm_mlo.txt"
file = open(file_name, "r")
lines = file.readlines()
file.close()

dates = []
data = []
logdata = []
for line in lines:
    if len(line) > 4:
        try:
            year = int(line[0:4])
            if year > 1957 and year < 2013:
                words = str.split(line)
                
                ppm = float(words[3]) #take averages instead
                
                
                if ppm > 0: 
                    logdata.append(math.log(ppm))
                    data.append(ppm)
                    dates.append(float(words[2]))
        except ValueError:
            pass

print " read", len(data), "values from", file_name


transform = sine_transform(data)


freqs = [ float(i) for i in xrange(len(transform))]
#plt.subplot(2, 1, 1)
plt.plot( dates, data,label='Data' )

fit=cpt.least_squares_fit(dates, data)
print fit
print
ecks= numpy.linspace(1960,2020,1000)
why= ecks*fit[1]+fit[0]
plt.plot(ecks,why,label='Linear')

fit= cpt.least_squares_fit(dates,logdata)
print fit
print 

why= [math.pow(math.e, elem*fit[1]+fit[0]) for elem in ecks] 
plt.plot(ecks,why,label='Exponential')


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
ax = plt.subplot(2, 1, 2)
plt.plot( freqs, transform )
ax.set_yscale('log')
'''
plt.show()
