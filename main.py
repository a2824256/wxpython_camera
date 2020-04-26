import cv2
from wx import *
import pyzed.sl as sl
import math
import numpy as np
import sys
from PIL import Image as img
COVER = 'screenshot.png'
TYPE = "zed"


class camera(Frame):

    def __init__(self, parent, title):
        Frame.__init__(self, parent, title=title, size=(600, 600))
        self.panel = Panel(self)
        self.Center()
        self.image_cover = Image(COVER, BITMAP_TYPE_ANY).Scale(350, 300)
        self.bmp = StaticBitmap(self.panel, -1, Bitmap(self.image_cover))
        self.counter = 0
        start_button = Button(self.panel, label='Start')
        close_button = Button(self.panel, label='Close')
        take_button = Button(self.panel, label='Take photo')

        self.Bind(EVT_BUTTON, self.start, start_button)
        self.Bind(EVT_BUTTON, self.close, close_button)
        # 修改截图命令
        self.Bind(EVT_BUTTON, self.zed_take, take_button)
        self.grid_bag_sizer = GridBagSizer(hgap=5, vgap=5)
        self.grid_bag_sizer.Add(self.bmp, pos=(0, 0), flag=ALL | EXPAND, span=(4, 4), border=5)
        self.grid_bag_sizer.Add(start_button, pos=(4, 1), flag=ALL | ALIGN_CENTER_VERTICAL, span=(1, 1), border=5)
        self.grid_bag_sizer.Add(close_button, pos=(4, 2), flag=ALL | ALIGN_CENTER_VERTICAL, span=(1, 1), border=5)
        self.grid_bag_sizer.Add(take_button, pos=(4, 3), flag=ALL | ALIGN_CENTER_VERTICAL, span=(1, 1), border=5)

        self.grid_bag_sizer.AddGrowableCol(0, 1)
        self.grid_bag_sizer.AddGrowableRow(0, 1)
        self.panel.SetSizer(self.grid_bag_sizer)
        self.grid_bag_sizer.Fit(self)


    # opencv 开启普通摄像头函数
    def open_camera(self, event):
        self.cap = cv2.VideoCapture(0)
        self.cnt = 0
        counter = 0
        while (self.cap.isOpened()):

            flag, im_rd = self.cap.read()
            self.frame = im_rd
            #k = cv2.waitKey(1)
            #print(k)
            #if k == ord('a'):
                #cv2.imwrite("test.jpg", im_rd)
                #break
            height, width = im_rd.shape[:2]
            image1 = cv2.cvtColor(im_rd, cv2.COLOR_BGR2RGB)
            pic = Bitmap.FromBuffer(width, height, image1)
            self.bmp.SetBitmap(pic)
            self.grid_bag_sizer.Fit(self)
            counter += 1
        self.cap.release()

    # zed_mini 自带驱动打开摄像头
    def open_zed(self, event):
        self.zed = sl.Camera()

        # Create a InitParameters object and set configuration parameters
        init_params = sl.InitParameters()
        init_params.depth_mode = sl.DEPTH_MODE.QUALITY  # Use PERFORMANCE depth mode
        init_params.coordinate_units = sl.UNIT.METER  # Use meter units (for depth measurements)
        init_params.camera_resolution = sl.RESOLUTION.VGA
        init_params.camera_fps = 100

        # Open the camera
        err = self.zed.open(init_params)
        if err != sl.ERROR_CODE.SUCCESS:
            exit(1)

        # Create and set RuntimeParameters after opening the camera
        runtime_parameters = sl.RuntimeParameters()
        runtime_parameters.sensing_mode = sl.SENSING_MODE.STANDARD  # Use STANDARD sensing mode
        # Setting the depth confidence parameters
        runtime_parameters.confidence_threshold = 100
        runtime_parameters.textureness_confidence_threshold = 100

        # Capture 150 images and depth, then stop
        i = 0
        self.image = sl.Mat()
        # cv2.imwrite("i1.jpg", MatrixToImage(image))
        self.depth = sl.Mat()
        # cv2.imwrite("d1.jpg", MatrixToImage(depth))
        self.point_cloud = sl.Mat()

        mirror_ref = sl.Transform()
        mirror_ref.set_translation(sl.Translation(2.75, 4.0, 0))
        tr_np = mirror_ref.m

        while True:
            # A new image is available if grab() returns SUCCESS
            if self.zed.grab(runtime_parameters) == sl.ERROR_CODE.SUCCESS:
                # Retrieve left image
                self.zed.retrieve_image(self.image, sl.VIEW.LEFT)
                # Retrieve depth map. Depth is aligned on the left image
                self.zed.retrieve_measure(self.depth, sl.MEASURE.DEPTH)
                # Retrieve colored point cloud. Point cloud is aligned on the left image.
                self.zed.retrieve_measure(self.point_cloud, sl.MEASURE.XYZRGBA)
                id = self.image.get_data()
                # dd = self.depth.get_data()
                im = img.fromarray(id)
                imi = im.convert('RGB')
                # im = img.fromarray(dd)
                # imd = im.convert('RGB')
                self.frame = imi
                size = imi.size
                image1 = cv2.cvtColor(np.asarray(imi), cv2.COLOR_BGR2RGB)
                pic = Bitmap.FromBuffer(size[0], size[1], image1)
                self.bmp.SetBitmap(pic)
                self.grid_bag_sizer.Fit(self)
                # im.save("test2.jpg")
                # Get and print distance value in mm at the center of the image
                # We measure the distance camera - object using Euclidean distance
                x = round(self.image.get_width() / 2)
                y = round(self.image.get_height() / 2)
                err, point_cloud_value = self.point_cloud.get_value(x, y)

                distance = math.sqrt(point_cloud_value[0] * point_cloud_value[0] +
                                     point_cloud_value[1] * point_cloud_value[1] +
                                     point_cloud_value[2] * point_cloud_value[2])

                point_cloud_np = self.point_cloud.get_data()
                point_cloud_np.dot(tr_np)

                if not np.isnan(distance) and not np.isinf(distance):
                    print("Distance to Camera at ({}, {}) (image center): {:1.3} m".format(x, y, distance), end="\r")
                    # Increment the loop
                    i = i + 1
                else:
                    print("Can't estimate distance at this position.")
                    print("Your camera is probably too close to the scene, please move it backwards.\n")
                sys.stdout.flush()

        # Close the camera
        self.zed.close()

    def zed_take(self, event):
        img1 = self.image.get_data()
        # dimg = self.depth.get_data()
        im = img.fromarray(img1)
        imi = im.convert('RGB')
        imi.save(str(self.counter) + ".jpg")
        # im = img.fromarray(dimg)
        # imd = im.convert('RGB')
        # imd.save(str(self.counter) + "_d.jpg")
        depth_zed = sl.Mat(self.zed.get_camera_information().camera_resolution.width,
                           self.zed.get_camera_information().camera_resolution.height, sl.MAT_TYPE.F32_C1)
        if self.zed.grab() == sl.ERROR_CODE.SUCCESS:
            # Retrieve depth data (32-bit)
            self.zed.retrieve_measure(depth_zed, sl.MEASURE.DEPTH)
            # Load depth data into a numpy array
            depth_ocv = depth_zed.get_data()
            depth_img = img.fromarray(depth_ocv)
            depth_img2 = depth_img.convert('RGB')
            depth_img2.save(str(self.counter) + "_d.jpg")
        self.counter += 1


    def take(self, event):
        cv2.imwrite(str(self.counter) + ".jpg", self.frame)
        self.counter += 1

    def start(self, event):
        import _thread
        # 在此修改选用哪种摄像头
        _thread.start_new_thread(self.open_zed, (event,))

    def close(self, event):
        if TYPE == "zed":
            self.zed.close()
        else:
            self.cap.release()

        self.bmp.SetBitmap(Bitmap(self.image_cover))
        self.grid_bag_sizer.Fit(self)


class camera_app(App):
    def OnInit(self):
        self.frame = camera(parent=None, title="camera")
        self.frame.Show(True)
        return True


if __name__ == "__main__":
    app = camera_app()
    app.MainLoop()
