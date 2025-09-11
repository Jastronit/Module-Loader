from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QComboBox, QHBoxLayout
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtCore import QUrl, Qt

def create_widget(BaseClass, module_name):
    class RadioWidget(BaseClass):
        def __init__(self):
            super().__init__(module_name)
            layout = QVBoxLayout(self)
            self.setLayout(layout)

            self.label = QLabel("Internet Radio")
            self.label.setAlignment(Qt.AlignCenter)
            layout.addWidget(self.label)

            self.stations = {
                "Rádio Slovensko": "http://icecast.stv.livebox.sk/slovensko_128.mp3",
                "Rádio_FM": "http://icecast.stv.livebox.sk/fm_128.mp3",
                "BBC World Service": "http://stream.live.vc.bbcmedia.co.uk/bbc_world_service"
            }

            self.combo = QComboBox()
            self.combo.addItems(self.stations.keys())
            layout.addWidget(self.combo)

            hbox = QHBoxLayout()
            self.btn_play = QPushButton("Play")
            self.btn_stop = QPushButton("Stop")
            hbox.addWidget(self.btn_play)
            hbox.addWidget(self.btn_stop)
            layout.addLayout(hbox)

            # player
            self.audio_output = QAudioOutput()
            self.player = QMediaPlayer()
            self.player.setAudioOutput(self.audio_output)

            self.btn_play.clicked.connect(self.play_selected)
            self.btn_stop.clicked.connect(self.stop)

        def play_selected(self):
            name = self.combo.currentText()
            url = self.stations.get(name)
            if url:
                self.player.setSource(QUrl(url))
                self.player.play()
                self.label.setText(f"Playing: {name}")

        def stop(self):
            self.player.stop()
            self.label.setText("Stopped")

    return RadioWidget()

