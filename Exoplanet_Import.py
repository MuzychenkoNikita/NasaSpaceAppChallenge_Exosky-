import astropy.units as u
from astropy.coordinates import SkyCoord
from astroquery.ipac.nexsci.nasa_exoplanet_archive import NasaExoplanetArchive
from pprint import pprint
import numpy as np

def Get_Exoplanets(amount = 1000):
    r = NasaExoplanetArchive.query_criteria(
        table="pscomppars", select=f"TOP {amount} pl_name, rastr, decstr, sy_dist", order="sy_dist ASC")

    output = []
    for row in r:
        output.append({
            'planet_id': row[0],
            'ra': np.float64(15 * int(row[1][:2]) + int(row[1][3:5])/4 + float(row[1][6:11])/240),
            'dec': np.float64(15 * int(row[2][:3]) + int(row[2][4:6])/4 + float(row[2][7:11])/240),
            'dist': np.float32(row[3] * 3.26156)
            })

    for i in output:
        yield i
    raise Exception("Out of planets :P")

if __name__=="__main__":
    output = Get_Exoplanets()
    for i in range(1000):
        print(next(output))
