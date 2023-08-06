#/usr/bin/env python
"""
Calibration helpers.  This contains some old legacy routines used by the
_initial and _refined scripts but also contains objects and methods for
the simiplified all-in-one calibration routine. 
"""

import logging
import pickle
import numpy as np
import cv2
from argus import Camera
import random




class Calibrator(object):
    """
    An object that performs calibrations
    """
    def __init__(self,point_inputs,patterns=20,inverted=False,shuffle=False):
        logging.debug("Creating Calibrator object")
        self.camera = Camera()
        self.point_inputs = point_inputs
        self.patterns = patterns
        self.inverted = inverted
        
        self.shuffle = shuffle
        self.ooP = None
        self.iiP = None



    def get_initial(self):
        """
        Obtains an initial calibration by varying only focal distance.
        This can be changed by changing the argus.INITIAL flag settings. 
        """
        self.ooP,self.iiP = self.point_inputs.get_subset(patterns=self.patterns,
                                                         inverted=self.inverted)

        #print self.ooP
        #print self.iiP

        # initialize outputs
        cM = np.array([[600.,0.,self.point_inputs.imageSize[0]/2.-0.5],
                       [0.,600.,self.point_inputs.imageSize[1]/2.-0.5],
                       [0.,0.,1.]],dtype=np.float32)
        dC = np.zeros((1,5),dtype=np.float32)
        rv = np.zeros((self.patterns,3),dtype=np.float32)
        tv = np.zeros((self.patterns,3),dtype=np.float32)

        retval,cM,dC,rv,tv = cv2.calibrateCamera(self.ooP,self.iiP,
                                                 self.point_inputs.imageSize,
                                                 cM,dC,
                                                 rv,tv,
                                                 flags=INITIAL)
        if retval:
            rmse = compute_rmse(self.ooP,self.iiP,cM,dC,rv,tv)
            if rmse < 10.:
                logging.warning("Abnormally low rmse - check it!")
            elif rmse > 10000.:
                logging.warning("Very large rmse detected, consider --inverted?")
            logging.debug("got initial calibration with rmse {0}".format(rmse))
            result = Camera(cM,dC,rmse)
            self.camera = result
            return True
        else:
            logging.warning("failed to find initial calibration")
            self.camera = Camera()
            return False




    def refine(self,flags):
        """
        Obtains a refined calibration, as specified by flags.
        argus.FIRSTPASS allows k1 and k2 to vary only
        argus.SECONDPASS allows k1-k3 to vary.
        These can be altered by passing in different flags. 
        """
        if self.shuffle:
            self.ooP,self.iiP = self.point_inputs.get_subset(patterns=self.patterns, inverted=self.inverted)

        # initialize outputs
        cM = self.camera.cM
        dC = self.camera.dC
        rv = np.zeros((self.patterns,3),dtype=np.float32)
        tv = np.zeros((self.patterns,3),dtype=np.float32)

        retval,cM,dC,rv,tv = cv2.calibrateCamera(self.ooP,self.iiP,
                                                 self.point_inputs.imageSize,
                                                 cM,dC,
                                                 rv,tv,
                                                 flags=flags)
        if retval:
            rmse = compute_rmse(self.ooP,self.iiP,cM,dC,rv,tv)
            if rmse < 10.:
                logging.warning("Abnormally low rmse - check it!")
            elif rmse > 10000.:
                logging.warning("Very large rmse detected, consider --inverted?")
            logging.debug("got refined calibration with rmse {0}, flags {1}".format(rmse,flags))
            result = Camera(cM,dC,rmse)
            self.camera = result
            return True
        else:
            logging.warning("failed to find refined calibration with flags {0}".format(flags))
            return False













class CalibrationInputs(object):
    """
    Object for handling calibration inputs obtained from pattern detection
    """
    def __init__(self):
        self.objectPoints = None
        self.imagePoints = None
        self.frames = None
        self.imageSize = None


    def improved_sample(self, frames, size):
        """
        Improved sample drawing that tries to make sure the sample
        of size size is spread out over the whole range of frames.
        Calling signature is meant to be drop in replacement for
        numpy.random.sample(). 

        Originally written by Dylan Ray
        """
        
        # compute some contorted stuff from Dylan Ray
        # i dunno wtf this is but i won't mess with it
        length = len(frames)-1
        S = float(size)
        L = float(length)
        second_cm = -(1./4.)*L**2. + (1./6.)*L*(2*L+1)
        fourth_cm = (-3.*(L/2.)**2. + \
                     6.*(L/2.)**2.*((1./6.)*L*(2.*L + 1.)) -  
                     4.*(L/2.)*((1./4.)*L**2.*(L + 1.)) + 
                     (1./30.)*L*(6.*L**3. + 9.*L**2. + L - 1.))
        sample_variance_var = ((S - 1.)**2./(S)**3.*fourth_cm - 
                               ((S - 1.)*(S - 3.))*second_cm**2./(S)**3.)
        sample_variance_mean = (S-1.)/S*second_cm
        LB = sample_variance_mean+0.1*sample_variance_var**0.5
        LB = min(LB, ((L+1.)**2.-1.)/12.)

        # now actually draw the sample
        found = False
        count = 0
        MAX_TRIES = 50 # old one didn't actually check this
        
        while (not found) and (count < MAX_TRIES):
            sample = list() # initialize the sample to empty list

            for k in xrange(size):
                a = np.random.randint(0, length)
                while a in sample:
                    a = np.random.randint(0, length)
                    # NB this will cause an infinite loop 
                    # if sample has everything
                sample.append(a)
            # at end of this, sample is list of integers each one
            # only appearing once
                
            found = (np.var(sample) >= LB)
            # check if good sample actually found
            
        if not found:
            raise RuntimeError("argus.ImprovedSampler MAX_TRIES exceeded")
            return None
        else:
            ret = [frames[X] for X in sample]
            # list comprehension 
            # pythonic way to make the return list of frames
            return ret

    def get_subset(self,patterns=20,inverted=False):
        #subset = random.sample(self.frames,patterns)
        subset = self.improved_sample(self.frames,patterns)
        if inverted:
            ooP = [-self.objectPoints[X] for X in subset]
        else:
            ooP = [self.objectPoints[X] for X in subset]
        iiP = [self.imagePoints[X] for X in subset]
        return ooP,iiP

    def _from_pkl(cls,ifilename):    
        result = cls()
        logging.debug("Reading corners from {0}".format(ifilename))
        ifile = file(ifilename,"rb")
        result.objectPoints = pickle.load(ifile) # load object points
        result.imagePoints = pickle.load(ifile) # load image points
        result.frames = result.objectPoints.keys() 
        result.imageSize = pickle.load(ifile) # load image size
        ifile.close()
        return result
    from_pkl = classmethod(_from_pkl)





# calibration flags defined here
# Others can be defined. 

# for initial - everything is fixed except focal length!
INITIAL = int(0) | cv2.CALIB_FIX_PRINCIPAL_POINT | \
          cv2.CALIB_FIX_ASPECT_RATIO | \
          cv2.CALIB_FIX_K1 | \
          cv2.CALIB_FIX_K2 | \
          cv2.CALIB_ZERO_TANGENT_DIST | \
          cv2.CALIB_FIX_K3

# first pass is now first order stuff: f, k1
FIRSTPASS = int(0) | cv2.CALIB_USE_INTRINSIC_GUESS | \
            cv2.CALIB_FIX_PRINCIPAL_POINT | \
            cv2.CALIB_FIX_ASPECT_RATIO | \
            cv2.CALIB_ZERO_TANGENT_DIST | \
            cv2.CALIB_FIX_K2 | \
            cv2.CALIB_FIX_K3

# in second pass allow second order k2; we think t1 t2 are 0ish 
# due to good manufacturing; same with cx and cy
SECONDPASS = int(0) | cv2.CALIB_USE_INTRINSIC_GUESS | \
             cv2.CALIB_FIX_PRINCIPAL_POINT | \
             cv2.CALIB_FIX_ASPECT_RATIO | \
             cv2.CALIB_ZERO_TANGENT_DIST | \
             cv2.CALIB_FIX_K3

# two more passes for k3 and tangential distortion
THIRDPASS = int(0) | cv2.CALIB_USE_INTRINSIC_GUESS | \
             cv2.CALIB_FIX_PRINCIPAL_POINT | \
             cv2.CALIB_FIX_ASPECT_RATIO | \
             cv2.CALIB_ZERO_TANGENT_DIST

FOURTHPASS = int(0) | cv2.CALIB_USE_INTRINSIC_GUESS | \
             cv2.CALIB_FIX_PRINCIPAL_POINT | \
             cv2.CALIB_FIX_ASPECT_RATIO

# OPTIONAL
# at very end, fix everything else and allow it to change
# principal point hopefully only a little
LASTPASS = int(0) | cv2.CALIB_USE_INTRINSIC_GUESS | \
           cv2.CALIB_FIX_FOCAL_LENGTH | \
           cv2.CALIB_FIX_ASPECT_RATIO | \
           cv2.CALIB_FIX_K1 | \
           cv2.CALIB_FIX_K2 | \
           cv2.CALIB_ZERO_TANGENT_DIST | \
           cv2.CALIB_FIX_K3










def compute_rmse(oP,iP,cM,dC,tv,rv):
    """
    reprojection error for a calibration.  cv2.calibrateCamera
    unfortunately doesn't return this!
    """
    result = 0.
    point_count = 0
    for index in xrange(len(oP)):
        projection,_ = cv2.projectPoints(oP[index],
                                         rv[index],
                                         tv[index],
                                         cM,
                                         dC)
        result += np.sum((projection-iP[index])**2.)
        point_count += oP[index].shape[0]
    return (result/float(point_count))**0.5

















# These are only included for backwards compatibility

def load_points(filename):
    """
    Loads objectPoints, imagePoints, and imageSize from .pkl

    Returns dicts of objectPoints and imagePoints, where each
    element is as expected for OpenCV cv2.calibrateCamera and 
    related functions. 

    imageSize is a tuple of (width,height) in pixels, also as 
    expected for OpenCV.
    """
    logging.debug("Reading corners from {0}".format(filename))
    ifile = file(filename,"rb")
    oP = pickle.load(ifile) # load object points
    iP = pickle.load(ifile) # load image points
    frames = oP.keys() 
    iS = pickle.load(ifile) # load image size
    ifile.close()
    return oP,iP,frames,iS

def initialize_outputs(iS,n):
    # Evan got this as initial guess
    cM = np.array([[600.,0.,iS[0]/2.-0.5],[0.,600.,iS[1]/2.-0.5],[0.,0.,1.]],dtype=np.float32)
    dC = np.array([[-0.35,0.25,-0.001,0.001,-0.11]],dtype=np.float32)
    rv = np.zeros((n,3),dtype=np.float32)
    tv = np.zeros((n,3),dtype=np.float32)
    return cM,dC,rv,tv









                
                    
                    
