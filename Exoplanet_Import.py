import astropy.units as u
from astropy.coordinates import SkyCoord
from astroquery.ipac.nexsci.nasa_exoplanet_archive import NasaExoplanetArchive
import math
import numpy as np

def Get_Exoplanets(amount = 1000):
    r = NasaExoplanetArchive.query_criteria(
        table="pscomppars", select=f"TOP {amount} pl_name, rastr, decstr, sy_dist", order="sy_dist ASC")

    output = []
    for row in r:
        distance = np.float32((1000/row[3])*3.26156)
        azimuth = (15 * int(row[1][:2]) + int(row[1][3:5])/4 + float(row[1][6:11])/240)*(math.pi/180)
        elevation = (15 * int(row[2][:3]) + int(row[2][4:6])/4 + float(row[2][7:11])/240)*(math.pi/180)

        output.append({
            'planet_id': row[0],
            'x': np.float64(distance*math.cos(elevation)*math.cos(azimuth)),
            'y': np.float64(distance*math.cos(elevation)*math.sin(azimuth)),
            'z': np.float64(distance*math.sin(elevation)),
            'dist': np.float32(row[3] * 3.26156)
            })

    for i in output:
        yield i
    raise Exception("Out of planets :P")

if __name__=="__main__":
    output = Get_Exoplanets()
    for i in range(1000):
        print(next(output))
