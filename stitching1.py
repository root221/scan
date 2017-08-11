import cv2
import numpy as np

files = ["50_9.jpg","60_9.jpg"]
#files1 = ["60_9.jpg","60_10.jpg","60_11.jpg"]
#files = ["result2.jpg","result1.jpg"]
MIN_MATCH_COUNT = 4



H_lst =[ 
[[  9.93693389e-01,  -1.41020251e-03,   1.98509022e+02],
 [  3.77828452e-03,   9.96561109e-01,   3.63943481e+00],
 [  9.16743487e-06,   3.36257675e-07,   1.00000000e+00]],
[[  1.00218468e+00,   3.57555698e-03,   3.89415254e+02],
 [  9.32819539e-03,   1.00220851e+00,   5.59373923e+00],
 [  2.51168566e-05,   6.23226680e-06,   1.00000000e+00]],
[[  9.91767706e-01,   1.04687533e-02,   5.84248309e+02],
 [  1.10888095e-02,   9.97858151e-01,   1.09348504e+01],
 [  2.95120139e-05,   1.43534827e-05,   1.00000000e+00]],
[[  9.79350147e-01,   1.05576063e-03,  7.76942039e+02],
 [  1.42763382e-02,   9.81230020e-01,  1.80020745e+01],
 [  3.62510474e-05,   6.38106937e-06,  1.00000000e+00]]
]

def drawMatch(img1,img2,kp1,kp2,good,mask,direction):
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

		cv2.imwrite("match.jpg",vis)

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
		cv2.imwrite("match.jpg",vis)

def blend(imgA,imgB):
	
	# generate Gaussian pyramid for A
	G = imgA.copy()
	gpA = [G]
	for i in range(5):
		G = cv2.pyrDown(G)
		gpA.append(G)

	# generate Gauessaion pyramid for B
	G = imgB.copy()
	gpB = [G]
	for i in range(5):
		G = cv2.pyrDown(G)
		gpB.append(G)

	# generate Laplacian Pyramid for A
	lpA = [gpA[5]]
	for i in range(5,0,-1):
		size = (gpA[i-1].shape[1],gpA[i-1].shape[0])
		G = cv2.pyrUp(gpA[i],dstsize = size)
		L = cv2.subtract(gpA[i-1],G)
		lpA.append(L)
	# generate Laplacian Pyramid for B
	lpB = [gpB[5]]
	for i in range(5,0,-1):
		size = (gpB[i-1].shape[1],gpB[i-1].shape[0])
		G = cv2.pyrUp(gpB[i],dstsize = size)
		L = cv2.subtract(gpB[i-1],G)
		lpB.append(L)

	# add left and right halves of images in each level
	LS = []
	for la,lb in zip(lpA,lpB):
		rows,cols,channel = la.shape
		l = np.hstack((la[:,0:cols/2],lb[:,cols/2:]))
		LS.append(l)

	# reconstruct
	l = LS[0]
	for i in range(1,6):
		size = (LS[i].shape[1],LS[i].shape[0])
		l = cv2.pyrUp(l,dstsize=size)
		l = cv2.add(l,LS[i])
	return l
# get detector and descriptor 

detector = cv2.FeatureDetector_create("SIFT")
extractor = cv2.DescriptorExtractor_create("SIFT")

imgs = []
for file in files:
	img = cv2.imread(file)
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
	direction = "horizontal"
	drawMatch(img1,img2,kp1,kp2,good,mask,direction)
	print(H)
	#H = np.array(H_lst[i])
	top_left = np.dot(H,np.array([0,0,1]))
	
	top_right = np.dot(H,np.array([img2.shape[1],0,1]))
	top_right = top_right / top_right[-1]

	bottom_left = np.dot(H,np.array([0,img2.shape[0],1]))
	bottom_left = bottom_left / bottom_left[-1]

	bottom_right = np.dot(H,np.array([img2.shape[1],img2.shape[0],1]))
	bottom_right = bottom_right / bottom_right[-1]

	print(top_right)
	print(top_left)
	print(bottom_right)
	print(bottom_left)
	
	# warp image left to right
	result = cv2.warpPerspective(img2,H,(int(min(bottom_right[0],top_right[0])),min(img1.shape[0],int(bottom_right[1]))))
	result[0:min(img1.shape[0],int(bottom_right[1])), 0:img1.shape[1]] = img1[0:min(img1.shape[0],int(bottom_right[1])),0:img1.shape[1]]
	# warp image top to bottom
	#bottom = min(bottom_right[1],bottom_left[1])
	#result = cv2.warpPerspective(img2,H,(int(bottom_right[0]),int(min(bottom_right[1],bottom_left[1]))))
	#result[0:img1.shape[0],:] = img1[:,0:int(bottom_right[0])]
	#imgs[i+1] = result


#result = imgs[len(imgs)-1]
cv2.imwrite("result3.jpg",result)


