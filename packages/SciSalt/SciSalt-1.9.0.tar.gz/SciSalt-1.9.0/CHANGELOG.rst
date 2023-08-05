Changelog
=========

1.7.1 (2015-11-24)
------------------

* Added git checking

1.7.0 (2015-11-24)
------------------

* Updates to ion modeling (2D, etc.)
* Updates to NonUniformImage, support code
* Add periodictable dependency
* Color updates
* Better piecewise function

1.6.0 (2015-08-31)
------------------

* Added ion modeling

1.5.0 (2015-08-31)
------------------

* Added personal ellipse fitting scisalt.scipy.hough_ellipse.
* Added an Imshow_Slider_Array for perusing an array of images.
* More config options for scisalt.logging.mylogger.
* Added gaussian function at scisalt.numpy.
* Behind-the-scenes updates and bug fixes.
* Progressbar now includes times, percentages.

1.4.4 (2015-08-10)
------------------

* Can now run githubtunnel from the command line

1.4.3 (2015-08-05)
------------------

* Fixed colorbar in scisalt.matplotlib.imshow
* Updated documentation with the start of a new manual

1.4.0 (2015-07-31)
------------------

scisalt.accelphys
^^^^^^^^^^^^^^^^^

* Moved findpinch to OneShot

scisalt.logging
^^^^^^^^^^^^^^^

* mylogger only uses console handlers if not given a filename

scisalt.matplotlib
^^^^^^^^^^^^^^^^^^

* Imshow_Slider

  * Now centers images within the axes automatically
  * Sliders now go down to zero
  * Image is now accessible as an attribute

* RectangleSelector

  * Can store its parent
  * Window is now settable progammatically

* imshow rescaling bug fixed
* plot added

scisalt.scipy
^^^^^^^^^^^^^

* Gauss fits are now accessed solely through GaussResults

scisalt.utils
^^^^^^^^^^^^^

* Methods *get*, *keys* added for making development with h5py easier

1.3.0 (2015-07-22)
------------------

scisalt.matplotlib
^^^^^^^^^^^^^^^^^^

* Added colorbar
* Added contour
* Added imshow
* Added quiver
* Added scaled_figsize
* Changed setup_figure: Supports *\*\*kwargs* pass-through to matplotlib.figure.Figure.

scisalt.utils
^^^^^^^^^^^^^

* Added progressbar

1.2.1 (2015-07-15)
------------------

* Documentation updates

1.2.0 (2015-07-15)
------------------

scisalt.matplotlib
^^^^^^^^^^^^^^^^^^

* Imshow_Slider

  * Renamed imshow_slider -> Imshow_Slider
  * Colorbar options added
  * Attribute *p* changed to *AxesImage*

* setup_figure

  * Changed arguments from *gridspec_(x/y)* to *rows* and *cols*
  * Added *figsize* control

* Added RectangleSelector
* Added setup_axes


1.1.1 (2015-07-12)
------------------

* First release on PyPI
