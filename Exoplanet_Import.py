from astroquery.ipac.nexsci.nasa_exoplanet_archive import NasaExoplanetArchive
import math
import numpy as np

class ExoplanetData:
    def __init__(self, amount=1000):
        self.amount = amount
        self.exoplanets = list(self._get_exoplanets())

    def _get_exoplanets(self):
        r = NasaExoplanetArchive.query_criteria(
            table="pscomppars", select=f"TOP {self.amount} pl_name, rastr, decstr, sy_dist",
            order="sy_dist ASC", where="sy_dist IS NOT NaN")

        for row in r:
            distance = np.float32(row[3] * 3.26156)

            ra_parts = row[1].replace('h', ' ').replace('m', ' ').replace('s', '').split()
            ra_decimal = 15 * (int(ra_parts[0]) + int(ra_parts[1]) / 60 + float(ra_parts[2]) / 3600)
            azimuth = math.radians(ra_decimal)

            dec_parts = row[2].replace('d', ' ').replace('m', ' ').replace('s', '').split()
            dec_decimal = (int(dec_parts[0]) + int(dec_parts[1]) / 60 + float(dec_parts[2]) / 3600)
            elevation = math.radians(dec_decimal)

            yield {
                'planet_id': row[0],
                'x': np.float64(distance * math.cos(elevation) * math.cos(azimuth)),
                'y': np.float64(distance * math.cos(elevation) * math.sin(azimuth)),
                'z': np.float64(distance * math.sin(elevation)),
            }

    def get_all_names(self):
        """Returns a list of all exoplanet names."""
        return [planet['planet_id'] for planet in self.exoplanets]

    def get_coordinates_by_name(self, name):
        """Returns the XYZ coordinates of an exoplanet given its name."""
        for planet in self.exoplanets:
            if planet['planet_id'].lower() == name.lower():
                return {
                    'x': planet['x'],
                    'y': planet['y'],
                    'z': planet['z']
                }
        return None

if __name__ == "__main__":
    exoplanet_data = ExoplanetData()
    
    # Get and print all exoplanet names
    all_names = exoplanet_data.get_all_names()
    print("All Exoplanet Names:")
    print(all_names)

    # Get and print XYZ coordinates by name
    name = "Kepler-22 b"
    coordinates = exoplanet_data.get_coordinates_by_name(name)
    if coordinates:
        print(f"\nCoordinates of {name}:")
        print(coordinates)
    else:
        print(f"\n{name} not found.")