from astroquery.gaia import Gaia
import pandas as pd

# Define the ADQL query to fetch stars with brightness less than 6.5 (phot_g_mean_mag < 6.5)
query = """
SELECT ra, dec, phot_g_mean_mag, phot_bp_mean_mag, phot_rp_mean_mag
FROM gaiadr3.gaia_source
WHERE phot_g_mean_mag < 6.5
"""

# Execute the query
job = Gaia.launch_job(query)
results = job.get_results()

# Convert the results to a pandas DataFrame
df = results.to_pandas()

# Print the relevant columns for stars with brightness less than 6.5
print("Stars with brightness less than 6.5 (G-band):")
print(df[['ra', 'dec', 'phot_g_mean_mag', 'phot_bp_mean_mag', 'phot_rp_mean_mag']])

# Optionally, save the data to a CSV file
df.to_csv('bright_stars.csv', index=False)
