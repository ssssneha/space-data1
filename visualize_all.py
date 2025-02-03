import json
import sys
import math
import csv
import random

from skyfield.api import Loader, EarthSatellite
from skyfield.timelib import Time
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# My modules
import satellite
import satutils
import bot

def read_json_file(file_path):
    try:
        with open(file_path, 'r') as file:
            json_data = json.load(file)
        return json_data

    except FileNotFoundError:
        print(f"Error: File not found. Please check the file path.")
        return None

    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return None
    
def filter_debris_satellites(json_data):
    debris = []
    for sat in json_data:
        if sat.get("OBJECT_TYPE") == "DEBRIS":
            debris.append(sat)
    return debris

def plot_3d_satellites(L1, L2, ax):

    def makecubelimits(axis, centers=None, hw=None):
        lims = ax.get_xlim(), ax.get_ylim(), ax.get_zlim()
        if centers == None:
            centers = [0.5*sum(pair) for pair in lims] 

        if hw == None:
            widths  = [pair[1] - pair[0] for pair in lims]
            hw      = 0.5*max(widths)
            ax.set_xlim(centers[0]-hw, centers[0]+hw)
            ax.set_ylim(centers[1]-hw, centers[1]+hw)
            ax.set_zlim(centers[2]-hw, centers[2]+hw)
            print("hw was None so set to:", hw)
        else:
            try:
                hwx, hwy, hwz = hw
                print("ok hw requested: ", hwx, hwy, hwz)

                ax.set_xlim(centers[0]-hwx, centers[0]+hwx)
                ax.set_ylim(centers[1]-hwy, centers[1]+hwy)
                ax.set_zlim(centers[2]-hwz, centers[2]+hwz)
            except:
                print("nope hw requested: ", hw)
                ax.set_xlim(centers[0]-hw, centers[0]+hw)
                ax.set_ylim(centers[1]-hw, centers[1]+hw)
                ax.set_zlim(centers[2]-hw, centers[2]+hw)

        return centers, hw
    
    load = Loader('~/Documents/fishing/SkyData')
    ts = load.timescale()

    Roadster = EarthSatellite(L1, L2)
    hours = np.arange(0, 3, 0.01)
    time = ts.utc(2018, 2, 7, hours)
    Rpos = Roadster.at(time).position.km

    x, y, z = Rpos
    ax.plot(x, y, z, label=f"Satellite: {Roadster.name}")  # Plot orbit

    # Add Earth's surface as a sphere (optional for visualization)
    

    halfpi, pi, twopi = [f*np.pi for f in [0.5, 1, 2]]
    degs, rads = 180/pi, pi/180

    load = Loader('~/Documents/fishing/SkyData')
    data = load('de421.bsp')
    ts   = load.timescale()

    planets = load('de421.bsp')
    earth   = planets['earth']

    Roadster = EarthSatellite(L1, L2)

    #print(Roadster.epoch.tt)
    hours = np.arange(0, 3, 0.01)

    time = ts.utc(2018, 2, 7, hours)

    Rpos    = Roadster.at(time).position.km
    Rposecl = Roadster.at(time).ecliptic_position().km

    #print(Rpos.shape)

    re = 6378.

    theta = np.linspace(0, twopi, 201)
    cth, sth, zth = [f(theta) for f in [np.cos, np.sin, np.zeros_like]]
    lon0 = re*np.vstack((cth, zth, sth))
    lons = []
    for phi in rads*np.arange(0, 180, 15):
        cph, sph = [f(phi) for f in [np.cos, np.sin]]
        lon = np.vstack((lon0[0]*cph - lon0[1]*sph,
                        lon0[1]*cph + lon0[0]*sph,
                        lon0[2]) )
        lons.append(lon)

    lat0 = re*np.vstack((cth, sth, zth))
    lats = []
    for phi in rads*np.arange(-75, 90, 15):
        cph, sph = [f(phi) for f in [np.cos, np.sin]]
        lat = re*np.vstack((cth*cph, sth*cph, zth+sph))
        lats.append(lat)

    r_Roadster = np.sqrt((Rpos**2).sum(axis=0))
    alt_roadster = r_Roadster - re

    plt.plot(hours, r_Roadster)
    plt.plot(hours, alt_roadster)
    

# main

if __name__ == "__main__":
    
    if len(sys.argv) != 2:
        print("Usage: python visualize_all.py input_file")
        sys.exit(1)

    input_file = sys.argv[1]

    print(f"Reading from file {input_file}")
    json_data = read_json_file(input_file)

    for sat in json_data:
        debris = filter_debris_satellites(json_data)
    
    print(f"Total debris satellites: {len(debris)}")
    i = 0

    # Create a shared 3D plot
    fig = plt.figure(figsize=[10, 8])
    ax = fig.add_subplot(111, projection="3d")
    ax.set_title("Orbits of Satellites and Debris")
    ax.set_xlabel("X (km)")
    ax.set_ylabel("Y (km)")
    ax.set_zlabel("Z (km)")

    re = 6378.0
    u = np.linspace(0, 2 * np.pi, 100)
    v = np.linspace(0, np.pi, 100)
    xs = re * np.outer(np.cos(u), np.sin(v))
    ys = re * np.outer(np.sin(u), np.sin(v))
    zs = re * np.outer(np.ones(np.size(u)), np.cos(v))
    ax.plot_wireframe(xs, ys, zs, color="black", alpha=0.1)

    for sat in debris:
        i += 1
        L1 = sat["TLE_LINE1"]
        L2 = sat["TLE_LINE2"]
        plot_3d_satellites(L1, L2, ax)
        if i == 100:
            break

    if True:
        plt.figure()
        plt.xlabel('hours', fontsize=14)
        plt.ylabel('Geocenter radius or altitude (km)', fontsize=14)

    

    plt.show()
    print(f"done")

    


