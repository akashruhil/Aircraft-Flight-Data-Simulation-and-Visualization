import pandas as pd
import folium
from my_module import ADRDataGenerator


def create_map(data, file_name):
    start_lat, start_lon = data["Latitude"].iloc[0], data["Longitude"].iloc[0]
    m = folium.Map(location=[start_lat, start_lon], zoom_start=18)

    # Add route as a polyline
    route = list(zip(data["Latitude"], data["Longitude"]))
    folium.PolyLine(route, color="blue", weight=2.5, opacity=0.8).add_to(m)

    # Add markers for selected data points
    for _, row in data.iterrows():
        popup_content = f"""
        <b>Date:</b> {row['Date']}<br>
        <b>Time:</b> {row['Time']}<br>
        <b>Speed:</b> {row['Speed (km/h)']} km/h<br>
        <b>Altitude:</b> {row['Altitude (ft)']} ft<br>
        <b>Roll Angle:</b> {row['Roll Angle (deg)']}°<br>
        <b>Pitch Angle:</b> {row['Pitch Angle (deg)']}°<br>
        <b>Engine1 RPM:</b> {row['Engine1 RPM']}<br>
        <b>Engine1 Temp:</b> {row['Engine1 Temp (°C)']}°C<br>
        <b>Engine2 RPM:</b> {row['Engine2 RPM']}<br>
        <b>Engine2 Temp:</b> {row['Engine2 Temp (°C)']}°C<br>
        <b>Oil Warning:</b> {"Yes" if row['Oil Warning'] else "No"}<br>
        <b>Hydraulic Warning:</b> {"Yes" if row['Hydraulic Warning'] else "No"}<br>
        <b>Pressure Warning:</b> {"Yes" if row['Pressure Warning'] else "No"}<br>
        <b>Low Fuel Warning:</b> {"Yes" if row['Low Fuel Warning'] else "No"}<br>
        <b>Undercarriage:</b> {row['Undercarriage Position']}
        """
        folium.Marker(
            location=[row["Latitude"], row["Longitude"]],
            popup=popup_content,
            icon=folium.Icon(color="red", icon="plane", prefix="fa"),
        ).add_to(m)

    # Save the map to an HTML file
    m.save(file_name)
    print(f"Map saved as '{file_name}'")


def main():
    # Generate ADR data
    print("Generating ADR data...")
    generator = ADRDataGenerator(
        start_lat=26.108053,
        start_lon=91.585943,
        total_distance=100,  # in kilometers
        average_speed=300 / 3600,  # km/s
        sampling_rate=2,  # seconds
    )
    generator.save_to_csv("adr_data.csv")

    # Load the generated data
    df = pd.read_csv("adr_data.csv")

    # Create and save the initial map
    output_file = "aircraft_sortie_map.html"
    create_map(df, output_file)
    print(f"Map created and saved to {output_file}")

    # Filter application loop
    current_data = df
    while True:
        response = input("Do you want to apply filters to the data? (yes/no): ").strip().lower()
        if response == "no":
            print("Exiting. No further filters applied.")
            break

        try:
            num_filters = int(input("How many filters do you want to apply? "))
            if num_filters <= 0:
                print("Number of filters must be at least 1.")
                continue
        except ValueError:
            print("Please enter a valid number.")
            continue

        filters = []

        for _ in range(num_filters):
            print("Select a parameter to filter:")
            parameters = [
                "Speed (km/h)",
                "Altitude (ft)",
                "Roll Angle (deg)",
                "Pitch Angle (deg)",
                "Engine1 RPM",
                "Engine1 Temp (°C)",
                "Engine2 RPM",
                "Engine2 Temp (°C)",
            ]
            for i, param in enumerate(parameters, 1):
                print(f"{i}. {param}")
            try:
                choice = int(input("Enter the number of the parameter: "))
                parameter = parameters[choice - 1]
            except (ValueError, IndexError):
                print("Invalid choice. Please select a valid parameter.")
                continue

            while True:
                try:
                    threshold = float(input(f"Enter the threshold for {parameter}: "))
                    filters.append((parameter, threshold))
                    break
                except ValueError:
                    print("Please enter a valid number.")

        # Apply all filters
        filtered_data = current_data
        for parameter, threshold in filters:
            filtered_data = filtered_data[filtered_data[parameter] > threshold]
            if filtered_data.empty:
                print("No data points satisfy the filters. Please try again with different values.")
                break
        else:
            # If all filters are applied successfully
            current_data = filtered_data
            output_file = "filtered_aircraft_sortie_map.html"
            create_map(current_data, output_file)
            print(f"Filtered map created and saved to {output_file}")


if __name__ == "__main__":
    main()
