import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from geopy.distance import geodesic
import random
from scipy.interpolate import splprep, splev


class ADRDataGenerator:
    def __init__(self, start_lat, start_lon, total_distance, average_speed, sampling_rate=2):
        self.start_lat = start_lat
        self.start_lon = start_lon
        self.total_distance = total_distance
        self.average_speed = average_speed  # km/s
        self.sampling_rate = sampling_rate
        # self.total_time = int(self.total_distance / self.average_speed)
        self.total_time = int(500)
        self.timestamps = self.generate_timestamps()
        self.route_points = self.generate_smooth_route()
    
    def generate_timestamps(self):
        """Generate timestamps for the simulation."""
        return [datetime.now() + timedelta(seconds=i) for i in range(self.total_time)]

    def generate_smooth_route(self, num_curves=7):
        """Generate a smooth route with random curves."""
        points = [(self.start_lat, self.start_lon)]
        for m in range(num_curves):
            random_point = (
                self.start_lat + random.uniform(-0.5, 0.5),
                self.start_lon + random.uniform(-0.5, 0.5),
            )
            points.append(random_point)
        points.append((self.start_lat, self.start_lon))  # Return to the starting point
        
        # Interpolate points for a smooth curve
        latitudes, longitudes = zip(*points)
        tck, u = splprep([latitudes, longitudes], s=1)
        smooth_points = splev(np.linspace(0, 1, self.total_time), tck)
        route = list(zip(smooth_points[0], smooth_points[1]))
        
        # Scale route to meet the total distance requirement
        current_distance = sum(
            geodesic(route[i], route[i + 1]).kilometers for i in range(len(route) - 1)
        )
        scale_factor = self.total_distance / current_distance
        scaled_route = [
            (
                self.start_lat + (lat - self.start_lat) * scale_factor,
                self.start_lon + (lon - self.start_lon) * scale_factor,
            )
            for lat, lon in route
        ]
        return scaled_route

    def generate_random_parameters(self):
        """Generate random flight parameters."""
        return {
            "Speed (km/h)": np.random.uniform(100, 400, self.total_time),
            "Altitude (ft)": np.random.uniform(200, 20000, self.total_time),
            "Roll Angle (deg)": np.random.uniform(-45, 45, self.total_time),
            "Pitch Angle (deg)": np.random.uniform(-20, 20, self.total_time),
            "Roll Control Movement": np.random.uniform(-10, 10, self.total_time),
            "Pitch Control Movement": np.random.uniform(-10, 10, self.total_time),
            "Engine1 RPM": np.random.uniform(0, 100, self.total_time),
            "Engine1 Temp (°C)": np.random.uniform(200, 800, self.total_time),
            "Engine2 RPM": np.random.uniform(0, 100, self.total_time),
            "Engine2 Temp (°C)": np.random.uniform(200, 800, self.total_time),
            "Oil Warning": np.random.choice([0, 1], self.total_time, p=[0.99, 0.01]),
            "Hydraulic Warning": np.random.choice([0, 1], self.total_time, p=[0.99, 0.01]),
            "Pressure Warning": np.random.choice([0, 1], self.total_time, p=[0.99, 0.01]),
            "Low Fuel Warning": np.random.choice([0, 1], self.total_time, p=[0.98, 0.02]),
            "Undercarriage Position": np.random.choice(["UP", "DOWN"], self.total_time, p=[0.9, 0.1]),
        }

    def create_dataframe(self):
        """Create a DataFrame with flight data."""
        params = self.generate_random_parameters()
        data = {
            "Date": [t.strftime("%Y-%m-%d") for t in self.timestamps],
            "Time": [t.strftime("%H:%M:%S") for t in self.timestamps],
            "Latitude": [p[0] for p in self.route_points],
            "Longitude": [p[1] for p in self.route_points],
            **params,
        }
        return pd.DataFrame(data)

    def save_to_csv(self, filename="adr_data.csv"):
        """Save the generated data to a CSV file."""
        df = self.create_dataframe()
        df.to_csv(filename, index=False)
        print(f"ADR data generated and saved as '{filename}'")
