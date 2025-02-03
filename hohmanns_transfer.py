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




def hohmanns_3d(sat):
    # Extract TLE data
    tle_name = sat.get("OBJECT_NAME", "")
    tle_line1 = sat.get("TLE_LINE1", "")
    tle_line2 = sat.get("TLE_LINE2", "")

    # Extract semi-major axis
    earth_radius = 6378  # km
    mu = 398600  # Earth's gravitational parameter (km^3/s^2)
    r1 = float(earth_radius)
    r2 = float(sat.get("SEMIMAJOR_AXIS"))
    print(f"r1: {r1:.2f} km/s")
    print(f"r2: {r2:.2f} km/s")

    # Semi-major axis of the transfer orbit
    a_transfer = (r1 + r2) / 2

    # Velocity calculations for circular orbits
    v1 = np.sqrt(mu / r1)  # Initial orbit velocity
    v2 = np.sqrt(mu / r2)  # Final orbit velocity

    # Calculate velocities at perigee of transfer orbit
    v_transfer1 = np.sqrt(mu * ((2 / r1) - (1 / a_transfer)))  # Velocity at perigee
    v_transfer2 = np.sqrt(mu * ((2 / r2) - (1 / a_transfer)))  # Velocity at apogee

    # Delta-v calculations
    delta_v1 = v_transfer1 - v1
    delta_v2 = v2 - v_transfer2
    total_delta_v = delta_v1 + delta_v2

    print(f"Total Delta V: {delta_v1:.2f} km/s")

    # Set up the plot
    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(111, projection='3d')
    ax.set_xlim(-r2 - 1000, r2 + 1000)
    ax.set_ylim(-r2 - 1000, r2 + 1000)
    ax.set_zlim(-r2 - 1000, r2 + 1000)
    ax.set_xlabel('X (km)')
    ax.set_ylabel('Y (km)')
    ax.set_zlabel('Z (km)')
    ax.set_title('3D Hohmann Transfer Maneuver')

    # Function to update the plot for animation
    def animate(frame):
        # Generate the angle for the orbit at each frame
        theta = np.linspace(0, 2 * np.pi * frame / 100, 300)
        
        # Initial orbit (LEO)
        x1 = r1 * np.cos(theta)
        y1 = r1 * np.sin(theta)
        z1 = np.zeros_like(x1)  # Flat in the XY plane
        
        # Final orbit (target orbit)
        x2 = r2 * np.cos(theta)
        y2 = r2 * np.sin(theta)
        z2 = np.zeros_like(x2)  # Flat in the XY plane
        
        # Elliptical transfer orbit
        eccentricity = (r2 - r1) / (r1 + r2)
        r_transfer = a_transfer * (1 - eccentricity ** 2) / (1 + eccentricity * np.cos(theta))
        x_transfer = r_transfer * np.cos(theta)
        y_transfer = r_transfer * np.sin(theta)
        z_transfer = np.zeros_like(x_transfer)  # Flat in the XY plane
        
        # Update the plot for current frame
        ax.cla()  # Clear previous frame
        ax.set_xlim(-r2 - 1000, r2 + 1000)
        ax.set_ylim(-r2 - 1000, r2 + 1000)
        ax.set_zlim(-r2 - 1000, r2 + 1000)
        
        # Plot the Earth (static)
        ax.scatter(0, 0, 0, color='b', s=1000, label="Earth", alpha=0.5)

        

        # Plot orbits
        #ax.plot(x1, y1, z1, 'g', label="Initial Orbit (LEO)")
        ax.plot(x2, y2, z2, 'r', label="Final Orbit (Target)")
        ax.plot(x_transfer, y_transfer, z_transfer, 'b--', label="Hohmann Transfer Orbit")
        
        # Update the satellite position for animation
        #ax.scatter(x1[frame % len(x1)], y1[frame % len(y1)], 0, color='g', s=50)
        ax.scatter(x2[frame % len(x2)], y2[frame % len(y2)], 0, color='r', s=50)
        # Update the satellite position for animation along the transfer orbit
        satellite_x = x_transfer[frame % len(x_transfer)]
        satellite_y = y_transfer[frame % len(y_transfer)]
        satellite_z = z_transfer[frame % len(z_transfer)]
        
        ax.scatter(satellite_x, satellite_y, satellite_z, color='k', s=100, label="Satellite")
        
        ax.legend()
        ax.legend(handlelength=1.0, handleheight=1.0, markerscale=0.01)
        ax.legend(loc="upper right", bbox_to_anchor=(1.1, 1.1))

    # Create the animation
    ani = animation.FuncAnimation(fig, animate, frames=200, interval=50, blit=False)

    # Show the plot
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

    hohmanns_3d(debris[105])  # Test Hohmann's transfer for a single debris satellite
    


    
    