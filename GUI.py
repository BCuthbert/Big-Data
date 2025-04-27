# Run:
# python3 GUI.py & python3 data_faker.py
# To create fake data for this to update with
# Also the query is going to have to be run for a few seconds before the graph looks correct

import sys
import os
import pandas as pd
import matplotlib
matplotlib.use("QtAgg")
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt6.QtCore import (QTimer, QTime, QDateTime)
from PyQt6.QtWidgets import (
    QApplication, 
    QWidget, 
    QVBoxLayout, 
    QTableWidget, 
    QTableWidgetItem, 
    QLabel, 
    QGroupBox, 
    QHBoxLayout, 
    QCheckBox,
    QPushButton, 
    QDateTimeEdit,
    QPlainTextEdit,
    QTabWidget,
    QSizePolicy
)

CSV_PATH = "data.csv"  
REFRESH_INTERVAL = 5000  # In miliseconds
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
GROUPBOX_STYLE = """
                    QGroupBox {
                        font-weight: bold;
                        font-size: 16px;
                        border: 1px solid gray;
                        border-radius: 5px;
                        margin-top: 10px;
                    }

                    QGroupBox::title {
                        subcontrol-origin: margin;
                        subcontrol-position: top center;
                        padding: 0 5px;
                    }
                 """ # Make a theme.py?

class TimestreamViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Real-Time Timestream Viewer")
        self.setGeometry(100, 100, WINDOW_WIDTH, WINDOW_HEIGHT)

        self.runContinuous = False
        self.elapsedTime = QTime(0,0)

    # Layout setup
        GUILayout = QHBoxLayout()
        column1 = QVBoxLayout()
        column2 = QVBoxLayout()
        column3 = QVBoxLayout()

    # Column 1 (Query Box)
        # 1. Add Query Info Module FIRST (at the top)
        self.queryInfoGroup, self.elapsedTimeLabel, self.queryStatusLabel = makeQueryInfoModule(self.runQuery, self.stopQuery, self.runContinuous)
        self.queryInfoGroup.setStyleSheet(GROUPBOX_STYLE)
        column1.addWidget(self.queryInfoGroup)

        # Log Output Area
        self.logBoxGroup = QGroupBox("Logs")
        self.logBoxGroup.setStyleSheet(GROUPBOX_STYLE)
        logLayout = QVBoxLayout()
        # Actual Logs TextBox
        self.logBox = QPlainTextEdit()
        self.logBox.setReadOnly(True)
        self.logBox.setPlaceholderText("Log Output...")
        logLayout.addWidget(self.logBox)
        # Adding to Column
        self.logBoxGroup.setLayout(logLayout)
        column1.addWidget(self.logBoxGroup)

    # Column 2 (Data Visualization Widget)
        self.graphGroup = QGroupBox("Data Graphs")
        self.graphGroup.setStyleSheet(GROUPBOX_STYLE)
        graphLayout = QVBoxLayout()

        # Graph Box
        self.graphCanvas = MplCanvas(self, width=5, height=4, dpi=100)
        graphLayout.addWidget(self.graphCanvas)

        # Graph Option Tabs
        self.graphTabs = QTabWidget()
        self.graphTabs.setStyleSheet("QTabWidget::pane { border: 0; }")
        # Types of tabs
        self.lineGraphTab = QWidget()
        self.boxPlotTab = QWidget()
        # Appending tabs
        self.graphTabs.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        self.graphTabs.addTab(self.lineGraphTab, "Line Graph")
        self.graphTabs.addTab(self.boxPlotTab, "Box Plot")
        graphLayout.addWidget(self.graphTabs)

        self.graphGroup.setLayout(graphLayout)
        column2.addWidget(self.graphGroup)

    # Column 3 (Data Table)
        self.timeStreamGroup = QGroupBox("Timestream Data Results")
        self.timeStreamGroup.setStyleSheet(GROUPBOX_STYLE)
        timeStreamLayout = QVBoxLayout()

        # Adding data to table
        self.table = QTableWidget()
        timeStreamLayout.addWidget(self.table)
        self.timeStreamGroup.setLayout(timeStreamLayout)
        column3.addWidget(self.timeStreamGroup)
        self.updateTable()

        self.secondsPassed = QTimer(self)
        self.secondsPassed.timeout.connect(self.updateElapsedTime)

        self.dataTimer = QTimer(self)
        self.dataTimer.timeout.connect(self.updateTable)



    # Final Layout
        GUILayout.addLayout(column1)
        GUILayout.addLayout(column2)
        GUILayout.addLayout(column3)

        self.setLayout(GUILayout)


    # Methods
    def updateTable(self):
        if os.path.exists(CSV_PATH):
            try:
                self.df = pd.read_csv(CSV_PATH)

                self.table.setRowCount(len(self.df))
                self.table.setColumnCount(len(self.df.columns))
                self.table.setHorizontalHeaderLabels(self.df.columns.tolist())

                for row_idx, row in self.df.iterrows():
                    for col_idx, value in enumerate(row):
                        item = QTableWidgetItem(str(value))
                        self.table.setItem(row_idx, col_idx, item)
                self.graphCanvas.updateGraph(self.df)
                self.log(f"Table updated with {len(self.df)} rows.")

            except Exception as e:
                self.log(f"Error loading CSV: {e}")
        else:
            self.log("CSV file not found.")

    def runQuery(self):
        # Notify user
        self.log("Running Query...")
        self.queryStatusLabel.setText("Query Status: Running")

        # Start the timer when the query is run
        self.elapsedTime = QTime(0,0)
        self.elapsedTimeLabel.setText(self.elapsedTime.toString("hh:mm:ss"))
        self.secondsPassed.start(1000)
        self.dataTimer.start(REFRESH_INTERVAL)

        # Data processing logic here for when query is run
        self.log("Query is running")

    def stopQuery(self):
        # Notify user
        self.log("Stopping Query...")
        self.queryStatusLabel.setText("Query Status: Stopped")

        # Stop the timer
        self.secondsPassed.stop()
        self.dataTimer.stop()

        self.log("Query is stopped")

    def updateElapsedTime(self):
        # Update the elapsed time (increment by 1 second)
        self.elapsedTime = self.elapsedTime.addSecs(1)
        self.elapsedTimeLabel.setText(self.elapsedTime.toString("hh:mm:ss"))

    def log(self, message):
        self.logBox.appendPlainText(message)
        self.logBox.verticalScrollBar().setValue(self.logBox.verticalScrollBar().maximum())



def makeQueryInfoModule(runQuery, stopQuery, runContinuous):
    box = QGroupBox("Query Information")
    layout = QVBoxLayout()

    # Top status info
    queryStatusLabel = QLabel("Query Status: Stopped")
    layout.addWidget(queryStatusLabel)

    # Elapsed time to update later
    elapsedTimeLabel = QLabel("00:00:00")
    elapsedTimeBox = QHBoxLayout()
    elapsedTimeBox.addWidget(QLabel("Time Elapsed:"))
    elapsedTimeBox.addWidget(elapsedTimeLabel)
    layout.addLayout(elapsedTimeBox)

    # Other status info
    layout.addWidget(QLabel("Variance Detected: N/A"))
    layout.addWidget(QLabel("Data Pruned: 0 rows"))
    layout.addWidget(QLabel("Data Confidence: High"))

    # Continuous query checkbox
    continuousQuery = QCheckBox("Run Continuously")
    continuousQuery.setChecked(True)
    layout.addWidget(continuousQuery)

    # Custom timeframe input
    timeframeLayout = QHBoxLayout()
    startTime = QDateTimeEdit()
    endTime = QDateTimeEdit()
    runQueryButton = QPushButton("Run Query")
    stopQueryButton = QPushButton("Stop Query")

    now = QDateTime.currentDateTime()

    startTime.setDateTime(now)
    endTime.setDateTime(now.addSecs(3600)) # 1 hour

    if (runContinuous):
        timeframeLayout.addWidget(QLabel("From:"))
        timeframeLayout.addWidget(startTime)
        timeframeLayout.addWidget(QLabel("To:"))
        timeframeLayout.addWidget(endTime)

    timeframeLayout.addWidget(runQueryButton)
    timeframeLayout.addWidget(stopQueryButton)

    layout.addLayout(timeframeLayout)

    runQueryButton.clicked.connect(runQuery)
    stopQueryButton.clicked.connect(stopQuery)

    box.setLayout(layout)
    return box, elapsedTimeLabel, queryStatusLabel

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super().__init__(fig)

    def updateGraph(self, df, graphType="line"):
        if df.empty:
            return

        self.axes.clear()
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        x = df["timestamp"]
        y = df["sensor_value"]

        try:
            if graphType == 'line':
                self.axes.plot(x, y, marker="o", linestyle="-", color="blue")

                self.axes.set_title("Sensor Value Over Time")
                self.axes.set_xlabel("Timestamp")
                self.axes.set_ylabel("Sensor Value")
                self.figure.tight_layout()
                self.draw()

            elif graphType == "box":
                df["time_bucket"] = df["timestamp"].dt.strftime("%H:%M:%S")
                grouped = df.groupby("time_bucket")["sensor_value"].apply(list)

                self.axes.boxplot(grouped.tolist(), tick_labels=grouped.index, vert=True)
                self.axes.set_title("Sensor Value Distribution Over Time")
                self.axes.set_xlabel("Time")
                self.axes.set_ylabel("Sensor Value")
                self.axes.tick_params(axis='x', rotation=45)
        except Exception as e:
            print(f"Graph update failed: {e}")


# Run the app
if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = TimestreamViewer()
    viewer.show()
    sys.exit(app.exec())
