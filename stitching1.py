import cv2
import numpy as np
files = ["fig3.jpg","fig2.jpg"]
MIN_MATCH_COUNT = 4
# get keypoint and descriptor for each image
lst = []
detector = cv2.FeatureDetector_create("SIFT")
extractor = cv2.DescriptorExtractor_create("SIFT")
for file in files:
	img = cv2.imread(file)
	gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
	
	# finds the keypoint in the image
	kps = detector.detect(gray)
	
	# get descriptor
	(kps,des) = extractor.compute(gray,kps)
	
	lst.append((img,kps,des))

for i in range(len(lst)-1):
	
	kp1 = lst[i][1]
	kp2 = lst[i+1][1]
	des1 = lst[i][2]
	des2 = lst[i+1][2]

	# match key point
	bf = cv2.BFMatcher()
	matches = bf.knnMatch(des1,des2, k=2)
	# Apply ration test
	good = []
	for m,n in matches:
		if m.distance < 0.75*n.distance:
			good.append(m)


	if len(good) > MIN_MATCH_COUNT:
		src_pts = np.float32([ kp1[m.queryIdx].pt for m in good ]).reshape(-1,1,2)
		dst_pts = np.float32([ kp2[m.trainIdx].pt for m in good ]).reshape(-1,1,2)

		#dst_pts = np.float32([ kp2[m.trainIdx].pt for m in good ]).reshape(-1,1,2)
		H,mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC,5.0)


	# warp image
	result = cv2.warpPerspective(lst[i][0],H,(1000,1000))
	img2 = lst[i+1][0]
	result[0:img2.shape[0], 0:img2.shape[1]] = img2
	cv2.imwrite("result.jpg",result)