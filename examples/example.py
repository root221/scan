import cv2
from stitch import Stitcher

files = ["Hill1.jpg","Hill2.jpg","Hill3.jpg"]

imgs = []
for filename in files:
	img = cv2.imread(filename)
	imgs.append(img)
imgs = [imgs]

stitcher = Stitcher(imgs)
result = stitcher.stitch_all_images()
cv2.imwrite("result.jpg",result)