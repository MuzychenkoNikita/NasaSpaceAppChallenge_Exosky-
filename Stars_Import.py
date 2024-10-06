from astroquery.gaia import Gaia
import numpy as np
import math

def Get_Stars(amount = 1000):
    query = f"""
    SELECT TOP {amount}
        gaiadr3.gaia_source.source_id, 
        gaiadr3.gaia_source.ra, 
        gaiadr3.gaia_source.dec, 
        gaiadr3.gaia_source.phot_g_mean_mag, 
        gaiadr3.gaia_source.parallax, 
        gaiadr2.gaia_source.radius_val 
    FROM gaiadr3.gaia_source 
    LEFT JOIN gaiadr2.gaia_source ON gaiadr3.gaia_source.source_id = gaiadr2.gaia_source.source_id
    WHERE gaiadr3.gaia_source.parallax_error / gaiadr3.gaia_source.parallax < 0.2
    ORDER BY gaiadr3.gaia_source.phot_g_mean_mag ASC
    """

    job = Gaia.launch_job(query)
    r = job.get_results()

    output = []
    for row in r:
        distance = np.float32((1000/row[4])*3.26156)
        azimuth = row[1]*(math.pi/180)
        elevation = row[2]*(math.pi/180)

        output.append({
            'source_id': row[0],
            'x': np.float64(distance*math.cos(elevation)*math.cos(azimuth)),
            'y': np.float64(distance*math.cos(elevation)*math.sin(azimuth)),
            'z': np.float64(distance*math.sin(elevation)),
            'g_mag': row[3],
            'dist': distance,
            'rad': row[4] * 7.35355*(10**-8)
            })

    for i in output:
        yield i

if __name__=="__main__":
    output = Get_Stars()
    for i in range(1000):
        print(next(output))
