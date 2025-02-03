import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from skyfield.api import Loader, EarthSatellite
import json
import sys

def makecubelimits(ax, centers=None, hw=None):
    lims = ax.get_xlim(), ax.get_ylim(), ax.get_zlim()
    if centers is None:
        centers = [0.5 * sum(pair) for pair in lims]

    if hw is None:
        widths = [pair[1] - pair[0] for pair in lims]
        hw = 0.5 * max(widths)
        ax.set_xlim(centers[0] - hw, centers[0] + hw)
        ax.set_ylim(centers[1] - hw, centers[1] + hw)
        ax.set_zlim(centers[2] - hw, centers[2] + hw)
    else:
        try:
            hwx, hwy, hwz = hw
            ax.set_xlim(centers[0] - hwx, centers[0] + hwx)
            ax.set_ylim(centers[1] - hwy, centers[1] + hwy)
            ax.set_zlim(centers[2] - hwz, centers[2] + hwz)
        except:
            ax.set_xlim(centers[0] - hw, centers[0] + hw)
            ax.set_ylim(centers[1] - hw, centers[1] + hw)
            ax.set_zlim(centers[2] - hw, centers[2] + hw)

    return centers, hw

def plot_multiple_satellite_orbits(tle_list, hours_range=(0, 3, 0.01)):
    """
    Plots 3D orbits for multiple satellites given their TLE data.

    Parameters:
    - tle_list: List of tuples (name, line1, line2) for satellites
    - hours_range: Tuple (start, stop, step) for time range in hours
    """
    # Load Skyfield data
    load = Loader('~/Documents/fishing/SkyData')
    ts = load.timescale()
    planets = load('de421.bsp')
    earth = planets['earth']

    # Create figure
    fig = plt.figure(figsize=[10, 8])
    ax = fig.add_subplot(1, 1, 1, projection='3d')

    hours = np.arange(*hours_range)

    count = 0

    for name, tle_line1, tle_line2 in tle_list:
        if count == 10:
            return
        else:
            # Create satellite object
            satellite = EarthSatellite(tle_line1, tle_line2, name, ts)

            # Get positions over time
            time = ts.utc(2018, 2, 7, hours)
            positions = satellite.at(time).position.km

            # Plot orbit
            x, y, z = positions
            ax.plot(x, y, z, label=name)

    # Draw Earth lat/lon grid
    re = 6378  # Earth radius in km
    theta = np.linspace(0, 2 * np.pi, 201)
    cth, sth, zth = np.cos(theta), np.sin(theta), np.zeros_like(theta)

    # Longitude lines
    for phi in np.radians(np.arange(0, 180, 15)):
        cph, sph = np.cos(phi), np.sin(phi)
        lon = np.vstack((re * cth * cph - re * zth * sph,
                         re * zth * cph + re * cth * sph,
                         re * sth))
        ax.plot(*lon, '-k')

    # Latitude lines
    for phi in np.radians(np.arange(-75, 90, 15)):
        cph, sph = np.cos(phi), np.sin(phi)
        lat = np.vstack((re * cth * cph, re * sth * cph, re * zth + re * sph))
        ax.plot(*lat, '-k')

    # Adjust limits and legend
    centers, hw = makecubelimits(ax)
    ax.legend()
    ax.set_xlabel("X (km)")
    ax.set_ylabel("Y (km)")
    ax.set_zlabel("Z (km)")
    ax.set_title("3D Satellite Orbits")

    plt.show()


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


data = read_json_file("e-formatted.json")
print(f"data: {data[1]}")   
tle_list = [(sat["OBJECT_NAME"], sat["TLE_LINE1"], sat["TLE_LINE2"]) for sat in data]

plot_multiple_satellite_orbits(tle_list)
