import sys
import numpy as np
import librosa
import PyQt5.QtWidgets as QW
import pyqtgraph as pg


class WidgetPlot(QW.QWidget):
    def __init__(self):
        super().__init__()
        pg.setConfigOptions(imageAxisOrder='row-major')

        self.x = 0
        self.y = 0
        self.sr = 0

        self.w_signal = pg.GraphicsWindow()
        self.w_spec = pg.GraphicsWindow()

        self.p_signal = self.w_signal.addPlot()
        self.plot_signal = self.p_signal.plot(pen=('#0F8EBB50'))

        self.p_spec = self.w_spec.addPlot()
        self.hist = pg.HistogramLUTItem()

        self.init_ui()
        self.init_event()

    def init_ui(self):
        # signal
        self.w_signal.setFixedHeight(200)
        self.p_signal.setLabel('bottom', 'Time', 's')
        self.p_signal.setLabel('left', 'Intensity')
        self.p_signal.showGrid(x=True, y=True, alpha=0.7)
        self.p_signal.addItem(self.plot_signal)

        # spectrogram
        self.img = pg.ImageItem()
        self.p_spec.addItem(self.img)
        self.hist.setImageItem(self.img)
        # self.p_spec.addItem(self.hist)
        self.hist.gradient.restoreState(
            {'mode': 'rgb',
             'ticks': [(0.5, (0, 182, 188, 255)),
                       (1.0, (246, 111, 0, 255)),
                       (0.0, (75, 0, 113, 255))]})
        # self.w_spec.addItem(self.hist)

        self.p_spec.setLabel('bottom', "Time", units='s')
        self.p_spec.setLabel('left', "Frequency", units='Hz')

        # layout
        vbox0 = QW.QVBoxLayout()
        vbox0.addWidget(self.w_signal)
        vbox0.addWidget(self.w_spec)
        self.setLayout(vbox0)

    def init_event(self):
        pass

    def get_spectrogram(self, signal, sr):
        n_fft = 512
        hop_length = 256
        # f, t, spec = sp.signal.spectrogram(signal, sr, nfft=n_fft)
        # spec = spec/spec.mean()
        # spec = librosa.amplitude_to_db(spec)

        spec = np.abs(librosa.stft(signal, n_fft=n_fft, hop_length=hop_length))
        spec = librosa.amplitude_to_db(spec)
        t = len(signal) / sr
        f = int(sr)/2
        return f, t, spec

    def update_plot(self):
        x = self.x[::100]
        y = self.y[::100]
        self.plot_signal.setData(x, y)
        self.p_signal.setXRange(x[0], x[-1], padding=0)

    def update_spectrogram(self):
        f, t, spec = self.get_spectrogram(self.y, self.sr)

        self.img = pg.ImageItem()
        self.p_spec.addItem(self.img)
        self.hist.setImageItem(self.img)

        self.img.scale(t/spec.shape[1], f/spec.shape[0])
        self.img.setImage(spec)
        self.p_spec.setXRange(0, t, padding=0)
        self.p_spec.setYRange(0, f, padding=0)

    def set_signal(self, signal, sr):
        self.sr = sr
        signal = signal.astype('float16')
        self.y = signal
        self.x = np.arange(0, len(signal))/sr

        self.update_plot()
        self.update_spectrogram()


def main():
    app = QW.QApplication(sys.argv)

    # filename = librosa.util.example_audio_file()
    filename = '../data/sample/dir00/cartoon-birds-2_daniel-simion.mp3'
    data, sr = librosa.load(filename, sr=None)
    w = WidgetPlot()
    w.set_signal(data, sr)

    w.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
