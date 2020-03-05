import cv2
from wx import *


COVER = 'screenshot.png'


class camera(Frame):

    def __init__(self,parent,title):
       Frame.__init__(self,parent,title=title,size=(600,600))
       self.panel = Panel(self)
       self.Center()

       self.image_cover = Image(COVER, BITMAP_TYPE_ANY).Scale(350,300)
       self.bmp = StaticBitmap(self.panel, -1, Bitmap(self.image_cover))

       start_button = Button(self.panel,label='Start')
       close_button = Button(self.panel,label='Close')

       self.Bind(EVT_BUTTON,self.start,start_button)
       self.Bind(EVT_BUTTON,self.close,close_button)
       self.grid_bag_sizer = GridBagSizer(hgap=5,vgap=5)
       self.grid_bag_sizer.Add(self.bmp, pos=(0, 0), flag=ALL | EXPAND, span=(4, 4), border=5)
       self.grid_bag_sizer.Add(start_button, pos=(4, 1), flag=ALL | ALIGN_CENTER_VERTICAL, span=(1, 1), border=5)
       self.grid_bag_sizer.Add(close_button, pos=(4, 2), flag=ALL | ALIGN_CENTER_VERTICAL, span=(1, 1), border=5)

       self.grid_bag_sizer.AddGrowableCol(0,1)
       self.grid_bag_sizer.AddGrowableRow(0,1)
       self.panel.SetSizer(self.grid_bag_sizer)
       self.grid_bag_sizer.Fit(self)



    def open_camera(self,event):
       self.cap = cv2.VideoCapture(0)
       self.cap.set(3, 480)
       self.cnt = 0

       while(self.cap.isOpened()):

           flag, im_rd = self.cap.read()
           self.k = cv2.waitKey(1)

           if(self.k == ord('q')):
               break
           height,width = im_rd.shape[:2]
           image1 = cv2.cvtColor(im_rd, cv2.COLOR_BGR2RGB)
           pic = Bitmap.FromBuffer(width,height,image1)
           self.bmp.SetBitmap(pic)
           self.grid_bag_sizer.Fit(self)

       self.cap.release()


    def start(self,event):
        # 多线程
       import _thread
       _thread.start_new_thread(self.open_camera, (event,))


    def close(self,event):
       self.cap.release()
       self.bmp.SetBitmap(Bitmap(self.image_cover))
       self.grid_bag_sizer.Fit(self)


class camera_app(App):
    def OnInit(self):
       self.frame = camera(parent=None,title="camera")
       self.frame.Show(True)
       return True

if __name__ == "__main__":
    app = camera_app()
    app.MainLoop()
