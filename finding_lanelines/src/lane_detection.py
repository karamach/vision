import math
import cv2
from utils import *

class LaneDetector(object):

    def __init__(self):
        pass

    # canny transform
    def canny(self, img, low_threshold, high_threshold):
        return cv2.Canny(img, low_threshold, high_threshold) 

    def gaussian_blur(self, img, kernel_size):
        return cv2.GaussianBlur(img, (kernel_size, kernel_size), 0)

    # Find region of interest for the lanes based on defined polygon
    def region_of_interest(self, img, vertices):
        # defining a blank mask to start with
        mask = np.zeros_like(img)   
    
        # defining a 3 channel or 1 channel color to fill the mask with depending on the input image
        if len(img.shape) > 2:
            channel_count = img.shape[2]  # i.e. 3 or 4 depending on your image
            ignore_mask_color = (255,) * channel_count
        else:
            ignore_mask_color = 255
        
        # filling pixels inside the polygon defined by "vertices" with the fill color    
        cv2.fillPoly(mask, vertices, ignore_mask_color)
    
        # returning the image only where mask pixels are nonzero
        masked_image = cv2.bitwise_and(img, mask)
        return masked_image

    
    def draw_lines(self, img, lines, color=[255, 0, 0], thickness=5):
        ll_slope_sum, ll_cnt, rl_slope_sum, rl_cnt = 0, 0, 0, 0
        ll_max, rl_max = (img.shape[1], img.shape[0]), (img.shape[1], img.shape[0])

        # Limit left lane lines with slopes between 20 and 70 degrees and right lane
        # slopes between 100 and 160 degrees.
        for line in lines:
            for x1, y1, x2, y2 in line:
                slope = Utils.get_slope(x1, y1, x2, y2)
                if 100 < math.degrees(slope) < 160:
                    rl_cnt += 1
                    rl_slope_sum += slope
                    rl_max = (x1, y1) if y1 < rl_max[1] else rl_max
                elif 20 < math.degrees(slope) < 70:
                    ll_cnt += 1
                    ll_slope_sum += slope
                    ll_max = (x2, y2) if y2 < ll_max[1] else ll_max

        # Draw left and right lanes based on top most value and average slope
        top_bound = int(img.shape[0] * .62)
        if ll_cnt > 0:
            (llx2, lly2) = ll_max
            (llx1, lly1) = (int(llx2 - (img.shape[0]-lly2)/math.tan(float(ll_slope_sum)/ll_cnt)), img.shape[0])
            assert (0 < Utils.get_slope(llx1, lly1, llx2, lly2) < math.pi/2)
            if lly2 > top_bound:
                llx2, lly2 = int(llx2 + (lly2-top_bound)/math.tan(float(ll_slope_sum)/ll_cnt)), top_bound
            elif lly2 < top_bound:
                llx2, lly2 = int(llx2 - (top_bound-lly2)/math.tan(float(ll_slope_sum)/ll_cnt)), top_bound
            cv2.line(img, (llx1, lly1), (llx2, lly2), color, thickness)
        if rl_cnt > 0:
            (rlx1, rly1) = rl_max
            (rlx2, rly2) = (int(rlx1 + (rly1-img.shape[0])/math.tan(float(rl_slope_sum)/rl_cnt)), img.shape[0])
            assert (math.pi/2 < Utils.get_slope(rlx1, rly1, rlx2, rly2) < math.pi)
            if rly1 > top_bound:
                rlx1, rly1 = int(rlx1 - (rly1-top_bound)/abs(math.tan(float(rl_slope_sum)/rl_cnt))), top_bound
            elif rly1 < top_bound:
                rlx1, rly1 = int(rlx1 + (top_bound-rly1)/abs(math.tan(float(rl_slope_sum)/rl_cnt))), top_bound
            cv2.line(img, (rlx1, rly1), (rlx2, rly2), color, thickness)

    # Input is a canny transformed image. Generates the hough lines
    def hough_lines(self, img, rho, theta, threshold, min_line_len, max_line_gap):
        lines = cv2.HoughLinesP(img, rho, theta, threshold, np.array([]), minLineLength=min_line_len, maxLineGap=max_line_gap)
        line_img = np.zeros((img.shape[0], img.shape[1], 3), dtype=np.uint8)
        if lines is not None:
            self.draw_lines(line_img, lines)
        return line_img

    # final image is a weighted combination of the original image and image with hough lines 
    def weighted_img(self, img, initial_img, α=0.8, β=1., λ=0.):
        return cv2.addWeighted(initial_img, α, img, β, λ)

    def mark_lane(self, image):
        imshape = image.shape
        gray_img = Utils.gray_scale(image)
        gaussian_blur_img = self.gaussian_blur(gray_img, 5)
        edges = self.canny(gaussian_blur_img, 60, 200)
        vertices = np.array([[(50, imshape[0]), (imshape[1]*.4, imshape[0]*.6), (imshape[1]*.6, imshape[0]*.6), (imshape[1], imshape[0])]],dtype=np.int32)
        roi = self.region_of_interest(edges, vertices)
        hough_out = self.hough_lines(roi, 1, np.pi / 180, 50, 180, 149)
        lane_marked = self.weighted_img(hough_out, image)
        return lane_marked

def run_test_images():
    ld = LaneDetector()    

    img = Utils.load_image('../data/solidWhiteRight.jpg')
    cv2.imwrite('../output/solidWhiteRight.jpg', cv2.cvtColor(ld.mark_lane(img), cv2.COLOR_RGB2BGR))
    img = Utils.load_image('../data/solidYellowCurve.jpg')
    cv2.imwrite('../output/solidYellowCurve.jpg', cv2.cvtColor(ld.mark_lane(img), cv2.COLOR_RGB2BGR))
    img = Utils.load_image('../data/solidYellowCurve2.jpg')
    cv2.imwrite('../output/solidYellowCurve2.jpg', cv2.cvtColor(ld.mark_lane(img), cv2.COLOR_RGB2BGR))
    img = Utils.load_image('../data/solidYellowLeft.jpg')
    cv2.imwrite('../output/solidYellowLeft.jpg', cv2.cvtColor(ld.mark_lane(img), cv2.COLOR_RGB2BGR))
    img = Utils.load_image('../data/whiteCarLaneSwitch.jpg')
    cv2.imwrite('../output/whiteCarLaneSwitch.jpg', cv2.cvtColor(ld.mark_lane(img), cv2.COLOR_RGB2BGR))
    img = Utils.load_image('../data/line-segments-example.jpg')
    cv2.imwrite('../output/line-segments-example.jpg', cv2.cvtColor(ld.mark_lane(img), cv2.COLOR_RGB2BGR))
    img = Utils.load_image('../data/laneLines_thirdPass.jpg')
    cv2.imwrite('../output/laneLines_thirdPass.jpg', cv2.cvtColor(ld.mark_lane(img), cv2.COLOR_RGB2BGR))

def run_test_video():
    ld = LaneDetector()
    import os
    from moviepy.editor import VideoFileClip
    clip = VideoFileClip("../data/solidYellowLeft.mp4")
    output_clip = clip.fl_image(ld.mark_lane)
    output_clip.write_videofile("../output/solidYellowLeft_out.mp4", audio=False)
    
if '__main__' == __name__:
    #run_test_images()    
    run_test_video()
