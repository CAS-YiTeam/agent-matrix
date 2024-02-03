import numpy as np
import asyncio
from vhmap.mcom import mcom
import queue

class VhmapDebugBridge():
    def __init__(self) -> None:
        self.queue_matrix_to_here = queue.Queue()

    def listen_update(self):
        while True:
            self.queue_matrix_to_here.get()

    def render(self, t):
        if not hasattr(self, 'visual_bridge'):
            self.visual_bridge = mcom(path='TEMP/v3d_logger/', draw_mode='Threejs')
            self.visual_bridge.v3d_init()
            self.visual_bridge.set_style('gray')
            self.visual_bridge.advanced_geometry_rotate_scale_translate('box', 'BoxGeometry(1,1,1)',   0,0,0,  1,1,1, 0,0,0)

        x = np.cos(t); y=np.sin(t); z= np.cos(t)*np.sin(t)  # 此帧的x,y,z坐标
        self.visual_bridge.v3d_object(
            'box|2233|Red|0.1',                         # 填入 ‘形状|几何体之ID标识|颜色|大小’即可
            x, y, z, ro_x=0, ro_y=0, ro_z=np.sin(t),    # 三维位置+欧拉旋转变换，六自由度
            track_n_frame=20)                           # 显示历史20帧留下的轨迹
        self.visual_bridge.v3d_show()   # 结束关键帧

