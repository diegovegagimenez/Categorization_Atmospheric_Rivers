# Simplified script SCALE ARs. 


import numpy as np
import time, datetime, sys
import multiprocessing
from multiprocessing import *
import sys
from netCDF4 import Dataset

File = Dataset(
    "./ERA5_Original_6h_East_West_1979.nc")  # Data from ERA5 over the region of interest. This data contains 5 days.
# The analysis will be carried out the second, third and fourth day (72 hours).

# This script does not use XARRAY and Cartopy. It makes use of numpy and generates data designed to plot in Basemap.
# Thus, a latitudinal correction ::-1 is necessary.

Lats = File.variables["latitude"][::-1]

print(Lats)
Lons = File.variables["longitude"][:]
East = File.variables["p71.162"][:, ::-1, :]
North = File.variables["p72.162"][:, ::-1, :]
IVT = np.sqrt(East ** 2 + North ** 2)

l1 = 250
l2 = 500
l3 = 750
l4 = 1000
l5 = 1250


def Eventer(max_IVT, persistence):  # EVENT CLASIFICATION MODULE. Time Resolution: 1h

    CAT = 0

    if max_IVT >= l1 and max_IVT < l2 and persistence < 24:
        CAT = 0
    if max_IVT >= l1 and max_IVT < l2 and persistence >= 24 and persistence < 48:
        CAT = 1
    if max_IVT >= l1 and max_IVT < l2 and persistence >= 48:
        CAT = 2

    if max_IVT >= l2 and max_IVT < l3 and persistence < 24:
        CAT = 1
    if max_IVT >= l2 and max_IVT < l3 and persistence >= 24 and persistence < 48:
        CAT = 2
    if max_IVT >= l2 and max_IVT < l3 and persistence >= 48:
        CAT = 3

    if max_IVT >= l3 and max_IVT < l4 and persistence < 24:
        CAT = 2
    if max_IVT >= l3 and max_IVT < l4 and persistence >= 24 and persistence < 48:
        CAT = 3
    if max_IVT >= l3 and max_IVT < l4 and persistence >= 48:
        CAT = 4

    if max_IVT >= l4 and max_IVT < l5 and persistence < 24:
        CAT = 3
    if max_IVT >= l4 and max_IVT < l5 and persistence >= 24 and persistence < 48:
        CAT = 4
    if max_IVT >= l4 and max_IVT < l5 and persistence >= 48:
        CAT = 5

    if max_IVT >= l5 and persistence < 24:
        CAT = 4
    if max_IVT >= l5 and persistence >= 24 and persistence < 48:
        CAT = 5
    if max_IVT >= l5 and persistence >= 48:
        CAT = 5

    return CAT


def Main_Analyzer(Array):
    EVENTS = np.zeros(shape=(Array.shape[0]))

    t = 0

    print(Array.shape)

    while t < Array.shape[0]:

        if Array[t] < l1:
            t = t + 1
        elif Array[t] >= l1:

            event_IVT = []
            event_t = []
            event_IVT = np.array(event_IVT)
            event_t = np.array(event_t)

            event_IVT = np.append(event_IVT, Array[t])
            event_t = np.append(event_t, t)

            go = 1
            t = t + 1
            while go == 1:
                if t < Array.shape[0]:

                    if Array[t] >= l1:
                        event_IVT = np.append(event_IVT, Array[t])
                        event_t = np.append(event_t, t)
                        t = t + 1
                    else:
                        go = 0
                        CAT = Eventer(np.max(event_IVT), len(event_t))
                        for i in event_t:
                            EVENTS[int(i)] = CAT

                else:
                    go = 0
                    CAT = Eventer(np.max(event_IVT), len(event_t))
                    for i in event_t:
                        EVENTS[int(i)] = CAT

    return EVENTS


OUTPUT = np.zeros(shape=(Lats.shape[0], Lons.shape[0]))

for n in range(Lats.shape[0]):
    print("%s out of %s" % (n, Lats.shape[0] - 1))
    for m in range(Lons.shape[0]):
        ARRAY = IVT[:, n, m]
        ARRAY = Main_Analyzer(ARRAY)
        ARRAY_72h = ARRAY[24:-24]
        max = np.max(ARRAY_72h)
        OUTPUT[n, m] = max

np.save("Output_Detections_Categories_v2", OUTPUT)
# This output provides the max category detected at each point throughout the 72-hour period
# Remember that latitudes have been transformed with respect to the original ERA5 Grid.
