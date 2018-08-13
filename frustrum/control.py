
class CameraRotController(Controllrt):

    def __init__(self, camera, rot_idx):
        self.camera = camera
        self.rot_idx = rot_idx
        
    def update(self, val):
        ypr = self.camera.curr_ypr
        ypr[self.rot_idx] = math.radians(val)
