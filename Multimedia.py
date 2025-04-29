import sys
import os
from PyQt6 import QtWidgets, QtCore, QtGui, QtMultimedia, QtMultimediaWidgets

# ---------------------------
# Custom Video Widget for Fullscreen Handling
# ---------------------------
class CustomVideoWidget(QtMultimediaWidgets.QVideoWidget):
    def keyPressEvent(self, event: QtGui.QKeyEvent):
        if event.key() == QtCore.Qt.Key.Key_Escape and self.isFullScreen():
            self.setFullScreen(False)
        else:
            super().keyPressEvent(event)



# ---------------------------
# Video Player Module
# ---------------------------
class VideoPlayerWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.mediaPlayer = QtMultimedia.QMediaPlayer(self)
        # Use our custom video widget for better fullscreen handling.
        self.videoWidget = CustomVideoWidget(self)
        self.init_ui()

    def init_ui(self):

        main_layout = QtWidgets.QHBoxLayout(self)
        
        
        layout_vid = QtWidgets.QVBoxLayout()
        layout_vid.addWidget(self.videoWidget)
        self.mediaPlayer.setVideoOutput(self.videoWidget)

        # Video control buttons
        control_layout = QtWidgets.QVBoxLayout()
        self.play_button = QtWidgets.QPushButton("Play")
        self.play_button.clicked.connect(self.play_video)
        control_layout.addWidget(self.play_button)

        self.pause_button = QtWidgets.QPushButton("Pause")
        self.pause_button.clicked.connect(self.pause_video)
        control_layout.addWidget(self.pause_button)

        self.fullscreen_button = QtWidgets.QPushButton("Full Screen")
        self.fullscreen_button.clicked.connect(self.toggle_fullscreen)
        control_layout.addWidget(self.fullscreen_button)

        # Video seeking slider
        self.position_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.position_slider.sliderMoved.connect(self.set_position)
        layout_vid.addWidget(self.position_slider)

        main_layout.addLayout(control_layout)
        main_layout.addLayout(layout_vid)

        # Connect media player signals
        self.mediaPlayer.positionChanged.connect(self.position_changed)
        self.mediaPlayer.durationChanged.connect(self.duration_changed)

    def play_video(self):
        self.mediaPlayer.play()

    def pause_video(self):
        self.mediaPlayer.pause()

    def toggle_fullscreen(self):
        if self.videoWidget.isFullScreen():
            self.videoWidget.setFullScreen(False)
        else:
            self.videoWidget.setFullScreen(True)

    def set_position(self, position):
        self.mediaPlayer.setPosition(position)

    def position_changed(self, position):
        self.position_slider.setValue(position)

    def duration_changed(self, duration):
        self.position_slider.setRange(0, duration)

    def load_video(self, video_path):
        if os.path.exists(video_path):
            url = QtCore.QUrl.fromLocalFile(video_path)
            self.mediaPlayer.setSource(url)
        else:
            QtWidgets.QMessageBox.warning(self, "Error", "Video file not found.")

