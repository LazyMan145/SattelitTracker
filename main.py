
import sys
import requests
from sgp4.api import Satrec
from sgp4.api import jday
from datetime import datetime
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QCheckBox, QHBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt5.QtCore import QTimer
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import cartopy.crs as ccrs
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from PIL import Image

class EarthMapWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout(self)
        self.figure, self.ax = plt.subplots(figsize=(10, 5), subplot_kw={'projection': ccrs.PlateCarree()})
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)
        self.plot_earth_map()

    def plot_earth_map(self):
        self.ax.stock_img()
        self.canvas.draw()

class SatelliteTrackerWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.update_satellite_position()

    def initUI(self):
        self.layout = QVBoxLayout(self)
        self.checkBoxLayout = QHBoxLayout()

        self.sat_files = [
            ('satellites/SAT-25544.dat', 'SAT-25544'),
            ('satellites/SAT-55978.dat', 'SAT-55978'),
            ('satellites/SAT-44387.dat', 'SAT-44387')
        ]

        self.checkBoxes = []
        for file_path, label in self.sat_files:
            checkBox = QCheckBox(label)
            checkBox.setChecked(True)
            checkBox.stateChanged.connect(self.update_satellite_position)
            self.checkBoxes.append((checkBox, file_path))
            self.checkBoxLayout.addWidget(checkBox)

        self.layout.addLayout(self.checkBoxLayout)

        self.figure, self.ax = plt.subplots(figsize=(10, 5), subplot_kw={'projection': ccrs.PlateCarree()})
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)

        self.setLayout(self.layout)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_satellite_position)
        self.timer.start(1000)  # Update every second

    def read_satellite_data(self, file_path):
        dates = []
        lats = []
        lons = []
        with open(file_path, 'r') as file:
            for line in file:
                parts = line.strip().split()
                if len(parts) != 4:
                    continue  # Skip lines that do not have exactly 4 parts
                try:
                    date = ' '.join(parts[0:2])
                    lat = float(parts[2])
                    lon = float(parts[3])
                    dates.append(datetime.strptime(date, '%Y-%m-%d %H:%M:%S'))
                    lats.append(lat)
                    lons.append(lon)
                except ValueError as e:
                    print(f"Skipping line due to error: {e}")
                    continue
        return np.array(lats), np.array(lons)

    def plot_satellite_trajectory(self, ax, lats, lons, label):
        ax.plot(lons, lats, transform=ccrs.Geodetic(), label=label)

    def update_satellite_position(self):
        self.ax.clear()
        self.ax.stock_img()
        for checkBox, file_path in self.checkBoxes:
            if checkBox.isChecked():
                lats, lons = self.read_satellite_data(file_path)
                self.plot_satellite_trajectory(self.ax, lats, lons, checkBox.text())
        self.ax.legend()
        self.canvas.draw()

class SatelliteLocationWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout(self)

        self.idInputLayout = QHBoxLayout()
        self.idInputLabel = QLabel("Enter Satellite ID:")
        self.idInput = QLineEdit()
        self.idInputButton = QPushButton("Track")
        self.idInputButton.clicked.connect(self.update_satellite_id)

        self.idInputLayout.addWidget(self.idInputLabel)
        self.idInputLayout.addWidget(self.idInput)
        self.idInputLayout.addWidget(self.idInputButton)
        self.layout.addLayout(self.idInputLayout)

        self.locationLabel = QLabel("Current Location: Loading...")
        self.layout.addWidget(self.locationLabel)

        self.figure, self.ax = plt.subplots(figsize=(10, 5), subplot_kw={'projection': ccrs.PlateCarree()})
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)

        self.setLayout(self.layout)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_location)
        self.timer.start(5000)  # Update every 5 seconds

        self.satellite_id = "25544"  # Default satellite ID (ISS)

        self.satellite_icon_path = "Satellite_icon-icons.com_74901.png"  # Replace with the path to your satellite icon image

        # Replace with your Space-Track credentials
        self.username = "YOUR_SPACETRACK_USERNAME"
        self.password = "YOUR_SPACETRACK_PASSWORD"

    def update_satellite_id(self):
        self.satellite_id = self.idInput.text()
        self.update_location()

    def get_tle(self, sat_id):
        login_url = "https://www.space-track.org/ajaxauth/login"
        data_url = f"https://www.space-track.org/basicspacedata/query/class/tle_latest/NORAD_CAT_ID/{sat_id}/orderby/TLE_LINE1%20ASC/limit/1/format/tle"
        creds = {
            "identity": self.username,
            "password": self.password
        }
        with requests.Session() as session:
            session.post(login_url, data=creds)
            response = session.get(data_url)
            if response.status_code == 200:
                tle_lines = response.text.strip().split('\n')
                return tle_lines
            else:
                return None

    def update_location(self):
        tle = self.get_tle(self.satellite_id)
        if tle and len(tle) == 2:
            satellite = Satrec.twoline2rv(tle[0], tle[1])
            now = datetime.utcnow()
            jd, fr = jday(now.year, now.month, now.day, now.hour, now.minute, now.second)
            e, r, v = satellite.sgp4(jd, fr)
            if e == 0:
                latitude = np.degrees(np.arcsin(r[2] / np.linalg.norm(r)))
                longitude = np.degrees(np.arctan2(r[1], r[0]))
                self.locationLabel.setText(f"Current Location: Latitude: {latitude}, Longitude: {longitude}")

                # Plot current position on the map
                self.ax.clear()
                self.ax.stock_img()
                self.ax.plot(longitude, latitude, 'ro', transform=ccrs.Geodetic(), label='Current Location')

                # Add satellite icon
                img = Image.open(self.satellite_icon_path)
                imscatter(longitude, latitude, img, zoom=0.05, ax=self.ax)  # Reduced zoom to make the icon smaller

                self.ax.legend()
                self.canvas.draw()
            else:
                self.locationLabel.setText("Error: Unable to compute satellite position")
        else:
            self.locationLabel.setText("Error: TLE data not available")

def imscatter(x, y, image, ax=None, zoom=1):
    if ax is None:
        ax = plt.gca()
    try:
        image = OffsetImage(image, zoom=zoom)
        x, y = np.atleast_1d(x, y)
        artists = []
        for x0, y0 in zip(x, y):
            ab = AnnotationBbox(image, (x0, y0), xycoords='data', frameon=False)
            ax.add_artist(ab)
            artists.append(ab)
        ax.update_datalim(np.column_stack([x, y]))
        ax.autoscale()
        return artists
    except Exception as e:
        print(f"Error in imscatter: {e}")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Satellite Tracker')
        self.setGeometry(100, 100, 1200, 600)
        self.initUI()

    def initUI(self):
        self.tabs = QTabWidget(self)
        self.setCentralWidget(self.tabs)

        self.earthMapTab = EarthMapWidget()
        self.satelliteTrackerTab = SatelliteTrackerWidget()
        self.satelliteLocationTab = SatelliteLocationWidget()

        self.tabs.addTab(self.earthMapTab, "Earth Map")
        self.tabs.addTab(self.satelliteTrackerTab, "Satellite Tracker")
        self.tabs.addTab(self.satelliteLocationTab, "Satellite Location")

def main():
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
