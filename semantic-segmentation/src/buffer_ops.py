__author__='karamach'

# bunch of buffer operations using basic oiio functions that can be chained together
# to form more complex ops. Most of them operate on image or buffer lists independently
# transforming them into output buffer lists. Some of them like weighted sum etc operate
# on the input list as a whole.

import functools
from functools import reduce
import PyOpenImageIO as oiio

# buf_list : [buf1, buf2, buf3 ...] where bufi = (bufi.R, bufi.G, ...)
# res_buf :  (res_buf.R, res_buf.G, .. ) where res_buf.R = buf1.R+buf2.R + .. 
class AddBuffersOp(object):

    @staticmethod
    def add_buffers(buf1, buf2):
        dst = oiio.ImageBuf()
        oiio.ImageBufAlgo.add(dst, buf1, buf2)
        return dst        

    def op(self, buf_list):
        return [reduce(lambda buf1, buf2: AddBuffersOp.add_buffers(buf1, buf2), buf_list)]

# Return the product of buffers in the input buffer list
class MultiplyBuffersOp(object):

    @staticmethod
    def multiply_buffers(buf1, buf2):
        dst = oiio.ImageBuf()
        oiio.ImageBufAlgo.mul(dst, buf1, buf2)
        return dst        

    def op(self, buf_list):
        return [reduce(lambda buf1, buf2: MultiplyBuffersOp.multiply_buffers(buf1, buf2), buf_list)]

# Select specific channels op
class SelectChannelsOp(object):

    def __init__(self, channels):
        self.channels = channels

    @staticmethod
    def select(buf, channels):
        dst = oiio.ImageBuf()
        oiio.ImageBufAlgo.channels(dst, buf, channels)
        return dst        

    def op(self, buf_list):
        return list(map(lambda buf: SelectChannelsOp.select(buf, self.channels), buf_list))

# Select specific channels by index and assign new names
class SelectChannelsByIndexOp(object):

    def __init__(self, channel_idxs, channel_names):
        self.channel_idxs = tuple(channel_idxs)
        self.channel_names = tuple(channel_names)

    @staticmethod
    def select(buf, channel_idxs, channel_names):
        dst = oiio.ImageBuf()
        oiio.ImageBufAlgo.channels(dst, buf, channelorder=channel_idxs, newchannelnames=channel_names)
        return dst        

    def op(self, buf_list):
        return list(map(lambda buf: SelectChannelsByIndexOp.select(buf, self.channel_idxs, self.channel_names), buf_list))
    

# Invert OIIOBuffer
class InvertBuffersOp:

    @staticmethod
    def invert(src):
        dst = oiio.ImageBuf()
        oiio.ImageBufAlgo.invert(dst, src)
        return dst                

    def op(self, buf_list):
        return list(map(lambda buf: InvertBuffersOp.invert(buf), buf_list))

    
# Select specific channels op
class SelectChannelsValuesOp(object):

    def __init__(self, channels, values):
        self.channels = channels
        self.values = values

    @staticmethod
    def select(buf, values, channels):
        dst = oiio.ImageBuf()
        oiio.ImageBufAlgo.channels(dst, buf, values, channels)
        return dst        

    def op(self, buf_list):
        return list(map(lambda buf: SelectChannelsValuesOp.select(buf, self.values, self.channels), buf_list))
    

# Get rgb channels from input
class GetRGBChannelsOp(object):
    def __init__(self):
        self.selector = SelectChannelsOp(('R', 'G', 'B',))

    def op(self, buf_list):
        return self.selector.op(buf_list)

# Get specific channels from input
class GetSpecificChannelsOp(object):
    
    def __init__(self, values):
        self.selector = SelectChannelsValuesOp(('R', 'G', 'B',), values)

    def op(self, buf_list):
        return self.selector.op(buf_list)
    
# convert 2 srgb
class Convert2SRGBOp(object):

    @staticmethod
    def convert(buf):
        dst = oiio.ImageBuf()
        oiio.ImageBufAlgo.colorconvert(dst, buf, 'linear', 'sRGB')
        dst.specmod().attribute('oiio:ColorSpace', 'sRGB')
        return dst        
    
    def op(self, buf_list):
        return list(map(lambda buf: Convert2SRGBOp.convert(buf), buf_list))

# add alpha channel
class AddAlphaChannelOp(object):

    def __init__(self, src_buf):
        self.alpha = oiio.ImageBuf()
        oiio.ImageBufAlgo.channels(self.alpha, src_buf, ('A',))

    @staticmethod
    def append_buffers(buf1, buf2):
        dst = oiio.ImageBuf()
        oiio.ImageBufAlgo.channel_append(dst, buf1, buf2)
        return dst        

    def op(self, buf_list):        
        return [reduce(lambda buf1, buf2: AddAlphaChannelOp.append_buffers(buf1, buf2), buf_list + [self.alpha])]

# concatenate buffs op
class ConcatenateBufsOp(object):

    @staticmethod
    def append_buffers(buf1, buf2):
        dst = oiio.ImageBuf()
        oiio.ImageBufAlgo.channel_append(dst, buf1, buf2)
        return dst        

    def op(self, buf_list):        
        return [reduce(lambda buf1, buf2: ConcatenateBufsOp.append_buffers(buf1, buf2), buf_list)]
    
# Do a scalar multiplication with the input
class ScalarMultiplyOp(object):

    def __init__(self, weights):
        self.weights = weights

    # multiply image buffer with weight
    @staticmethod
    def mul_buffer_scalar(buf, wt):
        dst = oiio.ImageBuf()
        oiio.ImageBufAlgo.mul(dst, buf, wt)
        return dst

    def op(self, buf_list):        
        # apply img weights to individual img bufs in the list
        return list(map(lambda buf_wt: ScalarMultiplyOp.mul_buffer_scalar(buf_wt[0], buf_wt[1]), zip(buf_list, self.weights)))

# Do a scalar addition with the input    
class ScalarAddOp(object):

    def __init__(self, weights):
        self.weights = weights

    # multiply image buffer with weight
    @staticmethod
    def add_buffer_scalar(buf, wt):
        dst = oiio.ImageBuf()
        oiio.ImageBufAlgo.add(dst, buf, wt)
        return dst

    def op(self, buf_list):        
        # apply img weights to individual img bufs in the list
        return list(map(lambda buf_wt: ScalarAddOp.add_buffer_scalar(buf_wt[0], buf_wt[1]), zip(buf_list, self.weights)))

# Convert input to png
class ConvertToPNGOp(object):

    # get channels from buf
    @staticmethod
    def get_rgba_channels(src):
        dst = oiio.ImageBuf()
        oiio.ImageBufAlgo.channels(dst, src, ('R', 'G', 'B', 'A',))
        return dst

    # convert to full display size
    @staticmethod
    def extract_display_window(src):
        dst = oiio.ImageBuf()
        oiio.ImageBufAlgo.crop(dst, src, oiio.get_roi_full(src.spec()))
        return dst    
        
    def op(self, buf_list):
        return list(map(
            lambda buf: ConvertToPNGOp.extract_display_window(ConvertToPNGOp.get_rgba_channels(buf)),
            buf_list
        ))

# Get specific channels
class GetChannelsOp(object):
    
    # get channels from buf
    @staticmethod
    def get_channels(src, channels):
        dst = oiio.ImageBuf()
        oiio.ImageBufAlgo.channels(dst, src, channels)
        return dst
    
    def op(self, buf_list):
        # get common channels across all img bufs
        buf_channel_names = map(lambda buf: set(buf.spec().channelnames), buf_list)
        common_channels = reduce(lambda channels1, channels2: channels1.intersection(channels2), buf_channel_names)
        return list(map(lambda buf: GetChannelsOp.get_channels(buf, tuple(common_channels)), buf_list))

# Copy channels from different layers
class ChannelCopyOp(object):
    
    def __init__(self, channel):
        self.channel = channel

    @staticmethod
    def channel_copy(channel, src):
        dst = oiio.ImageBuf()
        oiio.ImageBufAlgo.channels(dst, src, (channel + '.R', channel + '.G', channel + '.B',), ('R', 'G', 'B',))
        return dst
            
    def op(self, buf_list):
        return list(map(lambda buf: ChannelCopyOp.channel_copy(self.channel, buf), buf_list))

# Composite each of the buffers in the buf_list over base buf o
class CompositorOp(object):

    def __init__(self, base_buf):
        self.base_buf = base_buf

    @staticmethod
    def composite(A, B):
        dst = oiio.ImageBuf()
        oiio.ImageBufAlgo.over(dst, A, B)
        return dst        

    def op(self, buf_list):
        return list(map(lambda buf: CompositorOp.composite(buf, self.base_buf), buf_list))

# Weighted layer sum op
class WeightedLayerSumOp(object):

    def __init__(self, layers, alpha_src):
        self.layers = layers
        self.operators = [LayerTransformationOp( ('R', 'G', 'B',), layers), AddBuffersOp(),  AddAlphaChannelOp(alpha_src)]

    def op(self, buf_list):
        return [reduce(lambda res, operator: operator.op(res), self.operators, buf_list)]

# Weighted image sum op 
class WeightedImageSumOp(object):

    def __init__(self, weights):
        self.operators = [ScalarMultiplyOp(weights), AddBuffersOp()]

    def op(self, img_list):
        return reduce(lambda res, operator: operator.op(res), self.operators, img_list)

# Clamp buffers between min and max threshold values. Defaults are 0 and inf
class ClampOp(object):

    def __init__(self, min_th=0, max_th=float('inf')):
        self.min_th = min_th
        self.max_th = max_th

    def clamp(self, src):
        dst = oiio.ImageBuf()
        oiio.ImageBufAlgo.clamp(dst, src, self.min_th, self.max_th)
        return dst                

    def op(self, buf_list):
        return list(map(lambda buf: self.clamp(buf), buf_list))

# Do a weighted sum of images and add the aplha channel from alpha_src
class WeightedImageSumWithAlphaOp(object):

    def __init__(self, weights, alpha_src):
        self.operators = [WeightedImageSumOp(weights),  AddAlphaChannelOp(alpha_src)]

    def op(self, img_list):
        return reduce(lambda res, operator: operator.op(res), self.operators, img_list)
    
# Resize img to specified width, height
class ResizeSquareOp(object):

    def __init__(self, dim):
        self.dim = dim

    def __resize(self, src):
        s = src.spec()
        aspect_ratio = float(s.width)/s.height
        (w, h) = (self.dim, int(self.dim/aspect_ratio)) if s.width > s.height else (int(self.dim*aspect_ratio), self.dim)
        dst = oiio.ImageBuf(oiio.ImageSpec(w, h, 3, oiio.UINT8))
        oiio.ImageBufAlgo.resize(dst, src) 
        return dst

    def op(self, img_list):
        return list(map(lambda img: self.__resize(img), img_list))

# Extend image into a square region with dimension being same as larger
# dimension of source and image being in center. Fill unfilled regions with black
class ExtentCenterOp(object):

    @staticmethod
    def get_origins(src, dst):
        w_beg = int((dst.spec().width - src.spec().width)/2)
        h_beg = int((dst.spec().height - src.spec().height)/2)
        return w_beg, h_beg
    
    def __copy(self, src):
        src_w, src_h =  src.spec().width,  src.spec().height
        dst = oiio.ImageBuf(oiio.ImageSpec(max(src_w, src_h), max(src_w, src_h), 3, oiio.UINT8))
        oiio.ImageBufAlgo.zero(dst)   
        w_beg, h_beg = ExtentCenterOp.get_origins(src, dst)
        oiio.ImageBufAlgo.paste(dst, w_beg, h_beg, 0, 0, src) 
        return dst

    def op(self, img_list):
        return list(map(lambda img: self.__copy(img), img_list))

# Convert pixels to ImgBuf
class Pixels2BufOp:

    @staticmethod
    def pixels2buf(pixels, typ):
        buf = oiio.ImageBuf(oiio.ImageSpec(*pixels.shape, typ))
        buf.set_pixels(oiio.ROI(), pixels)
        return buf
        
        
    def op(self, pixels_list, types):
        return list(map(lambda pixels_type: Pixels2BufOp.pixels2buf(*pixels_type), zip(pixels_list, types)))
        
