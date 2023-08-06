from __future__ import print_function
import astropy as ap
from astropy.io import fits
import os
import matplotlib.pyplot as plt
import numpy as np
from photutils import CircularAperture
from photutils import aperture_photometry, CircularAnnulus
from astropy.table import hstack


__version__ = '1.0.1'

'''
    
    If the object oriented approach doesn't simplify this enough, I suppose you could rip the code apart
    by deleting the 'class _____' crap, and remove 'self' or '@classmethod' from every function, then it 
    will work just like normal procedural code.



'''

def timethis(input_function):
    '''
        Timing decorator used to report the time it took to use these functions.
    '''
    import time
    def Timer(*args, **kwargs):
        start = time.time()
        results = input_function(*args, **kwargs)
        end = time.time()
        print ('{}: {} took'.format(input_function.__class__.__name__,input_function.__name__),\
                        '%.3f seconds to run.'%(end-start))
        return results
    return Timer

    



class cepheus(object):
    
    def __init__(self, directory,sourceRA,sourceDEC):
        self.directory = directory
        self.files = self.files()
        self.Star = fits.open('{}/{}'.format(self.directory,self.files[51]))
        self.stardata = self.Star[0].data
        self.IMGheader = self.Star[0].header
        self.worldcoord = ap.wcs.WCS(header=self.IMGheader)
        self.sourceRA = sourceRA
        self.sourceDEC = sourceDEC


    def cut_vals(self,tbl):
        '''
            I don't bother using annoying astropy table objects, they are ridiculous and
            don't behave with python nicely. So this function cuts everything out that isnt 
            a string of digits in the table, to extract the background subtracted photon counts.
        '''
        nums = []
        for t in repr(tbl).split():
            try:
                nums.append(float(t))
            except:
                pass
        return nums


    def files(self):
        '''Load the files in your directory into an array... '''
        files = []
        for file in os.listdir(self.directory):
            if file.endswith('.fit'):
                files.append(file)
        files.sort()
        return files

    def calculate_fluxes(self,stardata,apertures,aper_annulus):
        '''
            Calculates the photon flux in an aperture, and an annulus
            around the aperture to subtract the background.
            
            As far as I can tell, the output value is still just a 'photon count', not technically a 
            photon flux. Possible modifications will start here, maybe uncommenting the apertures.area()
            which calculates the aperture phot_count divided by area of aperture.
            giving photons per area.
            
            I think we would further have to supplement that by dividing by the exposure time, and some 
            other wavelength value I cant think of, to get PHOTON FLUX ( photons per sec per cm^2 per wavelength)
        '''
        flux_table = aperture_photometry(stardata, apertures)
        bkg_table  = aperture_photometry(stardata, aper_annulus)
        
        phot_table = hstack([flux_table, bkg_table], table_names=['raw','bkg'])
        bkg_mean = phot_table['aperture_sum_bkg'] / aper_annulus.area()
        
        bkg_sum = bkg_mean * apertures.area()
        final_sum = phot_table['aperture_sum_raw'] - bkg_sum
        phot_table['residual_aperture_sum'] = final_sum
        #phot_table['res_aper_div_area'] = final_sum/apertures.area()
        #print(phot_table)
        return self.cut_vals(phot_table)
        
    def fluxcurve(self,sourceRA,sourceDEC, check=None):
        '''
            Stores the background subtracted photon fluxes in an aperture around the sourceRA and sourceDEC.
            
            r_in :  inner radius of the annulus, in pixels
            r_out:  outer radius of the annulus, in pixels.
                        The r_in value should be strictly greater than the radius of the aperture.
                        I used an aperture radius of r=6 ( see below), this should be fine for all
                        of everyones stars, references or not.
           
            worldcoord : a world-coordinate-system object that uses the fits header stuff to transform
                         a location on the image in pixels into RA and DEC values in degrees, and vice versa.
                         This is how the sourceRA and sourceDEC 'know' exactly where there cepheids and references
                         are.
           
           
        '''
        if check == None:
            check = False

            
        starlist = []
        #testtable = np.empty(shape=(len(files),5))
        testrun = []
        for i in range(len(self.files)):
            Star = fits.open('{}/{}'.format(self.directory,self.files[i]))
            stardata = Star[0].data
            IMGheader = Star[0].header
            worldcoord = ap.wcs.WCS(IMGheader)
            exposure = Star[0].header['EXPTIME']
            starlist.append((self.files[i],Star[0].header['OBJECT']))
            zeromag = Star[0].header['ZMAG']
            juliandate = Star[0].header['JD-MID']
            aper_annulus = CircularAnnulus((sourceRA, sourceDEC), r_in=7., r_out = 10.)
            apertures = CircularAperture((worldcoord.wcs_world2pix(sourceRA,sourceDEC,0)), r=6)
            
            testrun.append((self.calculate_fluxes(stardata,apertures, aper_annulus)[3], exposure,juliandate , zeromag))
        
        if check == True:
            return starlist
        
        
        
        return testrun


    def mag_calc_noref(self,sourceRA,sourceDEC):
        '''
            DEFUNCT -- PRODUCES LIKELY UNCALIBRATED DATA!!! DO NOT USE THIS
            Calculating the magnitude of the source star with NO reference star, using photon counts,
            exposure time, and zero point magnitude calibration: ALL header items.
            
            Output: 2 column array: 1st column is magnitudes, 2nd column is julian dates from fits files.
        '''
        testrun = self.fluxcurve(sourceRA,sourceDEC)
        maglist = []
        for i in range(len(testrun)):
            magnitude = -2.5*np.log10((testrun[i][0]/testrun[i][1])) + testrun[i][3]
            maglist.append((magnitude, testrun[i][2]))
        
        maglist = np.array(maglist, dtype=float)
        return maglist

    def calibrate_mag(self,sourceRA,sourceDEC,refRA,refDEC,refmag):
        '''
            Calculating the magnitude of the source star including a reference star.
        '''
        sourcestar = self.fluxcurve(sourceRA,sourceDEC)
        reference  = self.fluxcurve(refRA, refDEC)
        maglist = []    
        for i in range(len(sourcestar)):
            magnitude = -2.5*np.log10(sourcestar[i][0]/reference[i][0]) + refmag
            maglist.append((sourcestar[i][2], magnitude))
        return np.array(maglist,dtype=float)
    
    @classmethod
    def PL_VI_distance(self,period,Vmag,Imag):
        '''
            TYPE 2 CEPHEID LUMINOSITY DISTANCE 
            given by Majaess,Turner,Lane  2009
            arxiv: 0903.4206v2
        '''
        a = Vmag + 2.34*np.log10(period) - 2.25*(Vmag-Imag) + 6.03      
        return 10.**(a/5.)
    
    @classmethod
    def PL_BV_distance(self,period,meanB,meanV):
        a = meanV + 4.42*np.log10(period) - 3.43*(meanB-meanV) + 7.15        
        return 10.**(a/5.)
    
    @classmethod
    def dms_to_deg(self,dmsval):
        ''' ENTER THE DEG/MIN/SEC value as a STRING.'''
        deg,mins,secs = dmsval.split(' ')    
        deg = float(deg)
        mins = float(mins)
        secs = float(secs)
        total = deg + (mins/60.) + (secs/3600.)
        return total

    @classmethod
    def hms_to_deg(self,hmsval):
        ''' ENTER THE DEG/MIN/SEC value as a STRING.'''
        hour,mins,secs = hmsval.split(' ')    
        hour = float(hour)
        mins = float(mins)
        secs = float(secs)
        total = 15.*(hour + (mins/60.) + (secs/3600.))
        return total


    def show_image(self,sourceRA,sourceDEC,refRA=None,refDEC=None, ref2RA=None, ref2DEC=None):
        print('RED circle is the cepheid. WHITE circle is the reference object(s).')
        print('Add more reference stars by defining ref1aper = blahblahbelow, and ref1aper.plot(etc...)')
        #aper_annulus = CircularAnnulus((sourceRA, sourceDEC), r_in=6., r_out = 8.)

        apertures = CircularAperture((self.worldcoord.wcs_world2pix(sourceRA,sourceDEC,0)), r=10)
       
        #ref2aper  = CircularAperture((worldcoord.wcs_world2pix(ref2RA,ref2DEC,0)),     r=7)
        #ref3aper  = CircularAperture((worldcoord.wcs_world2pix(ref3RA,ref3DEC,0)),     r=3.5)
        #darkaper  = CircularAperture((worldcoord.wcs_world2pix(darkRA,darkDEC,0)),     r=3.5)
        
        
        fig = plt.figure()
        fig.add_subplot(111, projection = self.worldcoord)
        plt.imshow(self.stardata,origin='lower', cmap='jet')
        apertures.plot(color='red',lw=5, alpha=1)
        
        if refRA != None:
           ref1aper  = CircularAperture((self.worldcoord.wcs_world2pix(refRA,refDEC,0)),     r=10)
           ref1aper.plot(color='red', lw=5, alpha=1)
        #apertures2.plot(color='white',lw=2.0,alpha=0.5)
        #largeaperture.plot(color='red',  lw=1.5, alpha=0.5)
        if ref2RA != None:
           ref2aper  = CircularAperture((self.worldcoord.wcs_world2pix(ref2RA,ref2DEC,0)),     r=10)
           ref2aper.plot(color='red', lw=5, alpha=1)


    def plot_lightcurve(self, maglist, label=None):
        if label == None:
            label = 'BGO, V filter'
        plt.xlabel('Julian Date - 2457290')
        plt.ylim(10,14.2)
        plt.ylabel('Magnitude')
        plt.grid(True)
        plt.plot(maglist[:,0]- 2.45729e6,maglist[:,1], label=label,lw=3)        
        plt.legend()



class magtools(object):
    '''
        TYPE 2 CEPHEID PLRs:
        equations from Pritzl et al. (2003)
        ABSOLUTE MAGNITUDE CALCULATIONS
    '''
    def __init__(self, period):
        self.period = period

    def type2_mean_V(self):
        #UNCERTAINTIES
        #slope: 0.05
        #intercept: 0.05
        return (-1.64)*(np.log10(self.period)) + 0.05

    def type2_mean_B(self):
        #UNCERTAINTIES
        #slope: 0.09
        #intercept: 0.09
        return (-1.23)*(np.log10(self.period)) + 0.31

    def type2_mean_I(self):
        #UNCERTAINTIES
        #slope: 0.03
        #intercept: 0.01
        return (-2.03)*(np.log10(self.period)) - 0.36

    
    @classmethod
    def Bin_up(self,maglist):
        '''
            Averages out the data taken in the same day.
            Essentially taking integer values of the mid-JD and averaging those out. -- No 
            statistical weighting.
        '''
        Timebin = []
        for i in range(len(maglist)):
            if np.floor(maglist[i,0]) not in Timebin:
                Timebin.append(np.floor(maglist[i,0]))
        
        def sumbin(maglist, time):
            Vbin = []
            for i in range(len(maglist)):
                if np.floor(maglist[i,0]) == time:
                    Vbin.append(( maglist[i,1]))
            return np.average(Vbin)
            
        avg = []
        for i in range(len(Timebin)):
            avg.append(sumbin(maglist,Timebin[i])) 
        return np.array((Timebin,avg), dtype=float).T
    
    @classmethod
    def plot(self,maglist):
        '''
            plots the lightcurve of maglist data, subtracting off 2.45729e6 days,
            so the x axis looks nicer.
        '''
        plt.plot(maglist[:,0] - 2.45729e6, maglist[:,1], label='test bin', lw=2.0)
