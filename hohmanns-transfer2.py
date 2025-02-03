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
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation


import numpy as np
import matplotlib.pyplot as plt
from poliastro.bodies import Earth
from poliastro.twobody import Orbit
from poliastro.maneuver import Maneuver
from poliastro.util import norm

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


def hohmanns(sat):
    # Extract TLE data
    tle_name = sat.get("OBJECT_NAME", "")
    tle_line1 = sat.get("TLE_LINE1", "")
    tle_line2 = sat.get("TLE_LINE2", "")

    # Extract semi-major axis
    earth_radius = 6378  # km
    mu = 398600  # Earth's gravitational parameter (km^3/s^2)

    mean_motion = float(tle_line2.split()[7])  # Mean motion (rev/day)
    orbital_period = 86400 / mean_motion  # Convert to seconds
    semi_major_axis = (mu * (orbital_period / (2 * np.pi))**2) ** (1/3)  # Kepler's 3rd law
    h2 = semi_major_axis - earth_radius  # Altitude above Earth

    print(f"Derived Altitude from TLE: {h2:.2f} km")

    # Initial Orbit (LEO Example)
    h1 = 500  # Initial orbit altitude in km
    r1 = earth_radius + h1  # Initial orbit radius
    r2 = earth_radius + h2  # Final orbit radius (from TLE)

    # Orbital velocities
    v1 = np.sqrt(mu / r1)  # Initial circular orbit velocity
    v2 = np.sqrt(mu / r2)  # Final circular orbit velocity

    # Transfer orbit calculations
    a_transfer = (r1 + r2) / 2  # Semi-major axis of transfer orbit
    v_transfer1 = np.sqrt(mu * (2/r1 - 1/a_transfer))  # Velocity after 1st burn
    v_transfer2 = np.sqrt(mu * (2/r2 - 1/a_transfer))  # Velocity before 2nd burn

    # Delta-v calculations
    delta_v1 = v_transfer1 - v1  # Burn 1 (LEO to elliptical transfer)
    delta_v2 = v2 - v_transfer2   # Burn 2 (elliptical transfer to final circular)

    print(f"Delta-v for first burn: {delta_v1:.2f} km/s")
    print(f"Delta-v for second burn: {delta_v2:.2f} km/s")

    # Define plot
    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(111, projection='3d')

    # Plot Earth
    u = np.linspace(0, 2 * np.pi, 100)
    v = np.linspace(0, np.pi, 100)
    x = earth_radius * np.outer(np.cos(u), np.sin(v))
    y = earth_radius * np.outer(np.sin(u), np.sin(v))
    z = earth_radius * np.outer(np.ones(np.size(u)), np.cos(v))
    ax.plot_surface(x, y, z, color='b', alpha=0.3, label="Earth")

    # Generate angles for orbits
    theta = np.linspace(0, 2 * np.pi, 300)

    # Compute orbit paths
    x1, y1, z1 = r1 * np.cos(theta), r1 * np.sin(theta), np.zeros_like(theta)  # Initial orbit (LEO)
    x2, y2, z2 = r2 * np.cos(theta), r2 * np.sin(theta), np.zeros_like(theta)  # Final orbit
    r_transfer = (r1 * (1 + np.cos(theta))) / (1 + (r1/r2 - 1) * np.cos(theta))  # Transfer orbit
    x_transfer, y_transfer, z_transfer = r_transfer * np.cos(theta), r_transfer * np.sin(theta), np.zeros_like(theta)

    # Plot initial and final orbits
    ax.plot(x1, y1, z1, 'g', label="Initial Orbit (LEO)")
    ax.plot(x2, y2, z2, 'r', label="Final Orbit (TLE Target)")
    ax.plot(x_transfer, y_transfer, z_transfer, 'b--', label="Hohmann Transfer Orbit")

    # Satellite markers
    sat1, = ax.plot([], [], [], 'go', markersize=6, label="Satellite (Initial)")
    sat2, = ax.plot([], [], [], 'ro', markersize=6, label="Satellite (Final)")
    sat_transfer, = ax.plot([], [], [], 'bo', markersize=6, label="Satellite (Transfer)")

    # Animation update function
    def update(frame):
        num_steps = len(theta)

        # Initial orbit animation
        if frame < num_steps:
            sat1.set_data(np.array([x1[frame]]), np.array([y1[frame]]))
            sat1.set_3d_properties(np.array([z1[frame]]))
            return sat1,

        # Transfer orbit animation
        elif frame < 2 * num_steps:
            sat_transfer.set_data(np.array([x_transfer[frame - num_steps]]), np.array([y_transfer[frame - num_steps]]))
            sat_transfer.set_3d_properties(np.array([z_transfer[frame - num_steps]]))
            return sat_transfer,

        # Final orbit animation
        else:
            sat2.set_data(np.array([x2[frame - 2 * num_steps]]), np.array([y2[frame - 2 * num_steps]]))
            sat2.set_3d_properties(np.array([z2[frame - 2 * num_steps]]))
            return sat2,

    # Animate
    ani = animation.FuncAnimation(fig, update, frames=3 * len(theta), interval=50, blit=True)

    # Labels and legend
    ax.set_title(f"Hohmann Transfer to {tle_name}")
    ax.set_xlabel("X (km)")
    ax.set_ylabel("Y (km)")
    ax.set_zlabel("Z (km)")
    ax.legend()
    plt.show()


if __name__ == "__main__":
    
    if len(sys.argv) != 2:
        print("Usage: python hohmanns-transfer2.py input_file")
        sys.exit(1)

    input_file = sys.argv[1]

    print(f"Reading from file {input_file}")
    json_data = read_json_file(input_file)

    for sat in json_data:
        debris = filter_debris_satellites(json_data)

    hohmanns(debris[1])  # Test Hohmann's transfer for a single debris satellite
    

