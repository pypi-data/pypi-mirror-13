#!/usr/bin/env python
"""
"""

"""
# old code from Dylan

import numpy as np
import cv2
import sba.quaternions as quaternions
import sys
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import sba






# solves an overdetermined linear system for DLT coefficients constructed via
# these instructions: http://kwon3d.com/theory/dlt/dlt.html
def getCoefficients(xyz, uv):
    # delete rows which have nans
    toDel = list()
    for k in range(uv.shape[0]):
        if True in np.isnan(uv[k]):
            toDel.append(k)

    xyz = np.delete(xyz, toDel, axis = 0)
    uv = np.delete(uv, toDel, axis = 0)

    A = np.zeros((xyz.shape[0]*2, 11))

    # construct matrix based on uv pairs and xyz coordinates
    for k in range(xyz.shape[0]):
        A[2*k,:3] = xyz[k]
        A[2*k,3] = 1
        A[2*k,8:] = xyz[k]*-uv[k,0]
        A[2*k+1,4:7] = xyz[k]
        A[2*k+1,7] = 1
        A[2*k+1,8:] = xyz[k]*-uv[k,1]

    B = np.zeros((uv.shape[0]*2, 1))

    for k in range(uv.shape[0]):
        B[2*k] = uv[k,0]
        B[2*k + 1] = uv[k,1]

    # solve using numpy's least squared algorithm
    L = np.linalg.lstsq(A,B)[0]

    # reproject to calculate rmse
    reconsted = np.zeros((uv.shape[0],2))
    for k in range(uv.shape[0]):
        u = (np.dot(L[:3].T,xyz[k]) + L[3])/(np.dot(L[-3:].T,xyz[k]) + 1.)
        v = (np.dot(L[4:7].T,xyz[k]) + L[7])/(np.dot(L[-3:].T,xyz[k]) + 1.)
        reconsted[k] = [u, v]

    error = 0
    for k in range(uv.shape[0]):
        s = np.sqrt((reconsted[k,0] - uv[k,0])**2 + (reconsted[k,1] - uv[k,1])**2)
        error += s

    rmse = error/float(uv.shape[0])

    return L, rmse







# driver for SBA operations, graphing, and writing output
class sbaArgusDriver():
    def __init__(self, ppts, uppts, cams, display = True, scale = None, modeString = None, ref = None, name = None, temp = None):
        self.ppts = ppts
        self.uppts = uppts
        self.cams = cams
        self.ncams = cams.shape[0]
        self.display = True # deprecated option, always display graph
        self.scale = scale
        self.modeString = modeString
        self.nppts = 0
        self.nuppts = 0
        self.ref = ref
        self.name = name
        self.temp = temp

    # parses through the csvs given and finds those rows which have uv coordinates that can be triangulated
    # with respect to the last camera's reference frame. puts good indices in a list to reconstruct later and
    # preserve frame count
    def parse(self, pts):
        ret = list()
        # how many points are present?
        npts = pts.shape[1]/(2*self.ncams)
        # for each point column
        for k in range(npts):
            # get bad indices and remove them from a list of all indices to get good indices
            badindices = list()
            p = pts[:,k*2*self.ncams:(k+1)*2*self.ncams]
            for k in range(p.shape[0]):
                if True in np.isnan(p[k][2*(self.ncams - 1):]):
                    badindices.append(k)
                elif not False in np.isnan(p[k][:2*(self.ncams - 1)]):
                    badindices.append(k)
            goodindices = np.arange(pts.shape[0])
            toDel = list()
            for k in range(len(goodindices)):
                if k in badindices:
                    toDel.append(k)
            goodindices = np.delete(goodindices, toDel, axis = 0)
            ret.append([np.delete(p, badindices, axis = 0), goodindices])
        return ret

    # stacks everything together to pass into SBA
    def getPointsAndExtArray(self):
        indices = dict()
        # we've got both paired and unpaired points
        if self.ppts is not None and self.uppts is not None:
            parsed = self.parse(self.uppts)
            _ = parsed[0][0]
            for k in range(1, len(parsed)):
                _ = np.vstack((_, parsed[k][0]))
            unpaired = _
            _ = None

            ind = list()
            for k in range(len(parsed)):
                ind.append(list(parsed[k][1]))
            indices['unpaired'] = ind

            self.nuppts = unpaired.shape[0]

            pairedParsed = self.parse(self.ppts)
            _ = pairedParsed[0][0]
            for k in range(1, len(pairedParsed)):
                _ = np.vstack((_, pairedParsed[k][0]))
            paired = _
            _ = None

            self.nppts = paired.shape[0]

            ind = list()
            for k in range(len(pairedParsed)):
                ind.append(list(pairedParsed[k][1]))
            indices['paired'] = ind

            pts = np.vstack((paired, unpaired))
        # we've got only paired points
        elif self.ppts is not None and self.uppts is None:
            pairedParsed = self.parse(self.ppts)
            _ = pairedParsed[0][0]
            for k in range(1, len(pairedParsed)):
                _ = np.vstack((_, pairedParsed[k][0]))
            pts = _
            _ = None

            ind = list()
            for k in range(len(pairedParsed)):
                ind.append(list(pairedParsed[k][1]))
            indices['paired'] = ind

            self.nppts = pts.shape[0]
        # should never get here, as we now require that the user always have paired points
        # else you're just looking at pretty pictures
        elif self.uppts is not None and self.ppts is None:
            parsed = self.parse(self.uppts)
            _ = parsed[0][0]
            for k in range(1, len(parsed)):
                _ = np.vstack((_, parsed[k][0]))
            pts = _
            _ = None

            self.nuppts = pts.shape[0]

            ind = list()
            for k in range(len(parsed)):
                ind.append(list(parsed[k][1]))
            indices['unpaired'] = ind

        # if we've got reference points, stack them on top
        if self.ref is not None:
            pts = np.vstack((ref, pts))

        print 'Triangulating...'
        sys.stdout.flush()
	
	# pass the big stack of UV coordingates to be triagulated
        tring = multiTriangulator.multiTriangulator(pts, self.cams)
        xyz = tring.triangulate()

	# put them together for SBA
        pts = np.hstack((xyz, pts))

        return pts, tring.ext, indices

    def outputDLT(self, cos, error):
        fo = open(self.name + '-dlt-coefficients.csv', 'wb')
        fo.write('L_1,L_2,L_3,L_4,L_5,L_6,L_7,L_8,L_9,L_10,L_11,rmse\n')
        for k in range(cos.shape[0]):
            l = str(cos[k][0])
            fo.write(l + ',')
        fo.write(str(error))
        fo.close()

    def fix(self):
        pts, ext, indices = self.getPointsAndExtArray()

        print 'Passing points to SBA...'
        sys.stdout.flush()

        points = sba.Points.fromDylan(pts)
        cameras = sba.Cameras.fromDylan(np.hstack((self.cams, ext)))
        options = sba.Options.fromInput(cameras,points)
        options.camera = sba.OPTS_CAMS
        if self.modeString[0] == '0':
            options.nccalib = sba.OPTS_FIX5_INTR # fix all intrinsics
        elif self.modeString[0] == '1':
            options.nccalib = sba.OPTS_FIX4_INTR # optimize focal length
        elif self.modeString[0] == '2':
            options.nccalib = sba.OPTS_FIX2_INTR # optimize focal length and principal point

        if self.modeString[1] == '0':
            # If you wish to fix the intrinsics do so here by setting options
            options.ncdist = sba.OPTS_FIX5_DIST # fix all distortion coeffs
        elif self.modeString[1] == '1':
            options.ncdist = sba.OPTS_FIX4_DIST # optimize k2
        elif self.modeString[1] == '2':
            options.ncdist = sba.OPTS_FIX3_DIST # optimize k2, k4
        elif self.modeString[1] == '3':
            options.ncdist = sba.OPTS_FIX0_DIST # optimize all distortion coefficients

        newcameras,newpoints,info = sba.SparseBundleAdjust(cameras,points,options)
        info.printResults()
        sys.stdout.flush()

        newcameras.toTxt(self.temp + '/cn.txt')
        newpoints.toTxt(self.temp + '/np.txt')

        npframes = self.ppts.shape[0]
        if uppts is not None:
            nupframes = self.uppts.shape[0]
        else:
            nupframes = None

        if self.ref is not None:
            refBool = True
        else:
            refBool = False

        uvs = list()
        for k in range(self.ncams):
            uvs.append(pts[:,3+2*k:3+2*(k+1)])
        xyz = pts[:,:3]

        errs = list()
        dlts = list()
        for uv in uvs:
            cos, error = getCoefficients(xyz, uv)
            dlts.append(cos)
            errs.append(error)

        dlts = np.asarray(dlts)
        errs = np.asarray(errs)

        self.outputDLT(np.nanmean(dlts, axis = 0), np.nanmean(errs))

        if self.display:
            grapher = wandGrapher.wandGrapher(self.nppts, self.nuppts, self.scale, refBool, indices, self.ncams, npframes, nupframes, self.name, self.temp)
            print 'Graphing and writing output files...'
            sys.stdout.flush()

            grapher.graph()

def parseCSVs(csv):
    fo = open(csv)
    line = fo.readline()
    header = False
    try:
        float(line.split(',')[0])
    except:
        header = True
        pass
    if not header:
        ret = map(float, line.split(','))
    else:
        line = fo.readline()
        ret = map(float, line.split(','))
    line = fo.readline()
    while line != '':
        ret = np.vstack((ret, map(float, line.split(','))))
        line = fo.readline()
    return ret


if __name__ == '__main__':
    if sys.argv[1] != '':
        ppts = parseCSVs(sys.argv[1])
    else:
        ppts = None
    if sys.argv[2] != '':
        uppts = parseCSVs(sys.argv[2])
    else:
        uppts = None
    cams = np.loadtxt(sys.argv[3])
    scale = float(sys.argv[4])
    display = bool(sys.argv[5])
    mode = sys.argv[6]
    if sys.argv[7] != '':
        ref = np.loadtxt(sys.argv[7])
    else:
        ref = None
    name = sys.argv[8]
    tmp = sys.argv[9]

    driver = sbaArgusDriver(ppts, uppts, cams, display, scale, mode, ref, name, tmp)
    driver.fix()


# class for calling sbaTriangulate with multiple pixel coordinate pairs. Always passes the last camera
# as the reference frame camera. Afterwards, normalizes the other xyz coordinates based on the average distance for the
# origin camera xyzs and averages everything together for the final estimate of 3D coordinates. 
class multiTriangulator():
    def __init__(self, pts, intrins):
        self.pts = pts
        self.ncams = pts.shape[1]/2
        self.intrins = intrins
        self.ext = None

    def triangulate(self):
        # Last camera points
        origincam = self.pts[:,-2:]

        othercams = list()
        xyzs = list()
        # Other camera points
        for k in range(self.ncams - 1):
            othercams.append(self.pts[:, 2*k : 2*(k+1)])

        transrots = list()
        for k in range(len(othercams)):
            # List for the triangulatable point set indices
            goodindices = list()
            cam = othercams[k]

            # Populate goodindices
            for j in range(len(cam[:,0])):
                if not True in np.isnan(cam[j]) and not True in np.isnan(origincam[j]):
                    goodindices.append(j)

            dest = list()
            source = list()
            for j in range(len(cam[:,0])):
                if j in goodindices:
                    dest.append(np.asarray(cam[j]))
                    source.append(np.asarray(origincam[j]))

            dest = np.asarray(dest)
            source = np.asarray(source)

            tring = sbaTriangulate.Triangulator(dest, source,
                                                self.intrins[k,0], self.intrins[-1,0],
                                                self.intrins[k,1:3], self.intrins[-1,1:3],
                                                    self.intrins[k,-5:],
                                                    self.intrins[-1,-5:])
            tri = tring.triangulate()

            transrots.append(np.hstack((tring.getQuaternion(), tring.t)))

            xyz = np.zeros((len(self.pts[:,0]),3))

            for j in range(len(goodindices)):
                xyz[goodindices[j]] = tri[j]

            xyz[xyz == 0] = np.nan
            xyzs.append(xyz)
        # Cleanup
        othercams, origincam = None, None

        _ = transrots[0]
        for k in range(1, len(transrots)):
            _ = np.vstack((_, transrots[k]))
        _ = np.vstack((_, [1, 0, 0, 0, 0, 0, 0]))

        self.ext = _

        return self.normalizeAndAverage(xyzs)

    def normalizeAndAverage(self, xyzs):
        averdists = list()

        for xyz in xyzs:
            dists = list()
            for j in range(len(xyz[:,])):
                if not True in np.isnan(xyz[j]):
                    dists.append(np.linalg.norm(xyz[j]))
            #print dists
            averdists.append(np.nanmean(dists))
        ret = list()
        ret.append(xyzs[0])

        for k in range(1,len(xyzs)):
            ret.append(xyzs[k]*(averdists[0]/averdists[k]))

        return np.nanmean(np.asarray(ret), axis = 0)





# Gram-Schmidt column orthonormalization
def gs(X, row_vecs=False, norm = True):
    if not row_vecs:
        X = X.T
    Y = X[0:1,:].copy()
    for i in range(1, X.shape[0]):
        proj = np.diag((X[i,:].dot(Y.T)/np.linalg.norm(Y,axis=1)**2).flat).dot(Y)
        Y = np.vstack((Y, X[i,:] - proj.sum(0)))
    if norm:
        Y = np.diag(1/np.linalg.norm(Y,axis=1)).dot(Y)
    if row_vecs:
        return Y
    else:
        return Y.T

class Triangulator():
    def __init__(self, p1, p2, f1, f2, c1, c2, dist1, dist2):
        self.p1 = p1 # p1 is a np.array of shape (n,2)
        self.p2 = p2 # p2 is same shape (should be same length)
        self.f1 = f1 # float
        self.f2 = f2
        self.c1 = c1 # np arrays of shape (1,2)
        self.c2 = c2
        self.R = None
        self.t = None
        self.dist1 = dist1
        self.dist2 = dist2
        self.normalize()

    # Normalize by subtracting out the optical center and dividing by the focal length
    def normalize(self):
        src1 = np.zeros((1,self.p1.shape[0], self.p1.shape[1]), dtype = np.float32)
        src2 = np.zeros((1,self.p1.shape[0], self.p1.shape[1]), dtype = np.float32)

        src1[0] = self.p1
        src2[0] = self.p2

        # make some camera matrices
        K1 = np.asarray([[self.f1, 0., self.c1[0]],
                         [0., self.f1, self.c1[1]],
                         [0., 0., 1.]])
        K2 = np.asarray([[self.f2, 0., self.c2[0]],
                         [0., self.f2, self.c2[1]],
                         [0., 0., 1.]])

        d1 = cv2.undistortPoints(src1, K1, np.asarray(self.dist1), P = None)[0]
        d2 = cv2.undistortPoints(src2, K2, np.asarray(self.dist2), P = None)[0]

        self.p1 = d1
        self.p2 = d2

    def getQuaternion(self):
        if self.R.any():
            Q = quaternions.quatFromRotationMatrix(gs(self.R))
            return Q.asVector()

    def triangulate(self):
        # get the fundamental matrix from OpenCV
        F = self.getFundamentalMat()
        # decompose
        U, D, V = np.linalg.svd(F)

        V = V.T
        D = np.diag(D)

        W = np.asarray([[0.,-1., 0.],
                        [1., 0., 0.],
                        [0., 0., 1.]])

        t = U[:,2].T # as per easyWand / MATLAB

        # Four possible orientations (rotation matrices) * two possible translations (forward or backward) = 8 possibilites
        Rs = [ U.dot(W.T).dot(V.T), U.dot(W).dot(V.T), U.dot(W.T).dot(-V.T), U.dot(W).dot(-V.T) ]

        # make lists for the triangulated points for all 8 cases, and the count of positive Z values for all 8 cases
        outs = list()
        plusses = list()

        # Put the points in a format OpenCV likes
        ps1 = np.zeros((2,len(self.p1)))
        ps2 = np.zeros((2,len(self.p1)))
        for k in range(len(self.p1)):
            ps1[:,k] = self.p1[k].T
            ps2[:,k] = self.p2[k].T

        # Check each one
        for R in Rs:
            # Is it a valid rotation matrix?
            if np.round(np.linalg.det(R)) != -1:
            # projection matrix for last camera
                P1 = np.asarray([[1.,0.,0.,0.],
                                [0., 1., 0., 0.],
                                [0.,0.,1, 0.]])

                # Positive translation
                P = np.zeros((3,4))
                P[:,:3] = R
                P[:,3] = t.T

                # Negative translation
                P_ = np.zeros((3,4))
                P_[:,:3] = R
                P_[:,3] = -t.T

                # Make arrays for traingulated points, backward and forward translation
                out = np.zeros((3,len(self.p1)))
                out_ = np.zeros((3,len(self.p1)))

                # Count variables
                p = 0
                p_ = 0

                # Triangulate one at a time so that homogenous coefficient doesn't get too small
                for k in range(len(self.p1)):
                    tmp = np.zeros((4,1))
                    tmp2 = np.zeros((4,1))

                    cv2.triangulatePoints(P, P1, ps1[:,k], ps2[:,k], tmp)
                    cv2.triangulatePoints(P_, P1, ps1[:,k], ps2[:,k], tmp2)

                    tmp = tmp*(1./tmp[3,0])
                    tmp2 = tmp2*(1./tmp2[3,0])

                    out[:,k] = tmp[:3,0]
                    out_[:,k] = tmp[:3,0]

                # Transpose for easier to work with format
                out = out.T
                out_ = out_.T

                for k in range(len(out[:,0])):
                    if out[k,2] > 0:
                        p += 1
                    if out_[k,2] > 0:
                        p_ += 1

                outs.append(out)
                outs.append(out_)

                plusses.append(p)
                plusses.append(p_)
            else:
                outs.append([])
                outs.append([])
                plusses.append(-1)
                plusses.append(-1)

        self.R = gs(Rs[int(np.floor(np.argmax(plusses)/2.))])
        if np.argmax(plusses) % 2 == 0:
            self.t = U[:,2].T
        else:
            self.t = -U[:,2].T
        
        pts = outs[np.argmax(plusses)]
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        x = pts[:,0]
        y = pts[:,1]
        z = pts[:,2]

        ax.scatter(x,y,z)
        plt.show()
        
        return outs[np.argmax(plusses)]

    def getFundamentalMat(self):
        return cv2.findFundamentalMat(self.p2, self.p1, method = cv2.cv.CV_FM_8POINT)[0]

"""
