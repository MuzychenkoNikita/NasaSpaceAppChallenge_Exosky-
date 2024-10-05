import astropy.units as u
from astropy.coordinates import SkyCoord
from astroquery.gaia import Gaia
from pprint import pprint

def Get_Stars(amount = 1000):
    query = f"""
    SELECT TOP {amount}
        source_id, ra, dec,
        phot_g_mean_mag as g_mag
    FROM gaiadr3.gaia_source
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
            'g_mag': row[3]
            })

    for i in output:
        yield i
    raise Exception("Out of stars :P")

if __name__=="__main__":
    output = Get_Stars()
    for i in range(1000):
        print(next(output))
