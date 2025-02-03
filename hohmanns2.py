import json
import sys
import math
import csv
import random

from skyfield.timelib import Time
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import matplotlib.animation as animation

import numpy as np
from skyfield.api import load, Topos, EarthSatellite
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

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

# Constants
mu = 398600  # Earth's gravitational parameter in km^3/s^2
earth_radius = 6378  # Earth's radius in km

def hohmann_transfer_orbit(r1, r2, num_points=300):
    """Calculate the Hohmann transfer orbit from r1 to r2."""
    # Semi-major axis of the transfer orbit
    a_transfer = (r1 + r2) / 2
    
    # Orbital eccentricity
    e_transfer = (r2 - r1) / (r1 + r2)
    
    # Define the angular range for plotting
    theta = np.linspace(0, 2 * np.pi, num_points)
    
    # Elliptical transfer orbit equation
    r_transfer = a_transfer * (1 - e_transfer**2) / (1 + e_transfer * np.cos(theta))
    
    # Parametric equations for the transfer orbit
    x_transfer = r_transfer * np.cos(theta)
    y_transfer = r_transfer * np.sin(theta)
    z_transfer = np.zeros_like(x_transfer)  # Flat in the XY plane
    
    return x_transfer, y_transfer, z_transfer, theta

def apply_inclination_change(x, y, z, inclination_deg):
    """Apply inclination change to a given orbit in 3D."""
    inclination_rad = np.radians(inclination_deg)
    
    # Rotation matrix for inclination change about the X-axis
    rotation_matrix = np.array([
        [1, 0, 0],
        [0, np.cos(inclination_rad), -np.sin(inclination_rad)],
        [0, np.sin(inclination_rad), np.cos(inclination_rad)]
    ])
    
    # Apply rotation to each point in the orbit
    new_orbit = np.dot(rotation_matrix, np.vstack([x, y, z]))
    
    return new_orbit[0], new_orbit[1], new_orbit[2]

def apply_raan_change(x, y, z, raan_deg):
    """Apply RAAN change to a given orbit in 3D."""
    raan_rad = np.radians(raan_deg)
    
    # Rotation matrix for RAAN change about the Z-axis
    rotation_matrix = np.array([
        [np.cos(raan_rad), np.sin(raan_rad), 0],
        [-np.sin(raan_rad), np.cos(raan_rad), 0],
        [0, 0, 1]
    ])
    
    # Apply rotation to each point in the orbit
    new_orbit = np.dot(rotation_matrix, np.vstack([x, y, z]))
    
    return new_orbit[0], new_orbit[1], new_orbit[2]

def plot_orbit_animation(r1, r2, inclination_change, raan_change, num_frames=300):
    """Plot and animate the 3D Hohmann transfer including initial, transfer, and final orbits."""
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, projection='3d')

    # Initial orbit (circular orbit at r1)
    theta = np.linspace(0, 2 * np.pi, 300)
    x1 = r1 * np.cos(theta)
    y1 = r1 * np.sin(theta)
    z1 = np.zeros_like(x1)  # Flat in the XY plane

    # Final orbit (circular orbit at r2)
    x2 = r2 * np.cos(theta)
    y2 = r2 * np.sin(theta)
    z2 = np.zeros_like(x2)  # Flat in the XY plane

    # Plot the orbits
    ax.plot(x1, y1, z1, 'g', label="Initial Orbit (r1)")
    ax.plot(x2, y2, z2, 'r', label="Final Orbit (r2)")

    # Apply RAAN and inclination changes to the orbits
    x1_incl, y1_incl, z1_incl = apply_inclination_change(x1, y1, z1, inclination_change)
    x2_incl, y2_incl, z2_incl = apply_inclination_change(x2, y2, z2, inclination_change)

    # Plot the inclination-changed orbits
    ax.plot(x1_incl, y1_incl, z1_incl, 'b', label="Inclined Initial Orbit")
    ax.plot(x2_incl, y2_incl, z2_incl, 'm', label="Inclined Final Orbit")

    # Apply RAAN changes
    x1_raan, y1_raan, z1_raan = apply_raan_change(x1_incl, y1_incl, z1_incl, raan_change)
    x2_raan, y2_raan, z2_raan = apply_raan_change(x2_incl, y2_incl, z2_incl, raan_change)

    # Plot the RAAN-changed orbits
    ax.plot(x1_raan, y1_raan, z1_raan, 'c', label="RAAN-Changed Initial Orbit")
    ax.plot(x2_raan, y2_raan, z2_raan, 'y', label="RAAN-Changed Final Orbit")

    # Plot Earth at the origin
    ax.scatter(0, 0, 0, color='b', s=30000, label="Earth", alpha=0.5)

    # Set up the transfer orbit
    x_transfer, y_transfer, z_transfer, theta = hohmann_transfer_orbit(r1, r2)

    # Animation function
    def update(frame):
        ax.cla()  # Clear previous plot
        ax.set_xlabel('X (km)')
        ax.set_ylabel('Y (km)')
        ax.set_zlabel('Z (km)')
        ax.set_title('3D Hohmann Transfer Maneuver')

        # Re-plot the orbits with updated positions
        ax.plot(x1, y1, z1, 'g', label="Initial Orbit (r1)")
        ax.plot(x2, y2, z2, 'r', label="Final Orbit (r2)")

        ax.plot(x1_incl, y1_incl, z1_incl, 'b', label="Inclined Initial Orbit")
        ax.plot(x2_incl, y2_incl, z2_incl, 'm', label="Inclined Final Orbit")

        ax.plot(x1_raan, y1_raan, z1_raan, 'c', label="RAAN-Changed Initial Orbit")
        ax.plot(x2_raan, y2_raan, z2_raan, 'y', label="RAAN-Changed Final Orbit")

        # Update the transfer orbit as the animation progresses
        transfer_x = r1 * np.cos(theta[frame])
        transfer_y = r1 * np.sin(theta[frame])
        ax.plot([0, transfer_x], [0, transfer_y], [0, 0], 'b-', label="Transfer Orbit", alpha=0.6)

        # Earth at the origin
        ax.scatter(0, 0, 0, color='b', s=35000, label="Earth", alpha=0.5)

        # Set the limits of the plot
        ax.set_xlim([-r2-1000, r2+1000])
        ax.set_ylim([-r2-1000, r2+1000])
        ax.set_zlim([-r2-1000, r2+1000])

    # Create the animation
    ani = animation.FuncAnimation(fig, update, frames=num_frames, interval=100)

    plt.show()



if __name__ == "__main__":
    
    if len(sys.argv) != 2:
        print("Usage: python hohmanns_and_greedy_oneplane.py input_file")
        sys.exit(1)

    input_file = sys.argv[1]

    print(f"Reading from file {input_file}")
    json_data = read_json_file(input_file)

    for sat in json_data:
        debris = filter_debris_satellites(json_data)

    removal_sat = debris[105]

    # Extract TLE data
    sat_iclination = float(removal_sat.get("INCLINATION"))
    sat_raan = float(removal_sat.get("RA_OF_ASC_NODE"))
    sat_semimajor_axis = float(removal_sat.get("SEMIMAJOR_AXIS"))

    count =0
    tle_data = []

    for sat in debris:
        if float(sat.get("INCLINATION")) < (sat_iclination + 10) and float(sat.get("INCLINATION")) > (sat_iclination - 10) and float(sat.get("RA_OF_ASC_NODE")) < (sat_raan + 100) and float(sat.get("RA_OF_ASC_NODE")) > (sat_raan - 100):
            if float(sat.get("SEMIMAJOR_AXIS")) < (sat_semimajor_axis + 50) and float(sat.get("SEMIMAJOR_AXIS")) > (sat_semimajor_axis - 50):
                count += 1

    print(f"count: {count}")


    # Example usage:
    initial_altitude = sat_semimajor_axis - 6378  # km (starting orbit)
    final_altitude = float(debris[5].get("SEMIMAJOR_AXIS")) - 6378  # km (target orbit)
    inclination_change = abs(sat_iclination - float(debris[5].get("INCLINATION")))  # degrees
    raan_change =  abs(sat_raan - float(debris[5].get("RA_OF_ASC_NODE")))  # degrees
    at_apogee = True  # Change inclination at apogee (set to False for perigee)
    initial_inclination = sat_iclination # degrees (initial orbit inclination)
    final_inclination = float(debris[5].get("INCLINATION"))  # degrees (target orbit inclination)

    r1 = earth_radius + initial_altitude
    r2 = earth_radius + final_altitude

    # Plot and animate the transfer
    plot_orbit_animation(r1, r2, inclination_change, raan_change)

    #dv1, dv2, dv_inc, dv_raan, total_dv = total_maneuver_delta_v(initial_altitude, final_altitude, inclination_change, raan_change, at_apogee, initial_inclination, final_inclination)
    