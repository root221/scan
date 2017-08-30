## Introduction
An scanner for laser engraver.

## Dependency
- pip install opencv
- pip install numpy
- pip install pyserial


## Usage
- generate file that contain homography list use the function find_homography in Stitcher class(define in stitch.py)
- python main.py -o result.jpg -x data/H.p -y data/H1.p -b 115200 -p /dev/cu.wchusbserial1410
- -o output image filename
- -x the filename that contain horizontal homograpy list 
- -y the filename that contain vertical homograpy list 
- -p serial port
- -b baud rate
- open scan.html with browser
- click the scan button



## Result

<center>
<caption>image without calibration</caption>
<img src="examples/stitch.jpg">
<br>
<caption>image after calibrate</caption>
<img src="examples/tree.jpg">
<br>
</center>
