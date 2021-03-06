##################################################
## When loaded as a programmable filter in Paraview 5.10, 
## this script loads XYZ coordinates of particles from particleTracer to link neighbors in time
## Input: particle tracks, output: neighbor lines and neighbor displacement (neighborDist)
##################################################
## Daniel Carlson
## 2021 Nov
## Okinawa Institute of Science and Technology
##################################################

import math
import numpy as np
from vtk.numpy_interface import algorithms as algs
#from vtk.numpy_interface import dataset_adapter as dsa

X = inputs[0].Points[:,0]
Y = inputs[0].Points[:,1]
Z = inputs[0].Points[:,2]

FT = np.array(inputs[0].PointData["FT"]) #look for FT variable to pass along pipeline
defMag = np.array(inputs[0].PointData["defMag"]) #look for FT variable to pass along pipeline
pAge = inputs[0].PointData["InjectionStepId"] #default injection name in time from particleTracer
pSource = np.array(inputs[0].PointData["InjectedPointId"])

UPT = np.array(inputs[0].PointData["U"])
uPt = UPT[:,0]
vPt = UPT[:,1]
wPt = UPT[:,2]

stepsAll, stepCounts = np.unique(pAge, return_counts = True)

indVal = stepCounts > 2 #minimum 3 pts per ring
steps = stepsAll[indVal]

xn = np.array(X)
yn = np.array(Y)
zn = np.array(Z)

pn = np.array(pAge)

pdo = self.GetPolyDataOutput()
pts = vtk.vtkPoints()

kk = 0
nn = 0
ptsLen = np.array([None for _ in range(len(steps))])

difOut = 0*xn
thetaOut = 0*xn
FTOUT = 0*xn
DEFOUT = 0*xn
ptDist = 0*xn
ptDel = 0*xn
nPts = 0*xn
injectPtOut = 0*xn
UOUT = 0*xn
VOUT = 0*xn
WOUT = 0*xn

for jj in steps:
    
    indTmp = pn == jj

    xInd = xn[indTmp]
    yInd = yn[indTmp]
    zInd = zn[indTmp]
    
    xMean = np.mean(xInd)
    yMean = np.mean(yInd)
    zMean = np.mean(zInd)
       
    UOUT[indTmp] = uPt[indTmp]
    VOUT[indTmp] = vPt[indTmp]
    WOUT[indTmp] = wPt[indTmp]
    
    ptDist[indTmp] = np.sqrt((xInd-xMean)**2+(yInd-yMean)**2+(zInd-zMean)**2)
    ptDel[indTmp] = 1+abs(ptDist[indTmp]-np.mean(ptDist[indTmp])) / np.mean(ptDist[indTmp])

    FTInd = FT[indTmp]
    DefInd = defMag[indTmp]
   
    sourceInd = pSource[indTmp]
    
    ptsLen[nn] = len(xInd)
    
    difPt = 0*xInd
    thetaPt = 0*xInd
    
    ##difPt start and end
    difPt[0] = math.sqrt((xInd[1]-xInd[-1])**2 + (yInd[1]-yInd[-1])**2 + (zInd[1]-zInd[-1])**2)
    difPt[-1] = math.sqrt((xInd[0]-xInd[-1-1])**2 + (yInd[0]-yInd[-1-1])**2 + (zInd[0]-zInd[-1-1])**2)
    
    ##start theta
    X1 = xInd[1]-xInd[-1] 
    X0 = xInd[0]-xInd[-1] 
        
    Y1 = yInd[1]-yInd[-1] 
    Y0 = yInd[0]-yInd[-1] 
        
    Z1 = zInd[1]-zInd[-1] 
    Z0 = zInd[0]-zInd[-1] 
        
    AA = math.sqrt((X1)**2 + (Y1)**2 + (Z1)**2)
    BB = math.sqrt((X0)**2 + (Y0)**2 + (Z0)**2)
    CC = math.sqrt((X1-X0)**2 + (Y1-Y0)**2 + (Z1-Z0)**2)
    thetaPt[0] = np.arccos((AA**2 - BB**2 - CC**2)/(-2*BB*CC))
    
    ##end theta
    X1 = xInd[0]-xInd[-1-1] 
    X0 = xInd[-1]-xInd[-1-1] 
        
    Y1 = yInd[0]-yInd[-1-1] 
    Y0 = yInd[-1]-yInd[-1-1] 
        
    Z1 = zInd[0]-zInd[-1-1] 
    Z0 = zInd[-1]-zInd[-1-1] 
        
    AA = math.sqrt((X1)**2 + (Y1)**2 + (Z1)**2)
    BB = math.sqrt((X0)**2 + (Y0)**2 + (Z0)**2)
    CC = math.sqrt((X1-X0)**2 + (Y1-Y0)**2 + (Z1-Z0)**2)
    thetaPt[-1] = np.arccos((AA**2 - BB**2 - CC**2)/(-2*BB*CC))
        
    
    for i in range(1,len(xInd)-1):
       difPt[i] = math.sqrt((xInd[i+1]-xInd[i-1])**2 + (yInd[i+1]-yInd[i-1])**2 + (zInd[i+1]-zInd[i-1])**2)
    
    for i in range(1,len(xInd)-1):
        X1 = xInd[i+1]-xInd[i-1] 
        X0 = xInd[i]-xInd[i-1] 
        
        Y1 = yInd[i+1]-yInd[i-1] 
        Y0 = yInd[i]-yInd[i-1] 
        
        Z1 = zInd[i+1]-zInd[i-1]
        Z0 = zInd[i]-zInd[i-1]
        
        AA = math.sqrt((X1)**2 + (Y1)**2 + (Z1)**2)
        BB = math.sqrt((X0)**2 + (Y0)**2 + (Z0)**2)
        CC = math.sqrt((X1-X0)**2 + (Y1-Y0)**2 + (Z1-Z0)**2)
        
        thetaPt[i] = np.arccos((AA**2 - BB**2 - CC**2)/(-2*BB*CC))
        
    difOut[indTmp] = difPt
    thetaOut[indTmp] = thetaPt
    FTOUT[indTmp]= FTInd
    DEFOUT[indTmp]= DefInd
    nPts[indTmp] = ptsLen[nn]
    injectPtOut[indTmp] = sourceInd
    
    coordinates = algs.make_vector(xInd, yInd, zInd)
    for ii in range(0,len(xInd)):
        pts.InsertPoint(kk,coordinates[ii,0],coordinates[ii,1],coordinates[ii,2])
        kk = kk+1
    nn = nn +1

output.PointData.append(difOut, 'neighborDist')
output.PointData.append(thetaOut, 'neighborTheta')        
output.PointData.append(FTOUT, 'FT')
output.PointData.append(DEFOUT, 'defMag')    
output.PointData.append(ptDist, 'ptDist')
output.PointData.append(ptDel, 'ptDel')      
output.PointData.append(nPts, 'nPts')      
output.PointData.append(injectPtOut, 'ptSource')

output.PointData.append(UOUT, 'UOUT') 
output.PointData.append(VOUT, 'VOUT') 
output.PointData.append(WOUT, 'WOUT')      

pdo.SetPoints(pts)
pdo.Allocate(len(steps),1)

for jj in range(0,len(steps)-1):
    aPolyLine = vtk.vtkPolyLine()
    aPolyLine.GetPointIds().SetNumberOfIds(ptsLen[jj])
    
    if jj == 0:
        ptStart = 0
    else:
        ptStart = np.sum(ptsLen[0:jj])
          
    for ii in range(0,ptsLen[jj]):
        aPolyLine.GetPointIds().SetId(ii, ptStart+ii)
        
    pdo.InsertNextCell(aPolyLine.GetCellType(), aPolyLine.GetPointIds())    
    