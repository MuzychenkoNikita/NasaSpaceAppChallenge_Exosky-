from astroquery.ipac.nexsci.nasa_exoplanet_archive import NasaExoplanetArchive
import math
import numpy as np

def Get_Exoplanets(amount = 1000):
    r = NasaExoplanetArchive.query_criteria(
        table="pscomppars", select=f"TOP {amount} pl_name, rastr, decstr, sy_dist", order="sy_dist ASC", where="sy_dist IS NOT NaN")

    for row in r:
        distance = np.float32(row[3]*3.26156)

        ra_parts = row[1].replace('h', ' ').replace('m', ' ').replace('s', '').split()
        ra_decimal = 15 * (int(ra_parts[0]) + int(ra_parts[1])/60 + float(ra_parts[2])/3600)
        azimuth = math.radians(ra_decimal)

        dec_parts = row[2].replace('d', ' ').replace('m', ' ').replace('s', '').split()
        dec_decimal = (int(dec_parts[0]) + int(dec_parts[1])/60 + float(dec_parts[2])/3600)
        elevation = math.radians(dec_decimal)

        yield {
            'planet_id': row[0],
            'x': np.float64(distance*math.cos(elevation)*math.cos(azimuth)),
            'y': np.float64(distance*math.cos(elevation)*math.sin(azimuth)),
            'z': np.float64(distance*math.sin(elevation)),
            'dist': distance,
            }
        
    raise StopIteration("Out of planets :P")

if __name__=="__main__":
    output = Get_Exoplanets()
    for i in range(1000):
        print(next(output))
