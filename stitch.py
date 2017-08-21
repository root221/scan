import cv2
import numpy as np
import pickle
#from find import find
with (open("H.p","rb")) as f:
	H_horizontal_lst = pickle.load(f)["mtx"]

with(open("H1.p","rb")) as f:
	H_vertical_lst = pickle.load(f)["mtx"]

spe = [[  1.06321908e+00,  -1.54612823e-01,  -1.40087576e+02],
 [ -9.24776307e-02,   8.28748688e-01,   2.71126949e+03],
 [  1.36635956e-05,  -7.26914683e-05,   1.00000000e+00]]

spe = np.array(spe)

img_width = 2385
img_height = 568

def stitch(imgs,direction,x,y):
	
	img1 = imgs[0]
	img2 = imgs[1]
	cv2.imwrite("img1.jpg",img1)
	cv2.imwrite("img2.jpg",img2)
	if(direction == "horizontal"):
		H = np.array(H_horizontal_lst[x])
	else:
		
		if(y == 100):
			H = spe
		#H = find(imgs)
		else:
			if(y > 12):
				y = y - 14
			H = np.array(H_vertical_lst[y])
	top_left = np.dot(H,np.array([0,0,1]))
		
	top_right = np.dot(H,np.array([img2.shape[1],0,1]))
	top_right = top_right / top_right[-1]

	bottom_left = np.dot(H,np.array([0,img2.shape[0],1]))
	bottom_left = bottom_left / bottom_left[-1]

	bottom_right = np.dot(H,np.array([img2.shape[1],img2.shape[0],1]))
	bottom_right = bottom_right / bottom_right[-1]

	if(direction == "horizontal"):
		
		# warp image left to right
		height = int(min(bottom_right[1],bottom_left[1]))
		result = cv2.warpPerspective(img2,H,(int(min(bottom_right[0],top_right[0])),height ))
		offset_y = int(max(top_right[1],top_left[1]))
			
		# get two overlap subimages
		overlap_left = int(max(top_left[0],bottom_left[0]))
		overlap_right = img1.shape[1]

		# height - 1 ???
		subimg2 = result[offset_y:height-1,overlap_left:overlap_right].copy()
		subimg1 = img1[offset_y:height-1,overlap_left:overlap_right].copy()
		
		# alpha blending two overlap image
		overlap_width = overlap_right - overlap_left
		dst = subimg2.copy()
		for j in range(10):
			alpha = j * 0.1
			a = subimg1[:,(j * overlap_width/10) : ((j+1) * overlap_width/10)]
			b = subimg2[:,(j * overlap_width/10) : ((j+1) * overlap_width/10)]
			dst[:,(j * overlap_width/10) : ((j+1) * overlap_width/10)] = cv2.addWeighted(a,1-alpha,b,alpha,0)
		min_height = min(result.shape[0],img1.shape[0])
		result[0:min_height, 0:img1.shape[1]] = img1[0:min_height,0:img1.shape[1]]
		result[offset_y:height-1,overlap_left:overlap_right] = dst

	else:
		# warp image top to bottom	
		bottom = int(min(bottom_right[1],bottom_left[1]))
		result = cv2.warpPerspective(img2,H,(img1.shape[1],bottom))
				
		# get two overlap subimages
		overlap_top = int(max(top_right[1],top_left[1]))
		overlap_bottom = img1.shape[0] 
		subimg2 = result[overlap_top:overlap_bottom,0:img2.shape[1]].copy()
		subimg1 = img1[overlap_top:overlap_bottom,0:img2.shape[1]].copy()

		# alpha blending two overlap image	
		overlap_height = overlap_bottom - overlap_top
		delta = overlap_height / 10
		dst = subimg2.copy()
		for j in range(10):
			alpha = j * 0.1
			a = subimg1[ j * delta : (j+1) * delta,:] 
			b = subimg2[ j * delta : (j+1) * delta,:]
			dst[j * delta : (j+1) * delta,:] = cv2.addWeighted(a,1-alpha,b,alpha,0)
		# paste img1 to result image
		result[0:img1.shape[0], 0:img1.shape[1]] = img1[0:img1.shape[0],0:img1.shape[1]]
		# paste overlap(blend) region to result image
		result[overlap_top:overlap_bottom,0:img2.shape[1]] = dst
		offset_y = 0
	cv2.imwrite("result.jpg",result)
	
	return (result,offset_y)