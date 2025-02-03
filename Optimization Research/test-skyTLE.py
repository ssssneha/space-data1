from skyfield.api import EarthSatellite
import datetime as dt
from pytz import timezone
from skyfield import almanac
from skyfield.api import N, W, wgs84, load

#"TLE_LINE1": "1 00051U 60009C   24002.20430891  .00000017  00000-0  99980-3 0  9992",
#"TLE_LINE2": "2 00051  47.2149 304.8147 0108718  48.3483 312.6554 12.18315025821811"

ts = load.timescale()
#line1 = '1 25544U 98067A   14020.93268519  .00009878  00000-0  18200-3 0  5082'
#line2 = '2 25544  51.6498 109.4756 0003572  55.9686 274.8005 15.49815350868473'
line1 = '1 00051U 60009C   24002.20430891  .00000017  00000-0  99980-3 0  9992'
line2 = '2 00051  47.2149 304.8147 0108718  48.3483 312.6554 12.18315025821811'
satellite = EarthSatellite(line1, line2, 'Medium Space Debris', ts)
print(satellite)