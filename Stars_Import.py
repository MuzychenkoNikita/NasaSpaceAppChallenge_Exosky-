import pandas as pd
import numpy as np
from astroquery.vizier import Vizier

def Get_Stars(amount=4000, magnitude_limit="<6.0"):
    # Set up the Vizier catalog to query the Hipparcos catalog for stars with Vmag
    vizier = Vizier(columns=["*", "RAhms", "DEdms", "Vmag", "Plx"], row_limit=-1)  # No limit
    hipparcos_catalog = "I/239/hip_main"

    # Query the Hipparcos catalog for stars with specified magnitude
    hipparcos_data = vizier.query_constraints(catalog=hipparcos_catalog, Vmag=magnitude_limit)

    # Convert the results to a pandas DataFrame
    df = hipparcos_data[0].to_pandas()

    # Function to convert RAhms and DEdms to radians and calculate Cartesian coordinates
    def convert_to_xyz_brightness(row):
        ra_h, ra_m, ra_s = map(float, row['RAhms'].split())
        ra_deg = 15 * (ra_h + ra_m / 60 + ra_s / 3600)
        ra_rad = np.deg2rad(ra_deg)

        de_d, de_m, de_s = map(float, row['DEdms'].split())
        dec_deg = de_d + de_m / 60 + de_s / 3600
        dec_rad = np.deg2rad(dec_deg)

        if pd.notna(row['Plx']) and row['Plx'] > 0:
            distance_pc = 1000 / row['Plx']
            distance_ly = distance_pc * 3.26
        else:
            return np.nan, np.nan, np.nan, np.nan  # Skip stars without valid parallax

        # Convert to Cartesian coordinates
        x = distance_ly * np.cos(dec_rad) * np.cos(ra_rad)
        y = distance_ly * np.cos(dec_rad) * np.sin(ra_rad)
        z = distance_ly * np.sin(dec_rad)

        return x, y, z, row['Vmag']  # Return coordinates and brightness

    # Apply the conversion to get XYZ coordinates and brightness
    df[['x', 'y', 'z', 'Vmag']] = df.apply(lambda row: convert_to_xyz_brightness(row), axis=1, result_type='expand')

    # Filter out stars that have adjusted brightness greater than 6.0 (invisible stars)
    visible_stars = df[df['Vmag'] < 6.0].dropna(subset=['x', 'y', 'z'])

    # Limit the number of stars returned based on the specified amount
    return visible_stars[['x', 'y', 'z', 'Vmag']].head(amount).to_dict(orient='records')
