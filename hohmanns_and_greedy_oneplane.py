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

# Constants
mu = 398600  # Earth's gravitational parameter in km³/s²
earth_radius_km = 6378  # Earth's radius in km


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

def hohmanns_first(sat):
    # Extract TLE data
    tle_name = sat.get("OBJECT_NAME", "")
    tle_line1 = sat.get("TLE_LINE1", "")
    tle_line2 = sat.get("TLE_LINE2", "")

    print(f"First Debris to be collected: {tle_name}")

    # Extract semi-major axis
    earth_radius = 6378  # km
    mu = 398600  # Earth's gravitational parameter (km^3/s^2)

    r1 = float(earth_radius)
    r2 = float(sat.get("SEMIMAJOR_AXIS"))
    #print(f"r1: {r1:.2f} km/s")
    #print(f"r2: {r2:.2f} km/s")

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

    # Transfer time
    transfer_time = (1/2 * (2 * np.pi * np.sqrt(a_transfer**3 / mu)))/ 3600

    #print(f"Total Delta V: {total_delta_v:.2f} km/s")

    return total_delta_v, transfer_time


def hohmann_transfer_delta_v(r1, r2):
    """Calculates delta-v for a Hohmann transfer between two circular orbits."""
    # Initial and final orbit velocities
    v1 = np.sqrt(mu / r1)
    v2 = np.sqrt(mu / r2)

    # Semi-major axis of transfer orbit
    a_transfer = (r1 + r2) / 2

    # Transfer orbit velocities
    v_transfer1 = np.sqrt(mu * (2 / r1 - 1 / a_transfer))
    v_transfer2 = np.sqrt(mu * (2 / r2 - 1 / a_transfer))

    # Delta-v for the two burns
    delta_v1 = v_transfer1 - v1  # Burn at initial orbit
    delta_v2 = v2 - v_transfer2  # Burn at final orbit

    return delta_v1, delta_v2, a_transfer

def calculate_orbital_period(a):
    """Calculates the orbital period using Kepler's third law."""
    return 2 * np.pi * np.sqrt(a**3 / mu)

def calculate_transfer_time(r1, r2):
    """Calculates the time taken for the Hohmann transfer (half-period of the transfer orbit)."""
    # Semi-major axis of the transfer orbit
    a_transfer = (r1 + r2) / 2
    
    # Orbital period of the transfer orbit
    T_transfer = calculate_orbital_period(a_transfer)
    
    # Transfer time is half the orbital period
    return T_transfer / 2

def inclination_change_delta_v(altitude_km, inclination_change_deg, is_at_apogee=True):
    """Calculates delta-v for a plane change at a given altitude at perigee or apogee."""
    # Convert inclination change to radians
    inclination_change_rad = np.radians(inclination_change_deg)

    # Compute orbital velocity at given altitude
    orbital_radius = earth_radius_km + altitude_km
    velocity = np.sqrt(mu / orbital_radius)  # km/s

    # Compute delta-v for inclination change
    delta_v = 2 * velocity * np.sin(inclination_change_rad / 2)

    # If we're changing at apogee, no change is needed for this part
    if not is_at_apogee:
        delta_v /= np.sqrt(2)  # Less efficient at perigee (requires lower delta-v)

    return delta_v

def raan_change_delta_v(altitude_km, raan_change_deg, inclination_deg):
    """Calculates delta-v for a RAAN change at a given altitude."""
    # Convert RAAN change and inclination to radians
    raan_change_rad = np.radians(raan_change_deg)
    inclination_rad = np.radians(inclination_deg)

    # Compute orbital velocity at given altitude
    orbital_radius = earth_radius_km + altitude_km
    velocity = np.sqrt(mu / orbital_radius)  # km/s

    # Compute delta-v for RAAN change
    delta_v = 2 * velocity * np.sin(raan_change_rad / 2) * np.cos(inclination_rad)

    return delta_v

def total_maneuver_delta_v(initial_alt, final_alt, inclination_change, raan_change, is_at_apogee=True, initial_inclination=0, final_inclination=0):
    """Calculates total delta-v for a Hohmann transfer + optimal inclination and RAAN change at perigee or apogee."""
    # Convert to orbital radii (including Earth's radius)
    r1 = earth_radius_km + initial_alt
    r2 = earth_radius_km + final_alt

    # Compute Hohmann transfer delta-v
    delta_v1, delta_v2, a_transfer = hohmann_transfer_delta_v(r1, r2)

    # Compute inclination change delta-v at the optimal point (apogee/perigee)
    inclination_delta_v = inclination_change_delta_v(final_alt, inclination_change, is_at_apogee=is_at_apogee)

    # Compute RAAN change delta-v
    raan_delta_v = raan_change_delta_v(final_alt, raan_change, final_inclination)

    # Calculate the time taken for the Hohmann transfer
    transfer_time = calculate_transfer_time(r1, r2)  # Time in seconds
    transfer_time_hours = transfer_time / 3600  # Convert to hours

    # Total delta-v
    total_delta_v = delta_v1 + delta_v2 + inclination_delta_v + raan_delta_v

    return delta_v1, delta_v2, inclination_delta_v, raan_delta_v, total_delta_v, transfer_time_hours


def greedy_delta_v(tle_data, initial_sat):

    removal_sat = initial_sat # Satellite to remove debris
    collected = [] # List of debris objects that have been collected
    best_debris = None # Best debris object to collect
    best_delta_v = float('inf') # Best delta-v to collect debris
    total_delta_v = 0 # Total delta-v required to collect all debris
    total_transfer_time = 0 # Total transfer time for all maneuvers

    collected.append(removal_sat) # Add removal satellite to collected list
    
    for debris in tle_data:
        # Extract TLE data
        sat_iclination = float(removal_sat.get("INCLINATION"))
        sat_raan = float(removal_sat.get("RA_OF_ASC_NODE"))
        sat_semimajor_axis = float(removal_sat.get("SEMIMAJOR_AXIS"))

        # Check if debris has already been collected
        if debris in collected:
            continue

        # Calculate maneuver parameters
        initial_altitude = sat_semimajor_axis - 6378  # km (starting orbit)
        final_altitude = float(debris.get("SEMIMAJOR_AXIS")) - 6378  # km (target orbit)
        inclination_change = abs(sat_iclination - float(debris.get("INCLINATION")))  # degrees
        raan_change =  abs(sat_raan - float(debris.get("RA_OF_ASC_NODE")))  # degrees
        at_apogee = True  # Change inclination at apogee (set to False for perigee)
        initial_inclination = sat_iclination # degrees (initial orbit inclination)
        final_inclination = float(debris.get("INCLINATION"))  # degrees (target orbit inclination)

        # Calculate delta-v for maneuver
        dv1, dv2, dv_inc, dv_raan, total_dv, transfer_time  = total_maneuver_delta_v(initial_altitude, final_altitude, inclination_change, raan_change, at_apogee, initial_inclination, final_inclination)

        # Check if this debris is the best to collect
        if total_dv < best_delta_v:
            best_delta_v = total_dv
            best_debris = debris
        
        # Update total delta-v and collected list
        total_delta_v += best_delta_v
        collected.append(best_debris)
        removal_sat = best_debris
        total_transfer_time += transfer_time

        # Reset best debris and delta-v
        best_debris = None
        best_delta_v = float('inf')
    
    return total_delta_v, collected, total_transfer_time

def hohmanns_last(last_sat_orbit):
    # Extract TLE data
    tle_name = last_sat_orbit.get("OBJECT_NAME", "")
    tle_line1 = last_sat_orbit.get("TLE_LINE1", "")
    tle_line2 = last_sat_orbit.get("TLE_LINE2", "")

    #print(f"tle_name: {tle_name}")

    # Extract semi-major axis
    earth_radius = 6378  # km
    mu = 398600  # Earth's gravitational parameter (km^3/s^2)
    
    r1 = float(last_sat_orbit.get("SEMIMAJOR_AXIS"))
    #print(f"r1: {r1:.2f} km/s")
    r2 = float(earth_radius)
    #print(f"r1: {r1:.2f} km/s")
    #print(f"r2: {r2:.2f} km/s")

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

    # Transfer time
    transfer_time = (1/2 * (2 * np.pi * np.sqrt(a_transfer**3 / mu)))/ 3600

    #print(f"Total Delta V: {total_delta_v:.2f} km/s")

    return total_delta_v, transfer_time

def print_collected(collected):
    print("Collected debris:")
    for debris in collected:
        print(f" - {debris.get('OBJECT_NAME')}")


if __name__ == "__main__":
    
    if len(sys.argv) != 2:
        print("Usage: python hohmanns_and_greedy_oneplane.py input_file")
        sys.exit(1)

    input_file = sys.argv[1]

    print(f"Reading from file {input_file}")
    json_data = read_json_file(input_file)

    for sat in json_data:
        debris = filter_debris_satellites(json_data)


    # ---------------------------------------------------------------------------------
    # Example usage:
    # change the index of debris to test different satellites
    removal_sat = debris[1]
    isp = 300  # Specific impulse (s)
    m0 = 1000  # Initial mass (kg)
    # ---------------------------------------------------------------------------------


    # Extract TLE data
    sat_iclination = float(removal_sat.get("INCLINATION"))
    sat_raan = float(removal_sat.get("RA_OF_ASC_NODE"))
    sat_semimajor_axis = float(removal_sat.get("SEMIMAJOR_AXIS"))

    count = 0
    tle_data = []

    for sat in debris:
        if float(sat.get("INCLINATION")) < (sat_iclination + 10) and float(sat.get("INCLINATION")) > (sat_iclination - 10) and float(sat.get("RA_OF_ASC_NODE")) < (sat_raan + 100) and float(sat.get("RA_OF_ASC_NODE")) > (sat_raan - 100):
            if float(sat.get("SEMIMAJOR_AXIS")) < (sat_semimajor_axis + 50) and float(sat.get("SEMIMAJOR_AXIS")) > (sat_semimajor_axis - 50):
                count += 1
                tle_data.append(sat)

    print(f"count: {count}")

    total_delta_v1, total_time_1 = hohmanns_first(removal_sat) 

    total_delta_v2, collected, total_time_2 = greedy_delta_v(tle_data, removal_sat)

    total_delta_v3, total_time_3 = hohmanns_last(collected[-1]) 

    total_delta_v = total_delta_v1 + total_delta_v2 + total_delta_v3

    total_time = total_time_1 + total_time_2 + total_time_3

    print(f"Total Delta V (Hohmanns First): {total_delta_v1:.2f} km/s")
    print(f"Total Delta V (Greedy): {total_delta_v2:.2f} km/s")
    print(f"Total Delta V (Hohmanns Last): {total_delta_v3:.2f} km/s")
    print(f"Total Delta V: {total_delta_v:.2f} km/s")

    print(f"Total Time (Hohmanns First): {total_time_1:.2f} hours")
    print(f"Total Time (Greedy): {total_time_2:.2f} hours")
    print(f"Total Time (Hohmanns Last): {total_time_3:.2f} hours")
    print(f"Total Time: {total_time:.2f} hours")

    # Fuel mass calculation
    delta_v = total_delta_v  # Delta-v (km/s)
    g0 = 9.81  # Earth's gravity (m/s²)
    ve = isp * g0  # Effective exhaust velocity (m/s)
    m1 = m0 / (1 - np.exp(-delta_v / ve))  # Final mass (kg)

    print(f"Mass fuel required: {m1} kg")

    print("")
    print_collected(collected)



                

