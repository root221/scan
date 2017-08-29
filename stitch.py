import cv2
import numpy as np
import pickle

MIN_MATCH_COUNT = 200

class Stitcher:
	
	def __init__(self,img_list=None,H_lst=None):
		self.img_list = img_list
		self.H_lst = H_lst

	def stitch_all_images(self):

		if len(self.img_list) == 1:
			for i in range(len(self.img_list[0])-1):
				img1 = self.img_list[0][i]
				img2 = self.img_list[0][i+1]
				if not self.H_lst:
					H = self.find_homography(img1,img2)
				else:
					H = self.H_lst[0][i]
				(result,offsety) = self.stitch(img1,img2,"horizontal",H)
				self.img_list[0][i+1] = result

		
		return self.img_list[len(self.img_list)-1][len(self.img_list[0])-1]

	def stitch(self,img1,img2,direction,H,blend=1):
		
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
			if offset_y < 0:
				offset_y = 0
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
				dst[:,(j * overlap_width/10) : ((j+1) * overlap_width/10)] = cv2.addWeighted(a,1 - alpha,b,alpha,0)
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
				dst[j * delta : (j+1) * delta,:] = cv2.addWeighted(a,1 - alpha,b,alpha,0)
				#dst[j * delta : (j+1) * delta,:] = cv2.addWeighted(a,1 ,b,0,0)

			# paste img1 to result image
			result[0:img1.shape[0], 0:img1.shape[1]] = img1[0:img1.shape[0],0:img1.shape[1]]
			# paste overlap(blend) region to result image
			result[overlap_top:overlap_bottom,0:img2.shape[1]] = dst
			offset_y = 0
		
		return (result,offset_y)


	def find_homography(self,img1,img2):
		
		# get detector and descriptor 
		detector = cv2.FeatureDetector_create("SIFT")
		extractor = cv2.DescriptorExtractor_create("SIFT")

		gray = cv2.cvtColor(img1,cv2.COLOR_BGR2GRAY)
		
		# finds the keypoint in the image
		kps = detector.detect(gray)
			
		(kp1,des1) = extractor.compute(gray,kps)
		
		gray = cv2.cvtColor(img2,cv2.COLOR_BGR2GRAY)
		
		# finds the keypoint in the image
		kps = detector.detect(gray)
		
		(kp2,des2) = extractor.compute(gray,kps)

		# match key point
		bf = cv2.BFMatcher()
		matches = bf.knnMatch(des1,des2, k=2)

		
		# Apply ration test
		good = []
		for m,n in matches:
			if m.distance < 0.8*n.distance:
				good.append(m)
		
		if len(good) > MIN_MATCH_COUNT:
			src_pts = np.float32([ kp2[m.trainIdx].pt for m in good]).reshape(-1,1,2)
			dst_pts = np.float32([ kp1[m.queryIdx].pt for m in good ]).reshape(-1,1,2)
			H,mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC,5.0)
		
		return H


	def drawMatch(self,img1,img2,kp1,kp2,good,mask,direction,filename):
		if(direction == "horizontal"):
			w = img1.shape[1] 
			vis = np.zeros((max(img1.shape[0],img2.shape[0]),img1.shape[1] + img2.shape[1],3),dtype="uint8") 
			vis[0:img1.shape[0],0:img1.shape[1],:] = img1
			vis[0:img2.shape[0],img1.shape[1]:] = img2
			

			for (m,s) in zip(good,mask):
				if s:
					pt1 = (int(kp1[m.queryIdx].pt[0]),int(kp1[m.queryIdx].pt[1]))
					pt2 = (int(kp2[m.trainIdx].pt[0]+w),int(kp2[m.trainIdx].pt[1]))
					cv2.line(vis, pt1, pt2, (0, 255, 0), 1)

		else:
			h = img1.shape[0]
			vis = np.zeros((img1.shape[0] + img2.shape[0],max(img1.shape[1],img2.shape[1]),3) ,dtype="uint8")
			vis[0:img1.shape[0],0:img1.shape[1]] = img1
			vis[img1.shape[0]:,0:img2.shape[1]] = img2
			for (m,s) in zip(good,mask):
				if s:
					pt1 = (int(kp1[m.queryIdx].pt[0]), int(kp1[m.queryIdx].pt[1]))
					pt2 = (int(kp2[m.trainIdx].pt[0]), int(kp2[m.trainIdx].pt[1])+h)
					cv2.line(vis,pt1,pt2,(0,255,0),1)
		
		cv2.imwrite(filename,vis)
	 

