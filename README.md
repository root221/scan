## Introduction
An scanner for laser engraver.

## Dependency
- pip install opencv
- pip install numpy
- pip install pyserial


## Usage
- generate file that contain homography list, use the function find_homography in Stitcher class (define in stitch.py)
- python main.py -o result.jpg -x data/H.p -y data/H1.p -b 115200 -p /dev/cu.wchusbserial1410
- -o output image filename
- -x the filename that contain horizontal homograpy list 
- -y the filename that contain vertical homograpy list 
- -p serial port
- -b baud rate
- open scan.html with browser
- click the scan button

## Example for generating homography list 
``` python

	from stitch import Stitcher	
	H_list = []
	stitcher = Stitcher()
	for i in range((len(img_list)-1)):
		img1 = img_list[i]
		img2 = img_list[i+1]
		H = stitcher.find_homography(img1,img2)
		H_list.append(H)
		img,offset = stitcher.stitch(img1,img2,"horizontal",H,blend=1)
		img_list[i+1] = img

	matrix_pickle = {}
	matrix_pickle["mtx"] = H_list
	pickle.dump( matrix_pickle, open( "H.p", "wb" ) )	
```
## Result

<center>
<caption>image without calibration</caption>
<img src="examples/stitch.jpg">
<br>
<caption>image after calibrate</caption>
<img src="examples/tree.jpg">
<br>
</center>

## WebSources for image stitching

- [1] http://www.pyimagesearch.com/2016/01/11/opencv-panorama-stitching/
- [2] http://matthewalunbrown.com/papers/ijcv2007.pdf

