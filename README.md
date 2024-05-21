
# Satellite Tracker

Satellite Tracker is a Python-based application that provides real-time tracking of satellites. The application fetches the latest Two-Line Element (TLE) data from the Space-Track API and uses the `sgp4` library to calculate and display the current position of the satellite on a map.

## Features

- **Real-time tracking:** Displays the current location of satellites on a world map.
- **TLE Data Fetching:** Fetches the latest TLE data from Space-Track.
- **Custom Satellite ID:** Allows users to enter a custom satellite ID for tracking.
- **Interactive Map:** Displays the satellite's trajectory and current position on an interactive map.

## Installation

### Prerequisites

- Python 3.6+
- Space-Track account for accessing TLE data
- Required Python packages: `requests`, `sgp4`, `PyQt5`, `matplotlib`, `cartopy`, `Pillow`

### Install Required Packages

Use the following commands to install the required Python packages:

```bash
pip install requests sgp4 PyQt5 matplotlib cartopy Pillow
```

## Setup

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/LazyMan145/SattelitTracker.git
   cd SattelitTracker
   ```

2. **Configure Space-Track Credentials:**

   Update the `main.py` file with your Space-Track username and password:

   ```python
   self.username = "YOUR_SPACETRACK_USERNAME"
   self.password = "YOUR_SPACETRACK_PASSWORD"
   ```

3. **Run the Application:**

   ```bash
   python main.py
   ```

## Usage

1. **Launch the Application:**
   
   Run the `main.py` script to start the application. The main window will open with two tabs: "Earth Map" and "Satellite Tracker".

2. **Enter Satellite ID:**

   Go to the "Satellite Tracker" tab, enter the Satellite ID you want to track, and click "Track". The application will fetch the latest TLE data and display the current position of the satellite on the map.

3. **View Satellite Trajectory:**

   The trajectory of selected satellites will be displayed on the map, and the current position will be marked with a satellite icon.

## Project Structure

- `main.py`: Main application script.
- `get_coords_from_spacetrack.py`: Script to fetch TLE data from Space-Track and compute satellite positions.
- `get_OnlyLatestTLE_from_spacetrack.py`: Script to fetch only the latest TLE data from Space-Track.
- `get_coords_from_inputTLE.py`: Script to compute coordinates from input TLE data.


## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [Space-Track](https://www.space-track.org/) for providing satellite TLE data.
- [N2YO](https://www.n2yo.com/) for additional satellite tracking information.
- [SGP4](https://pypi.org/project/sgp4/) for satellite position calculations.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## Contact

For any inquiries or issues, please contact [dimikmazu@gmail.com](mailto:dimikmazu@gmail.com).


# SattelitTracker
