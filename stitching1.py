import cv2
import numpy as np

files = ["1Hill.JPG","2Hill.JPG","3Hill.JPG"]
MIN_MATCH_COUNT = 4

def drawMatch(img1,img2,kp1,kp2,good,mask):
	w = img1.shape[1] 
	vis = np.zeros((max(img1.shape[0],img2.shape[0]),img1.shape[1] + img2.shape[1],3),dtype="uint8") 
	vis[0:img1.shape[0],0:img1.shape[1],:] = img1
	vis[0:img2.shape[0],img1.shape[1]:] = img2
	

	for (m,s) in zip(good,mask):
		if s:
			pt1 = (int(kp1[m.queryIdx].pt[0]),int(kp1[m.queryIdx].pt[1]))
			pt2 = (int(kp2[m.trainIdx].pt[0]+w),int(kp2[m.trainIdx].pt[1]))
			cv2.line(vis, pt1, pt2, (0, 255, 0), 1)

	cv2.imwrite("match2.jpg",vis)
# get detector and descriptor 

detector = cv2.FeatureDetector_create("SIFT")
extractor = cv2.DescriptorExtractor_create("SIFT")

imgs = []
for file in files:
	img = cv2.imread(file)
	print(img.shape)
	imgs.append(img)


for i in range(len(imgs)-1):
	
	img1 = imgs[i]
	gray = cv2.cvtColor(img1,cv2.COLOR_BGR2GRAY)
	
	# finds the keypoint in the image
	kps = detector.detect(gray)
	
	# get descriptor
	(kp1,des1) = extractor.compute(gray,kps)
	
	img2 = imgs[i+1]
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
		if m.distance < 0.75*n.distance:
			good.append(m)

	print(len(good))
	if len(good) > MIN_MATCH_COUNT:

		src_pts = np.float32([ kp2[m.trainIdx].pt for m in good]).reshape(-1,1,2)
		dst_pts = np.float32([ kp1[m.queryIdx].pt for m in good ]).reshape(-1,1,2)
		
		H,mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC,5.0)
	drawMatch(img1,img2,kp1,kp2,good,mask)
	# warp image
	start = np.dot(H,np.array([0,0,1]))
	up = np.dot(H,np.array([img2.shape[1],0,1]))
	up = up / up[-1]
	end = np.dot(H,np.array([img2.shape[1],img2.shape[0],1]))
	end = end / end[-1]
	print(start)
	print(up)
	print(end)
	#result = cv2.warpPerspective(img2,H,())
	result = cv2.warpPerspective(img2,H,(int(min(end[0],up[0])),int(end[1])))
	print(result.shape)
	result[0:int(end[1]), 0:img1.shape[1]] = img1[0:int(end[1]),0:img1.shape[1]]
	img2 = img1[0:int(end[1]),0:img1.shape[1]]
	cv2.imwrite("result1.jpg",result)
	print(img2.shape)
	imgs[i+1] = result
'''
result = np.zeros((imgs[0].shape[0],3000,3),dtype="uint8")
print(result.shape)
result[:,0:400] = imgs[0]
result[:,400:700] = imgs[1]
'''
result = imgs[2]
cv2.imwrite("result1.jpg",result)


