"""Local camera acquisition, independent of the recognition models."""


class Camera:
    def __init__(self, index: int = 0):
        self.index = index
        self._device = None

    def __enter__(self):
        import cv2

        self._device = cv2.VideoCapture(self.index)
        if not self._device.isOpened():
            self._device.release()
            raise RuntimeError("Cannot open camera; check its index and OS camera permission")
        return self

    def read(self):
        """Return unmirrored RGB pixels."""
        import cv2

        ok, bgr = self._device.read()
        if not ok:
            raise RuntimeError("Cannot read a camera frame")
        return cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)

    def __exit__(self, *args):
        self._device.release()
