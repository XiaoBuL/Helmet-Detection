# -*- coding: utf-8 -*
import numpy as np

import timeit
from PIL import Image
from PIL import ImageDraw 
import os
import numpy as np
import matplotlib.pyplot as plt

plt.rcParams['figure.figsize'] = (10, 10)
plt.rcParams['image.interpolation'] = 'nearest'
plt.rcParams['image.cmap'] = 'gray'

# Make sure that the work directory is caffe_root
caffe_root = './' 
# modify img_dir to your path of testing images of kitti
#需要测试的集合的图片
img_dir = 'models/test/'
import os
os.chdir(caffe_root)
import sys
sys.path.insert(0, 'python')
from google.protobuf import text_format
from caffe.proto import caffe_pb2

import caffe
#from _ensemble import *

caffe.set_mode_cpu()
#deploy,模型，和labelmap的位置
model_def = 'models/VGGNet/VOChelmet/SSD_300x300/deploy.prototxt'
model_weights = 'models/VGGNet/VOChelmet/SSD_300x300/VGG_VOChelmet_SSD_300x300_iter_1200.caffemodel'
voc_labelmap_file = caffe_root+'data/VOChelmet/labelmap_voc.prototxt'
#最后标记完保存的路径
save_dir = 'models/VGGNet/'
#txt_dir =  'models/helmet/result1-150000/'
#f = open (r'out_3d.txt','w')

file = open(voc_labelmap_file, 'r')
labelmap = caffe_pb2.LabelMap()
text_format.Merge(str(file.read()), labelmap) 

net = caffe.Net(model_def,model_weights,caffe.TEST)
transformer = caffe.io.Transformer({'data': net.blobs['data'].data.shape})
transformer.set_transpose('data', (2, 0, 1))
transformer.set_mean('data', np.array([104,117,123])) # mean pixel
transformer.set_raw_scale('data',255) 
transformer.set_channel_swap('data',(2,1,0))
image_width = 300
image_height = 300
net.blobs['data'].reshape(1,3,image_height,image_width)
def get_labelname(labelmap, labels):
    num_labels = len(labelmap.item)
    labelnames = []
    if type(labels) is not list:
	labels =[labels]
    for label in labels:
    	found = False
        for i in xrange(0, num_labels):
            if label == labelmap.item[i].label:
                found = True
                labelnames.append(labelmap.item[i].display_name)
                break
        assert found == True
    return labelnames
 
im_names = list(os.walk(img_dir))[0][2]
for im_name in im_names:
    img_file = img_dir + im_name
    image = caffe.io.load_image(img_file)
    
    transformed_image = transformer.preprocess('data', image)
    net.blobs['data'].data[...] = transformed_image
    
    #t1 = timeit.Timer("net.forward()","from __main__ import net")
    #print t1.timeit(2)

    # Forward pass.
    detections = net.forward()['detection_out']
    
    # Parse the outputs.
    det_label = detections[0,0,:,1]
    det_conf = detections[0,0,:,2]
    det_xmin = detections[0,0,:,3]
    det_ymin = detections[0,0,:,4]
    det_xmax = detections[0,0,:,5]
    det_ymax = detections[0,0,:,6]

    # Get detections with confidence higher than 0.001
    top_indices = [i for i, conf in enumerate(det_conf) if conf >= 0.15]
    top_conf = det_conf[top_indices]
    top_label_indices = det_label[top_indices].tolist()
    top_labels = get_labelname(labelmap, top_label_indices)
    top_xmin = det_xmin[top_indices]
    top_ymin = det_ymin[top_indices]
    top_xmax = det_xmax[top_indices]
    top_ymax = det_ymax[top_indices]   

    #colors = plt.cm.hsv(np.linspace(0, 1, 21)).tolist()
 
    #img = Image.open(img_dir + "%06d.jpg"%(img_idx))
    img = Image.open(img_file)
    draw = ImageDraw.Draw(img)       
    for i in xrange(top_conf.shape[0]):
        xmin = top_xmin[i] * image.shape[1]
        ymin = top_ymin[i] * image.shape[0]
        xmax = top_xmax[i] * image.shape[1]
        ymax = top_ymax[i] * image.shape[0]
        
        h = float(ymax - ymin)
        w = float(xmax - xmin)
        #if (w==0) or (h==0):
        #   continue
        #if (h/w >=2)and((xmin<10)or(xmax > 1230)):
        #   continue
        
        score = top_conf[i]
        label_num = top_label_indices[i]
        if score > 0.3:
            draw.line(((xmin,ymin),(xmin,ymax),(xmax,ymax),(xmax,ymin),(xmin,ymin)),fill=(0,255,0))
            draw.text((xmin,ymin),'%s%.2f'%(top_labels[i], score),fill=(255,255,255))

    img.save(save_dir+im_name)  


