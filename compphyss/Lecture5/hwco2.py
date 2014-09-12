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
plt.subplot(2, 1, 1)
plt.plot( dates, data )

fit=cpt.least_squares_fit(dates, data)
print fit
ecks= numpy.linspace(1960,2020,1000)
why= ecks*fit[1]+fit[0]
plt.plot(ecks,why)

fit= cpt.least_squares_fit(dates,logdata)
print fit


why= [math.pow(math.e, elem*fit[1]+fit[0]) for elem in ecks] 
plt.plot(ecks,why)


fit=numpy.polyfit(dates,data,2)
why= fit[0]*ecks**2+fit[1]*ecks+fit[2]
plt.plot(ecks,why)
print fit



ax = plt.subplot(2, 1, 2)
plt.plot( freqs, transform )
ax.set_yscale('log')

plt.show()
