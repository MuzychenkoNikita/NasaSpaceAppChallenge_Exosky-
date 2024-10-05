import astropy.units as u
from astropy.coordinates import SkyCoord
from astroquery.gaia import Gaia
import numpy as np

def Get_Stars(amount = 1000):
    query = f"""
    SELECT TOP {amount}
        source_id, ra, dec, phot_g_mean_mag, parallax
    FROM gaiadr3.gaia_source
    WHERE parallax_error / parallax < 0.2
    ORDER BY phot_g_mean_mag ASC
    """

    job = Gaia.launch_job(query)
    r = job.get_results()

    output = []
    for row in r:
        output.append({
            'source_id': row[0],
            'ra': row[1],
            'dec': row[2],
            'g_mag': row[3],
            'dist': np.float32((1000/row[4])*3.26156)
            })

    for i in output:
        yield i
    raise Exception("Out of stars :P")

if __name__=="__main__":
    output = Get_Stars()
    for i in range(1000):
        print(next(output))
