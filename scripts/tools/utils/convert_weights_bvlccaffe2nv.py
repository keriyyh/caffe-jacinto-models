#import numpy as np
#import matplotlib.pyplot as plt
#matplotlib inline

################################################################
# Make sure that caffe is on the python path:
caffe_root = '../../caffe-jacinto/'  # caffe is expected to be in this folder

import sys
import os

sys.path.insert(0, caffe_root + 'python')
import caffe

# Load the net, list its data and params, and filter an example image.
caffe.set_mode_cpu()
print ("Afr setting cpu mode for caffe-bvlc")

#nvidia-cafe (0.16) fused bn style model
model_bvlc = '/user/a0132471/Files/caffe-jacinto-models/scripts/training/Manu_training/imagenet_mobilenetv2-1.0_2018-06-06_17-18-39_bvlcbn/initial/deploy.prototxt'
weights_bvlc = '/user/a0132471/Files/caffe-jacinto-models/scripts/tools/utils/MobileNetV2_new_names.caffemodel'

#bvlc bn style (scale seperate) model
model_nv = '/user/a0132471/Files/caffe-jacinto-models/scripts/training/Manu_training/imagenet_mobilenetv2-1.0_2018-06-06_17-14-41_fusedbn/initial/deploy.prototxt'
weights_nv = 'MobileNetV2_new_NV_fused_bn.caffemodel'


################################################################

#load nvidia train model (weigths for all layers except BN will be loaded)
net_nv = caffe.Net(model_nv, weights = None,phase = caffe.TEST)
#print("net_nv: blobs {}\nparams {}".format(net.blobs.keys()[0:20], net.params.keys()[0:10]))
print("net_nv: num_keys: ", len(net_nv.params.keys()))

#load bvlc train model (weigths for all layers except BN will be loaded)
net_bvlc = caffe.Net(model_bvlc, weights = weights_bvlc, phase = caffe.TEST)

#print("net_bvlc: blobs {}\nparams {}".format(net.blobs.keys()[0:20], net.params.keys()[0:10]))
print("bvlc_nv: num_keys: ", len(net_bvlc.params.keys()))

############################################################
#Process BVLC BN layers
############################################################
bn_keys_set = (key for key in net_nv.params.keys())
for key_name in bn_keys_set:
  len_key_name = len(net_nv.params[key_name])
  print("key_name", key_name)
  if ("/bn" in key_name) and (len_key_name>3): 
    key_name_scale = key_name.replace("/bn", "/scale")
    if len(net_nv.params[key_name][0].data.shape) > len(net_bvlc.params[key_name][0].data.shape):
      net_nv.params[key_name][0].data[:,0,0] = net_bvlc.params[key_name][0].data[...]
      net_nv.params[key_name][1].data[:,0,0] = net_bvlc.params[key_name][1].data[...]
      net_nv.params[key_name][2].data[...] = net_bvlc.params[key_name][2].data[...]
      net_nv.params[key_name][3].data[:,0,0] = net_bvlc.params[key_name_scale][0].data[...] 
      net_nv.params[key_name][4].data[:,0,0] = net_bvlc.params[key_name_scale][1].data[...]   
    else:
      net_nv.params[key_name][0].data[...] = net_bvlc.params[key_name][0].data[...]  
      net_nv.params[key_name][1].data[...] = net_bvlc.params[key_name][1].data[...] 
      net_nv.params[key_name][2].data[...] = net_bvlc.params[key_name][2].data[...] 
      net_nv.params[key_name][3].data[...] = net_bvlc.params[key_name_scale][0].data[...] 
      net_nv.params[key_name][4].data[...] = net_bvlc.params[key_name_scale][1].data[...]                 
  else:
    for index in range(0,len_key_name):
      net_nv.params[key_name][index].data[...] = net_bvlc.params[key_name][index].data[...]
    
net_nv.save(weights_nv)

