
# Video Segment Selector

A PySide6-based GUI application for **selecting and exporting segments** of a video.
Features:

* **Live camera preview** or **load video files** (`.mp4`, `.avi`, `.mov`, `.mkv`).
* **Segment selection slider** with draggable handles.
* **Export selected segment** as:

  * **Individual frames** (JPEG images).
  * **Short video clip** (MP4).
* **Drag & drop** support for quick video loading.

---

## Features

* Play/Pause video playback.
* Switch between camera feed and video files.
* Interactive range selector for start/end frames.
* Export as:

  * **Frames** (images for each frame in the selection).
  * **Video** (single short clip of the selection).

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/video-segment-selector.git
cd video-segment-selector
```

### 2. Create and activate a Conda environment

```bash
conda create -n vidsegment python=3.9
conda activate vidsegment
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

## Usage

Run the application:

```bash
python video_segment_selector.py
```

### Controls:

* **Load video**: Click "Switch to video" and choose a file or drag & drop into the window.
* **Select segment**: Drag the handles in the slider to set start and end frames.
* **Export**:

  * **"Export Segment"** → Saves selected frames as `.jpg`.
  * **"Export Segment Video"** → Saves selected range as a `.mp4` clip.

---

## Output

* Exported frames: `frame_00001.jpg`, `frame_00002.jpg`, …
* Exported video: `segment.mp4` (or custom name chosen in save dialog).

---

## Dependencies

* [PySide6](https://pypi.org/project/PySide6/) – GUI framework
* [OpenCV](https://pypi.org/project/opencv-python/) – Video processing
* [qimage2ndarray](https://pypi.org/project/qimage2ndarray/) – Convert NumPy arrays to Qt images

## Executable 
If you want to avoid the hassle of installation, you can also download the built executable here and it also include the screenshots of the UI and more details instructions of how to use the tool https://bill2239.itch.io/video-segment-selector

## License

GPL3.0

---

