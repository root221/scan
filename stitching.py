import numpy as np
import cv2

def detectAndDescribe(image):

	gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
	
	detector = cv2.FeatureDetector_create("SIFT")
	kps = detector.detect(gray)

	extractor = cv2.DescriptorExtractor_create("SIFT")
	(kps, features) = extractor.compute(gray, kps)

	kps = np.float32([kp.pt for kp in kps])
 
 	return (kps, features)


def matchKeypoints(kps1, kps2, features1, features2,ratio, reprojThresh):
 
	matcher = cv2.DescriptorMatcher_create("BruteForce")
 	rawMatches = matcher.knnMatch(features1, features2, 2)
 	matches = []

 	for m in rawMatches:
 		if len(m) == 2 and m[0].distance < m[1].distance * ratio:
 			matches.append((m[0].trainIdx, m[0].queryIdx))

 	if len(matches) > 4:
	 	pts1 = np.float32([kps1[i] for (j,i) in matches])
	 	pts2 = np.float32([kps2[i] for (i,j) in matches])
 		
 		(H,status) = cv2.findHomography(pts1,pts2,cv2.RANSAC,reprojThresh)
 		return (matches,H,status)

 	return None

def exposureCompensation(img1,img2):
	Isum1 = 0.0
	Isum2 = 0.0



img1 = cv2.imread("fig2.jpg")
img2 = cv2.imread("fig1.jpg")

kps1,features1 = detectAndDescribe(img1)
kps2,features2 = detectAndDescribe(img2)

(matches,H,status) = matchKeypoints(kps1,kps2,features1,features2,0.75,4)
print(H)

result = cv2.warpPerspective(img1,H,(img1.shape[1],img1.shape[0]))

mask = np.zeros((result.shape[0],result.shape[1]),bool)

for i in range(result.shape[0]):
	for j in range(result.shape[1]):
		if result[i][j].all():
			mask[i][j] = True
		else:
			mask[i][j] = False
print mask.shape
print result.shape
cv2.imwrite("mask.jpg",mask)
#result = cv2.warpPerspective(img1, H,
#			(img1.shape[1] + img2.shape[1], img1.shape[0]))

#result[0:img2.shape[0], 0:img2.shape[1]] = img2
 
#result[] = img2

cv2.imwrite("result1.jpg",result)
