import sys, os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QPushButton, QSlider, QComboBox,
    QFileDialog, QLineEdit, QProgressBar,
    QTabWidget, QFrame, QTextEdit
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap, QFont

from depth_engine import generate_depth_map
from stl_generator import depth_to_bas_relief, depth_to_lithophane, generate_label_plate_stl
from braille_engine import get_monument_info, text_to_braille_unicode
from qr_generator import generate_qr_code

OUTPUT_FOLDER = os.path.join(
    os.path.expanduser('~'), 'Documents', 'FeelTheMonument', 'output'
)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


class WorkerThread(QThread):
    progress = pyqtSignal(int)
    status   = pyqtSignal(str)
    done     = pyqtSignal(str, str)
    error    = pyqtSignal(str)

    def __init__(self, image_path, monument_name, params):
        super().__init__()
        self.image_path    = image_path
        self.monument_name = monument_name
        self.params        = params

    def run(self):
        try:
            self.status.emit('Running depth AI model...')
            self.progress.emit(10)
            depth = generate_depth_map(self.image_path)

            self.status.emit('Generating bas-relief STL...')
            self.progress.emit(40)
            name_safe = self.monument_name.replace(' ', '_')
            bas_path = os.path.join(OUTPUT_FOLDER, name_safe + '_bas_relief.stl')
            depth_to_bas_relief(
                depth, bas_path,
                base_mm=self.params['base'],
                relief_mm=self.params['relief'],
                width_mm=self.params['width'],
                smooth=self.params['smooth'])

            self.status.emit('Generating lithophane STL...')
            self.progress.emit(70)
            lit_path = os.path.join(OUTPUT_FOLDER, name_safe + '_lithophane.stl')
            depth_to_lithophane(depth, lit_path, width_mm=self.params['width'])

            if self.params.get('url'):
                self.status.emit('Generating label plate with Braille + QR...')
                self.progress.emit(88)
                plate_path = os.path.join(
                    OUTPUT_FOLDER, name_safe + '_label_plate.stl'
                )
                generate_label_plate_stl(
                    self.monument_name, self.params['url'], plate_path
                )

            self.progress.emit(100)
            self.done.emit(bas_path, lit_path)
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Feel the Monument')
        self.setMinimumSize(1000, 650)
        self.image_path   = None
        self.bas_stl_path = None
        self.lit_stl_path = None
        self._build_ui()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)

        # ---- SIDEBAR ----
        sidebar = QWidget()
        sidebar.setFixedWidth(280)
        sl = QVBoxLayout(sidebar)

        self.img_label = QLabel('No image uploaded')
        self.img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.img_label.setFixedHeight(160)
        self.img_label.setFrameStyle(QFrame.Shape.Box)
        upload_btn = QPushButton('Upload Monument Image')
        upload_btn.clicked.connect(self._upload)
        sl.addWidget(self.img_label)
        sl.addWidget(upload_btn)

        sl.addWidget(QLabel('Monument / Artwork name:'))
        self.monument_combo = QComboBox()
        self.monument_combo.addItems([
            'Taj Mahal', 'Qutub Minar', 'Red Fort',
            'Starry Night', 'Custom'
        ])
        sl.addWidget(self.monument_combo)

        self.custom_name_input = QLineEdit()
        self.custom_name_input.setPlaceholderText('Enter custom name here...')
        self.custom_name_input.setVisible(False)
        sl.addWidget(self.custom_name_input)
        self.monument_combo.currentTextChanged.connect(self._on_monument_changed)

        self.sliders = {}
        for (label, key, lo, hi, default) in [
            ('Plate width (mm)',    'width',  50, 200, 100),
            ('Relief height (mm)',  'relief',  2,  20,   8),
            ('Base thickness (mm)', 'base',    1,  10,   3),
            ('Smoothing',           'smooth',  0,  10,   3),
        ]:
            row = QHBoxLayout()
            lbl = QLabel(label)
            lbl.setFixedWidth(150)
            sl_w = QSlider(Qt.Orientation.Horizontal)
            sl_w.setRange(lo, hi)
            sl_w.setValue(default)
            val = QLabel(str(default))
            val.setFixedWidth(30)
            sl_w.valueChanged.connect(lambda v, lb=val: lb.setText(str(v)))
            row.addWidget(lbl)
            row.addWidget(sl_w)
            row.addWidget(val)
            self.sliders[key] = sl_w
            sl.addLayout(row)

        self.gen_btn = QPushButton('Generate STL')
        self.gen_btn.clicked.connect(self._generate)
        sl.addWidget(self.gen_btn)

        self.progress = QProgressBar()
        self.progress.setVisible(False)
        sl.addWidget(self.progress)

        self.status_lbl = QLabel('')
        self.status_lbl.setWordWrap(True)
        sl.addWidget(self.status_lbl)
        sl.addStretch()
        root.addWidget(sidebar)

        # ---- TABS ----
        tabs = QTabWidget()

        # Tab 1: Export
        export_tab = QWidget()
        et = QVBoxLayout(export_tab)
        self.bas_label   = QLabel('Bas-relief STL: not yet generated')
        self.lit_label   = QLabel('Lithophane STL: not yet generated')
        self.plate_label = QLabel('Label plate STL: not yet generated')
        export_bas_btn   = QPushButton('Save Bas-Relief STL (for blind users)')
        export_bas_btn.clicked.connect(self._export_bas)
        export_lit_btn   = QPushButton('Save Lithophane STL (backlit artwork)')
        export_lit_btn.clicked.connect(self._export_lit)
        export_plate_btn = QPushButton('Save Label Plate STL (Braille + QR)')
        export_plate_btn.clicked.connect(self._export_plate)
        et.addWidget(QLabel('Export Options:'))
        et.addWidget(self.bas_label)
        et.addWidget(export_bas_btn)
        et.addWidget(self.lit_label)
        et.addWidget(export_lit_btn)
        et.addWidget(self.plate_label)
        et.addWidget(export_plate_btn)
        et.addStretch()
        tabs.addTab(export_tab, 'Export STL')

        # Tab 2: Braille
        braille_tab = QWidget()
        bt = QVBoxLayout(braille_tab)
        bt.addWidget(QLabel('Braille preview (Unicode):'))
        self.braille_display = QTextEdit()
        self.braille_display.setReadOnly(True)
        self.braille_display.setFont(QFont('Segoe UI', 16))
        bt.addWidget(self.braille_display)
        tabs.addTab(braille_tab, 'Braille Label')

        # Tab 3: Audio QR
        qr_tab = QWidget()
        qt = QVBoxLayout(qr_tab)
        qt.addWidget(QLabel(
            'Paste a link to an audio description or video:'
        ))
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText(
            'e.g. https://drive.google.com/file/d/yourfileid/view'
        )
        gen_qr_btn = QPushButton('Generate QR Code Image')
        gen_qr_btn.clicked.connect(self._generate_qr)
        self.qr_preview = QLabel('QR code will appear here')
        self.qr_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.qr_preview.setFixedHeight(220)
        self.qr_status = QLabel(
            'Tip: If a URL is entered before clicking Generate STL, '
            'a physical label plate STL with Braille name and QR code '
            'will also be generated automatically.'
        )
        self.qr_status.setWordWrap(True)
        qt.addWidget(self.url_input)
        qt.addWidget(gen_qr_btn)
        qt.addWidget(self.qr_preview)
        qt.addWidget(self.qr_status)
        qt.addStretch()
        tabs.addTab(qr_tab, 'Audio QR Code')

        root.addWidget(tabs)

    def _on_monument_changed(self, text):
        self.custom_name_input.setVisible(text == 'Custom')

    def _upload(self):
        path, _ = QFileDialog.getOpenFileName(
            self, 'Select Image', '',
            'Images (*.jpg *.jpeg *.png *.webp *.bmp)'
        )
        if path:
            self.image_path = path
            pix = QPixmap(path).scaledToWidth(260)
            self.img_label.setPixmap(pix)

    def _get_monument_name(self):
        monument = self.monument_combo.currentText()
        if monument == 'Custom':
            custom = self.custom_name_input.text().strip()
            if not custom:
                return None
            return custom
        return monument

    def _generate(self):
        if not self.image_path:
            self.status_lbl.setText('Please upload an image first.')
            return

        monument = self._get_monument_name()
        if monument is None:
            self.status_lbl.setText('Please enter a custom name.')
            return

        info = get_monument_info(monument)
        braille = text_to_braille_unicode(info['short'])
        self.braille_display.setPlainText(
            f"Text: {info['short']}\n\nBraille: {braille}"
        )

        params = {
            'width':  self.sliders['width'].value(),
            'relief': self.sliders['relief'].value(),
            'base':   self.sliders['base'].value(),
            'smooth': self.sliders['smooth'].value() * 0.5,
            'url':    self.url_input.text().strip(),
        }

        self.progress.setVisible(True)
        self.gen_btn.setEnabled(False)
        self.plate_label.setText('Label plate STL: not yet generated')

        self.worker = WorkerThread(self.image_path, monument, params)
        self.worker.progress.connect(self.progress.setValue)
        self.worker.status.connect(self.status_lbl.setText)
        self.worker.done.connect(self._on_done)
        self.worker.error.connect(
            lambda e: self.status_lbl.setText('Error: ' + e)
        )
        self.worker.start()

    def _on_done(self, bas, lit):
        self.bas_stl_path = bas
        self.lit_stl_path = lit

        monument  = self._get_monument_name() or 'Custom'
        name_safe = monument.replace(' ', '_')
        plate_path = os.path.join(OUTPUT_FOLDER, name_safe + '_label_plate.stl')

        self.bas_label.setText(f'Bas-relief ready: {os.path.basename(bas)}')
        self.lit_label.setText(f'Lithophane ready: {os.path.basename(lit)}')

        if os.path.exists(plate_path):
            self.plate_stl_path = plate_path
            self.plate_label.setText(
                f'Label plate ready: {os.path.basename(plate_path)}'
            )
        else:
            self.plate_stl_path = None
            self.plate_label.setText(
                'Label plate STL: skipped (no URL entered)'
            )

        self.progress.setVisible(False)
        self.gen_btn.setEnabled(True)
        self.status_lbl.setText('Done! STL files generated.')

    def _export_bas(self):
        if not self.bas_stl_path:
            return
        dest, _ = QFileDialog.getSaveFileName(
            self, 'Save Bas-Relief', '', 'STL (*.stl)'
        )
        if dest:
            import shutil
            shutil.copy(self.bas_stl_path, dest)

    def _export_lit(self):
        if not self.lit_stl_path:
            return
        dest, _ = QFileDialog.getSaveFileName(
            self, 'Save Lithophane', '', 'STL (*.stl)'
        )
        if dest:
            import shutil
            shutil.copy(self.lit_stl_path, dest)

    def _export_plate(self):
        if not getattr(self, 'plate_stl_path', None):
            self.status_lbl.setText(
                'No label plate generated. Enter a URL before clicking Generate STL.'
            )
            return
        dest, _ = QFileDialog.getSaveFileName(
            self, 'Save Label Plate', '', 'STL (*.stl)'
        )
        if dest:
            import shutil
            shutil.copy(self.plate_stl_path, dest)

    def _generate_qr(self):
        url = self.url_input.text().strip()
        monument = self._get_monument_name() or 'Custom'
        path, err = generate_qr_code(url, OUTPUT_FOLDER, monument)
        if err:
            self.qr_status.setText('Error: ' + err)
            return
        pix = QPixmap(path).scaledToWidth(200)
        self.qr_preview.setPixmap(pix)
        self.qr_status.setText(f'QR image saved to: {path}')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())