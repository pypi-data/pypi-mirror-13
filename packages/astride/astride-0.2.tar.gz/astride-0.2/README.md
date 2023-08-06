# ASTRiDE (Automated Streak Detection for High Velocity Objects)

This package is the Python version of the streak detection pipeline
([Kim+ 2005](http://adsabs.harvard.edu/abs/2005JASS...22..385K) and 
[https://sites.google.com/site/dwkim78/streak-detection](https://sites.google.com/site/dwkim78/streak-detection))
originally programmed in C.

Basic idea is same with the C version, which uses a contour map of a fits image
to detect streaks. Nevertheless, the Python version has an improved algorithm
to determine whether each edge (i.e. each contour) 
in the contour map is a streak or not
For details, see the section "[How to Use ASTRiDE](#4-how-to-use-astride)". 

## Index
1. [Dependency](#1-dependency)
2. [Installation](#2-installation)
3. [Test the Installation](#3-test)
4. [How to Use ASTRiDE](#4-how-to-use-astride)
5. [Test with Crowded Field Image](#5-test-with-crowded-field-image)

- [ChangeLog](#changelog)
- [Citation](#citation)

## 1. Dependency

[Python 2.7+](https://www.python.org/) 

 * Not tested with Python 3.0+

[Numpy 1.9+](http://www.numpy.org/)
 
 * Numerical Python library.

[Scikit-image 0.11.3+](http://scikit-image.org/)
 
 * To get contour map of a fits image.

[Astropy 1.1.1+](http://www.astropy.org/)

 * For reading fits file and some utility functions.

[Matplotlib 1.5.1+](http://matplotlib.org/)

 * For plotting figures of detected streaks.

[Phoutils 0.2.1+](http://photutils.readthedocs.org/en/latest/index.html)

 * For calculating background map of a fits image.

## 2. Installation

The easiest way to install the ASTRiDE package is:

```python
pip install astride
```

Or,

```python
pip install git+https://github.com/dwkim78/ASTRiDE
```

If you do not want to install/upgrade the dependencies,
execute the above commend with the ```--no-deps``` option.
ASTRiDE possibly works with older version of Python and other libraries. 


Alternatively, you can download the ASTRiDE package from the Git repository as:

```python
git clone https://github.com/dwkim78/ASTRiDE

cd ASTRiDE
python setup.py install
```

You can edit ```setup.py```, if you do not want to update 
your own Python libraries (i.e. edit the ```install_requires``` variable).


## 3. Test

To check if ASTRiDE is correctly installed, type following commands in 
your Python console.

```python
from astride import test

test()
```

The command will print messages like:
```
2016-02-15 16:16:18,239 INFO - Start.
2016-02-15 16:16:18,241 INFO - Read a fits file..
2016-02-15 16:16:18,272 INFO - Search streaks..
2016-02-15 16:16:19,027 INFO - Save figures and write outputs to ./long/
2016-02-15 16:16:20,048 INFO - Done.
```

The test module will also save figures and write information of detected 
streaks under the "./long/" folder. In the folder, you can find two images
and one text file. The two images are:

| Image name | Description |
|----:|:------------|
| all.png |  An entire fit image with detected streak (shown below) |
| 1.png | A zoomed image for each linked streak |

<div align="center">
<img src="https://github.com/dwkim78/ASTRiDE/blob/master/astride/datasets/images/all.png">
[ all.png ]</div>


The output text file named as "streaks.txt" contains following information.

| Column | Description |
|----:|:------------|
| ID  | Index |
| x_center, y_center  | Coordinate of the center  |
| area  | Area inside a streak  |
| perimeter  | Length of perimeter of a streak  |
| shape_factor  | 4 * PI * 'area' / 'perimeter'^2 |
| radius_deviation  | Parameter to check roundness  |
| slope  | Slope of a linear line fitted to a streak  |
| intercept  | Intercept of a linear line fitted to a streak  |
| connectivity  | ID of another streak that is likely to be linked to the current streak  |


## 4. How to Use ASTRiDE? 

In this section, I will show how to use ASTRiDE to detect streaks. I will use
the fits image shown in the previous section.

### Create Streak Instance

We first need to create ASTRiDE Streak instance as:

```python
from astride import Streak

streak = Streak('long.fits')
```

You can replace "long.fits" with your own fits filename. There are many options customizing the Streak instance such as:

| Options | Description |
|----:|:------------|
| bkg_box_size  | A box size for calculating a background map of a fits image |
| contour_threshold  | A threshold to extract a contour map |
| min_points  | The minimum number of data points in each contour in the contour map
| shape_cut  | An empirical cut for shape factor |
| area_cut | An empirical cut for area inside each contour |
| radius_dev_cut  | An empirical cut for radius deviation |
| connectivity_angle | The maximum angle to link each edge (i.e. each contour) |
| output_path  | An output path to save figures and outputs |

Although you can customize pretty much everything of the Streak instance, 
I recommend to leave them as they are.
Hereinafter, the term "edge" means each contour from the contour map derived
from a fits image.

### Detect Streaks

We can now detect streaks in the fits image as:

```python

streak.detect()
```

In order to detect streaks, the Streak instance does as follows:

  1. Background removal
    * We first remove background from the fits image. The background map
    is derived using [Phoutils](http://photutils.readthedocs.org/en/latest/index.html).
    It calculates the map by sigma-clipping method within the box of the
    size "bkg_box_size". 
  
  2. Contour map
    * Using the [scikit-image](http://scikit-image.org/), we derive
    the contour map of the fits image. The level of the contour
    is controlled by the "contour_threshold" value, such as:
    contour_threshold * background standard deviation (calculated
    when deriving the background map). Default "contour_threshold" is 3.
    The following images shows all the edges detected using the contour map.
    
<div align="center">
<img src="https://github.com/dwkim78/ASTRiDE/blob/master/astride/datasets/images/all_edges.png">
[ All the edges (color-coded) derived using the contour map ]</div>
  
  3. Streak detection based on the morphologies of each contour (i.e. edge)
    * As you can see from the above figure, there are many edges of 
    star-like sources that are definitely <b>not</b> streaks. We remove such
    star-like sources by using the morphologies of each edge such as:
    
| Morphology | Description |
|----:|:------------|
| Shape Factor | [Circularity](https://goo.gl/Z0Jy9z). The circularity of a circle is 1, and streak-like shape has much smaller circularity than 1. We set 0.2 as a threshold (i.e. option "shape_cut") |
| Radius Deviation | An approximated deviation from roundness. Since we know the center of each edge, we can calculate distances to each data point from the center. We define a radius as the median value of the distances. We then calculate (the standard deviation of distances - radius) / radius. We set 0.5 as a threshold (i.e. option "radius_dev_cut"). |
| Area | The area must larger than 10 pixels (i.e. option "area_cut"). |

The following figure shows the remaining two streak after these cut.
 
<div align="center">
<img src="https://github.com/dwkim78/ASTRiDE/blob/master/astride/datasets/images/two_streaks.png">
[ Two streaks after the morphology cut. The numbers are their IDs. ]</div>
  
  4. Link streaks by their slopes
    * We finally detected two streaks. However, as you can see, these two
    streaks are not really separated two streaks. They seems to be
    one streak, but separately detected since the middle part of
    the streak is disconnected. This could happen for fast moving objects.
    We connect (i.e. link) such streaks by their slope derived from a
    linear line fitting. If their slopes are within the "connectivity_angle",
    and also the slope between the two centers of the two streaks are within
    the "connectivity_angle" with each streak, we then
    determine that the two streaks are connected. This is why
    the "all.png" shown in the [section "Test"](#3-test)
    has only one red dashed-line box around the two streaks. 
    If one streak (i.e. s1) is determined to be linked
    with another streak (i.e. s2), s1's "connectivity" value is the index
    of s2. If s2 is again linked with s3, then again s2's "connectivity"
    is the index of s3. If s3 is not linked with any other streaks,
    s3's "connectivity" is -1.
     
     
Note that all these information are accessible using the Streak instance 
(See [this section](#accessible-information-inside-the-streak-instance).)

### Plot Figures and Write Outputs
    
We provide modules to plot figures and write outputs as:

```python
streak.plot_figures()

streak.write_outputs()
```

This will generate figures including "all.png", and an individual
figure for each linked streak. A Filename of each individual file
is the first index among the indices of the linked streak such as "1.png"
shown below.

<div align="center">
<img src="https://github.com/dwkim78/ASTRiDE/blob/master/astride/datasets/images/1.png"></div>

The command shown above will also write an output text file, "streaks.txt"
containing many values of each streak.


### Accessible Information Inside the Streak Instance

The streak instance also contains many information derived during the 
detection processes such as:

| Variable | Description |
|----:|:------------|
| streak.raw_image | Raw fit image before background removal |
| streak.background_map | Derived background map |
| streak.image | Background removed image |
| streak.raw_edges | All the edges detected using a contour map |
| streak.streaks | The final list of streaks |


Among these, ```streak.streaks``` contains a list of detected streaks. 
Each element has all the information that "streaks.txt" has. 
It also contains additional information such as:

| Variable | Description |
|----:|:------------|
| x | X coordinates of a streak |
| y | Y coordinates of a streak |
| x_min and x_max | The minimum and maximum x coordinates of a streak |
| y_min and y_max | The minimum and maximum y coordinates of a streak |

Using the above information, you can make your own figures if needed.


### 5. Test with Crowded Field Image

The example shown above used less crowded field image. The following images
show the results using more crowded field image.
 
 <div align="center">
<img src="https://github.com/dwkim78/ASTRiDE/blob/master/astride/datasets/images/crowded_field.png">
[ Streak detection test using the crowded field image ]</div>

As you can see, ASTRiDE successfully excluded all the stars and 
detected two very short streaks that are quite hard to be detected even by
visual examination.


### Note

As you might notice, ASTRiDE does
not use any source detection algorithm (e.g. Source Extractor) to distinguish
stars from streaks. This is because such algorithms often find stellar-like-sources
<b>inside</b> a streak. For instance, see the following figure.

<div align="center">
<img src="https://github.com/dwkim78/ASTRiDE/blob/master/astride/datasets/images/source_detection.png">
[ Source Detection ]</div>

Thus we cannot use such source detection algorithms to remove stars before 
detecting streaks. One could think of using each detected source to
detect streaks by somehow connecting them. Such method, however, would not
be successful either for 1) short streaks, or 2) crowded field.


### Logger

If you want to write log messages either to console or to disk, 
you can use the ASTRiDE Logger class as:

```python
from astride import Logger

logger = Logger().getLogger()

logger.debug('debug message')
logger.info('info message')
logger.warn('warn message')
logger.error('error message')
logger.critical('critical message')
```

Keep in mind that you need to generate only one logger instance 
through the whole processes, but not many.
If you want to save log messages to a file, 
generate a logger instance as follows:
 
 ```python
 logger = Logger('/PATH/TO/FILE.log').getLogger()
 ```

This will send log messages to both console and a log file.
Note that the path must be the absolute path.

## ChangeLog

### v0.2
 - Beta version released. 

### v0.1
 - initiate the GitHub repository.

## Citation