import cv2
import sys
from PySide6 import QtCore, QtGui, QtWidgets
import qimage2ndarray


class SegmentSelectorWidget(QtWidgets.QWidget):
    segmentChanged = QtCore.Signal(int, int)

    def __init__(self, total_frames=100, parent=None):
        super().__init__(parent)
        self.setFixedHeight(40)
        self.setMinimumWidth(400)
        self.total_frames = total_frames
        self.start_frame = 0
        self.end_frame = total_frames - 1
        self.dragging = None  # 'start', 'end', or None

    def set_range(self, total_frames):
        self.total_frames = total_frames
        self.end_frame = total_frames - 1
        self.update()

    def mousePressEvent(self, event):
        x = event.position().x() if hasattr(event, "position") else event.x()
        pos = self._pixel_to_frame(x)
        if abs(pos - self.start_frame) < self.total_frames/100.0:
            self.dragging = 'start'
        elif abs(pos - self.end_frame) < self.total_frames/100.0:
            self.dragging = 'end'

    def mouseMoveEvent(self, event):
        if self.dragging:
            x = event.position().x() if hasattr(event, "position") else event.x()
            frame = max(0, min(self._pixel_to_frame(x), self.total_frames - 1))
            if self.dragging == 'start':
                self.start_frame = min(frame, self.end_frame)
            elif self.dragging == 'end':
                self.end_frame = max(frame, self.start_frame)
            self.segmentChanged.emit(self.start_frame, self.end_frame)
            self.update()

    def mouseReleaseEvent(self, event):
        self.dragging = None

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        w = self.width()
        h = self.height()

        # Background bar
        painter.setBrush(QtGui.QColor(200, 200, 200))
        painter.drawRect(0, h // 3, w, h // 3)

        # Selected segment
        x1 = self._frame_to_pixel(self.start_frame)
        x2 = self._frame_to_pixel(self.end_frame)
        painter.setBrush(QtGui.QColor(100, 150, 255))
        painter.drawRect(x1, h // 3, x2 - x1, h // 3)

        # Handles
        handle_color = QtGui.QColor(255, 50, 50)
        painter.setBrush(handle_color)
        painter.drawRect(x1 - 2, 0, 4, h)
        painter.drawRect(x2 - 2, 0, 4, h)

    def _frame_to_pixel(self, frame):
        return int(frame / self.total_frames * self.width())

    def _pixel_to_frame(self, pixel):
        return int(pixel / self.width() * self.total_frames)
    

class VideoPlayer(QtWidgets.QWidget):
    pause = False
    video = False

    def __init__(self, width=640, height=480, fps=30):
        super().__init__()

        self.video_size = QtCore.QSize(width, height)
        self.camera_capture = cv2.VideoCapture(cv2.CAP_DSHOW)
        self.video_capture = cv2.VideoCapture()
        self.fps = fps
        self.total_frames = 0
        self.start_frame = 0
        self.end_frame = 0
        self.video_path = None

        self.setAcceptDrops(True)

        # Widgets
        self.frame_label = QtWidgets.QLabel()
        self.quit_button = QtWidgets.QPushButton("Quit")
        self.play_pause_button = QtWidgets.QPushButton("Pause")
        self.camera_video_button = QtWidgets.QPushButton("Switch to video")
        self.export_button = QtWidgets.QPushButton("Export Segment")
        self.segment_label = QtWidgets.QLabel("Selected segment: 0s - 0s")
        self.selector = SegmentSelectorWidget()
        self.selector.segmentChanged.connect(self.update_segment_from_selector)
        self.export_video_button = QtWidgets.QPushButton("Export Segment Video")
        


        # Layout
        self.main_layout = QtWidgets.QGridLayout()
        self.setup_ui()
        self.setup_camera(fps)

    def setup_ui(self):
        self.frame_label.setFixedSize(self.video_size)
        self.quit_button.clicked.connect(self.close_win)
        self.play_pause_button.clicked.connect(self.play_pause)
        self.camera_video_button.clicked.connect(self.camera_video)
        self.export_button.clicked.connect(self.export_segment)
        self.export_video_button.clicked.connect(self.export_segment_video)

        self.main_layout.addWidget(self.frame_label, 0, 0, 1, 3)
        self.main_layout.addWidget(self.selector, 1, 0, 1, 3)
        self.main_layout.addWidget(self.segment_label, 2, 0, 1, 3)
        self.main_layout.addWidget(self.camera_video_button, 3, 0)
        self.main_layout.addWidget(self.play_pause_button, 3, 1)
        self.main_layout.addWidget(self.quit_button, 3, 2)
        #self.main_layout.addWidget(self.export_button, 4, 0, 1, 3)
        self.main_layout.addWidget(self.export_button, 4, 0, 1, 2)
        self.main_layout.addWidget(self.export_video_button, 4, 2, 1, 1)
        self.frames_to_gif_button = QtWidgets.QPushButton("Frames → GIF")
        self.frames_to_gif_button.clicked.connect(self.framesto_gif)
        self.main_layout.addWidget(self.frames_to_gif_button, 5, 0, 1, 3)
        self.setLayout(self.main_layout)

    def setup_camera(self, fps):
        self.frame_timer = QtCore.QTimer()
        self.frame_timer.timeout.connect(self.display_video_stream)
        self.camera_capture.set(3, self.video_size.width())
        self.camera_capture.set(4, self.video_size.height())
        self.frame_timer.start(int(1000 // fps))

    def play_pause(self):
        if not self.pause:
            self.frame_timer.stop()
            self.play_pause_button.setText("Play")
        else:
            self.frame_timer.start(int(1000 // self.fps))
            self.play_pause_button.setText("Pause")
        self.pause = not self.pause

    def camera_video(self):
        path = QtWidgets.QFileDialog.getOpenFileName(filter="Videos (*.mp4 *.avi *.mov *.mkv)")
        if path[0]:
            self.load_video(path[0])

    def load_video(self, path):
        self.video_path = path
        self.video_capture.open(path)
        if not self.video_capture.isOpened():
            QtWidgets.QMessageBox.warning(self, "Error", "Failed to load video.")
            return

        self.total_frames = int(self.video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
        self.start_frame = 0
        self.end_frame = self.total_frames - 1
        self.selector.set_range(self.total_frames)

        self.video = True
        self.camera_video_button.setText("Switch to camera")

    def update_segment_from_selector(self, start, end):
        self.start_frame = start
        self.end_frame = end
        self.segment_label.setText(f"Selected segment: {start // self.fps}s - {end // self.fps}s")

    def display_video_stream(self):
        if not self.video:
            ret, frame = self.camera_capture.read()
        else:
            pos = self.video_capture.get(cv2.CAP_PROP_POS_FRAMES)
            if pos > self.end_frame:
                self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, self.start_frame)
            ret, frame = self.video_capture.read()

        if not ret:
            return

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        if not self.video:
            frame = cv2.flip(frame, 1)
        else:
            frame = cv2.resize(frame, (self.video_size.width(), self.video_size.height()), interpolation=cv2.INTER_AREA)

        image = qimage2ndarray.array2qimage(frame)
        self.frame_label.setPixmap(QtGui.QPixmap.fromImage(image))

    def export_segment(self):
        if not self.video_path:
            QtWidgets.QMessageBox.warning(self, "Error", "No video loaded.")
            return

        output_dir = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if not output_dir:
            return

        cap = cv2.VideoCapture(self.video_path)
        if not cap.isOpened():
            QtWidgets.QMessageBox.warning(self, "Error", "Failed to open video for export.")
            return

        cap.set(cv2.CAP_PROP_POS_FRAMES, self.start_frame)

        frame_num = self.start_frame
        saved_count = 0

        while frame_num <= self.end_frame:
            ret, frame = cap.read()
            if not ret:
                break

            filename = f"{output_dir}/frame_{frame_num:05d}.jpg"
            cv2.imwrite(filename, frame)
            saved_count += 1
            frame_num += 1

        cap.release()
        QtWidgets.QMessageBox.information(self, "Done", f"Saved {saved_count} images to:\n{output_dir}")

    def export_segment_video(self):
        if not self.video_path:
            QtWidgets.QMessageBox.warning(self, "Error", "No video loaded.")
            return

        output_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Save Video Segment", "segment.mp4", "Videos (*.mp4 *.avi *.mov)"
        )
        if not output_path:
            return

        cap = cv2.VideoCapture(self.video_path)
        if not cap.isOpened():
            QtWidgets.QMessageBox.warning(self, "Error", "Failed to open video for export.")
            return

        # Get video properties
        cap.set(cv2.CAP_PROP_POS_FRAMES, self.start_frame)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)

        # Setup writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # mp4 codec
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        frame_num = self.start_frame
        while frame_num <= self.end_frame:
            ret, frame = cap.read()
            if not ret:
                break
            out.write(frame)
            frame_num += 1

        cap.release()
        out.release()
        QtWidgets.QMessageBox.information(self, "Done", f"Exported segment video to:\n{output_path}")

    def framesto_gif(self, duration=0.1):
        # Select folder containing frames
        frames_dir = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Frames Directory")
        if not frames_dir:
            return
            
        # Get all image files sorted
        import glob, os
        frame_files = sorted(glob.glob(os.path.join(frames_dir, "*.jpg")))
        if not frame_files:
            QtWidgets.QMessageBox.warning(self, "Error", "No JPG frames found in the selected directory.")
            return
        
        # Ask where to save GIF
        output_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Save GIF", "output.gif", "GIF (*.gif)"
        )
        if not output_path:
            return

        # Create GIF using imageio
        import imageio
        with imageio.get_writer(output_path, mode='I', duration=duration) as writer:
            for file in frame_files:
                frame = imageio.imread(file)
                writer.append_data(frame)

        QtWidgets.QMessageBox.information(self, "Done", f"GIF saved to:\n{output_path}")

    def close_win(self):
        self.camera_capture.release()
        self.video_capture.release()
        cv2.destroyAllWindows()
        self.close()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            self.load_video(path)
            break

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    player = VideoPlayer()
    player.setWindowTitle("Video Segment Selector")
    player.resize(700, 600)
    player.show()
    sys.exit(app.exec())