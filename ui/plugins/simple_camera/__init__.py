import tkinter as tk
import tkinter.ttk as ttk
from ui.plugin import ClosingHandler, PluginInfo, Plugin
from utils import EventInfo, EventQueue
from widgets.funky_btn import FunkyButton
from widgets.graphics import *
import cv2
from PIL import Image, ImageTk

"""
"nvarguscamerasrc sensor-id=%d ! "
        "video/x-raw(memory:NVMM), width=(int)%d, height=(int)%d, framerate=(fraction)%d/1 ! "
        "nvvidconv flip-method=%d ! "
        "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
        "videoconvert ! "
        "video/x-raw, format=(string)BGR ! appsink"
        """


def gstreamer_pipeline(
    sensor_id=0,
    capture_width=1920,
    capture_height=1080,
    display_width=960,
    display_height=540,
    framerate=30,
    flip_method=0,
):
    return (
        """nvarguscamerasrc sensor-id=%d ! video/x-raw(memory:NVMM), width=(int)%d, height=(int)%d, format=(string)NV12, framerate=(fraction)%d/1 ! nvvidconv flip-method=%d ! video/x-raw, width=(int)%d, height=(int)%d, , format=(string)BGRx ! videoconvert"""
        % (
            sensor_id,
            capture_width,
            capture_height,
            framerate,
            flip_method,
            display_width,
            display_height,
        )
    )

class SimpleCameraPlugin(Plugin):
    def __init__(self, master:tk.Misc, mainEventQueue:EventQueue, **kw):
        super().__init__(master, mainEventQueue, **kw)
        btnSize = 80
        btnTextSize = 10

        # Menu bar
        self.menuBar = tk.Frame(self, width=kw['width'], height=btnSize)
        self.backBtn = FunkyButton(BtnInfo(BtnStyle.Style2, BtnShape.Multiply, BtnColor.Red), btnSize, btnTextSize, self.menuBar, "Back", self.back)
        self.backBtn.grid(column=0,row=0)
        self.menuBar.pack(side='top')
        self.menuBar.grid_propagate(False)

        # Main UI area
        self.mainFrame = tk.Frame(self, width=kw['width'],height=kw['height']-btnSize)

        # Camera
        self.cameraContainer = tk.Label(self.mainFrame)
        self.videoCapture = cv2.VideoCapture(gstreamer_pipeline(flip_method=0), cv2.CAP_GSTREAMER)
        self.eventQueue.schedule(self.refresh_frame, 1/30, True)
        self.cameraContainer.pack()
        self._run = True
    
    def on_closing(self, handler: ClosingHandler):
        self._run = False
        handler.cancel = False
        self.videoCapture.release()

    def refresh_frame(self, info:EventInfo):
        if not self._run:
            info.exit()
            return
        if self.videoCapture.isOpened():
            try:
                _, frame = self.videoCapture.read()
                # Convert image from one color space to other
                opencv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
            
                # Capture the latest frame and transform to image
                captured_image = Image.fromarray(opencv_image)
            
                # Convert captured image to photoimage
                photo_image = ImageTk.PhotoImage(image=captured_image)
            
                # Displaying photoimage in the label
                self.cameraContainer.photo_image = photo_image
            
                # Configure image in the label
                self.cameraContainer.configure(image=photo_image)
                    
            except:
                info.exit()
                self.back()
        else:
            print("Error: Unable to open camera")
            info.exit()
            self.back()

PLUGIN_INFO = PluginInfo("Simple camera", BtnInfo(BtnStyle.Style2, BtnShape.Camera, BtnColor.Green))
ENTRY_POINT = SimpleCameraPlugin