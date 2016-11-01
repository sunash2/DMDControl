import math
import numpy as np
import scipy.ndimage as nd
import sys
sys.path.append('../Library/')
from HologramGeneration import ImageProcessing as IP
from UsbControl import LightCrafter6500Device as lc
import UsbControl.PatternCreation as pc
import PotetialGeneration.ImagePlanePotentialGenerator as ippg
from PIL import Image as pil
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

'''
hologramtest_gaussiann

take measured phase and amplitude data and generate DMDimage (hologram)
that compensate abberation and create gaussian at the focal point.
using Modules/HologramGeneration/ImageProcessing.py
'''

##########################
#fetch data
##########################
path = "../Data/PhaseMeasurement/"
Amp = np.genfromtxt(path + 'Ampl.csv', delimiter=',').T
Phase = np.genfromtxt(path +'Phasec1.csv', delimiter=',').T
Phaseresidual = np.genfromtxt(path +'Phase_residual.csv', delimiter=',').T
xsize,ysize = np.shape(Amp)
factor = 60 ##patch size of phase measurement

###########################
#interpolation
###########################
print "start interpolation"
interpol_setting = {'method':IP.linear_i,
                'factor':factor,
                'Amp':Amp,'Phase':Phase,'Phase residual':Phaseresidual}
interpolated = IP.Phasemap(**interpol_setting)
interpolated.interpolate()
phasemap = interpolated.phasemap_large


###########################
#create gaussian or fourier plane
###########################
gaus_setting =  {'image':"gaus",
                    'shape':np.shape(phasemap[0]),
                    'width':0.2}#0~1, zero to image size*2#
Gaussian = IP.TargetImage(**gaus_setting)
Gaussian.imagefft()
gaus = Gaussian.fimage

###########################
#generate hologram
###########################
print "start hologram generation"
hologram_setting = {'factor':factor,
                    'phasemap':phasemap,
                    'fimage':gaus,
                    'alpha':19,
                    'method':IP.hologramize}
pattern = IP.Hologram(**hologram_setting)
pattern.compute_hologram()


###########################
#upload to DMD
###########################
#print "start upload"
#lc_dmd = lc.LC6500Device()
settings = {'compression':'rle','exposure_time':500000}
dmd_pattern = pc.DMDPattern(**settings)
dmd_pattern.pattern = pattern.hologram
#lc_dmd.upload_image(dmd_pattern)


###########################
#show images
###########################
fig1=plt.figure(1,(25,10))

plt.subplot(2,5,1)
plt.gray()
plt.imshow(gaus,interpolation="none")
plt.title('gaussian')

plt.subplot(2,5,2)
plt.gray()
plt.imshow(phasemap[0],interpolation="none")
plt.colorbar()
plt.title('amplitude interpolated')

plt.subplot(2,5,3)
plt.gray()
plt.imshow(phasemap[1],interpolation="none")
plt.colorbar()
plt.title('phase interpolated')

plt.subplot(2,5,4)
plt.gray()
plt.imshow(pattern.hologram)
plt.title('dmdimage')


plt.subplot(2,5,7)
plt.gray()
plt.imshow(Amp,interpolation="none")
plt.title('amp original')


plt.subplot(2,5,8)
plt.gray()
plt.imshow(Phase,interpolation="none")
plt.title('phase original')

plt.subplot(2,5,9)
plt.gray()
plt.imshow(pattern.hologram[540-xsize*factor/2:540+xsize*factor/2,960-ysize*factor/2:960+ysize*factor/2])
plt.title('dmdimage')

#plt.subplot(2,5,5)
#plt.gray()
#plt.imshow(Amp_l2)
#plt.title('interpolated large amp')

#plt.subplot(2,5,10)
#plt.gray()
#plt.imshow(Phase_l2)
#plt.title('interpolated large')

plt.show()




