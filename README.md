# DogSitter

[ **OVERVIEW** ]

This app was made to record my neighbor's dogs while their dogs are shitting when out walking their dogs. This is achieved by using OpenCV and Tensorflow on a Raspberry Pi cluster. 

I have four overclocked Raspberry Pi's that all run Gentoo Linux. Three of these Pi's are 4b's and one is a 3b which will eventually be swapped out for another 4b.

[ **HOW IT WORKS** ]
 
The main Raspberry Pi 4b is overclocked @ 2Ghz and runs the motiondetection software. Once motion is detected then pictures are taken and ran through Tensorflow's common object detection method to recognize a dog and person together. Once this is done then i came each frame to a custom base cascade classifier template that i made with the help of imagenet. 

Once a dog is detected in the shitting position, the system starts taking pictures for 120 seconds. This is where the cluster comes in. They each have their own tasks while collectively performing a single task.

The single collective task is to process 3 images at a time. Will finish at a later time.


#### Compiling OpenCV from source
```javascript
cmake -DCMAKE_EXE_LINKER_FLAGS=-lcblas -DCMAKE_BUILD_TYPE=RELEASE -DCMAKE_INSTALL_PREFIX=/usr/local -DOPENCV_GENERATE_PKGCONFIG=ON -DBUILD_EXAMPLES=OFF -DWITH_EIGEN=ON -DWITH_FFMPEG=ON -DWITH_GSTREAMER=ON -DWITH_GTK=ON -DWITH_JPEG=ON -DWITH_LAPACK=OFF -DWITH_OPENMP=ON -DWITH_PNG=ON -DINSTALL_PYTHON_EXAMPLES=OFF -DINSTALL_C_EXAMPLES=OFF -DWITH_V4L=ON -DWITH_VTK=OFF -DWITH_CUDA=OFF -DWITH_CUBLAS=OFF -DOPENCV_EXTRA_MODULES_PATH='/home/anthony/Documents/Source/opencv-3.4.14/opencv_contrib/modules' ..
```

#### create vec file
```javascript
/usr/local/bin/opencv_createsamples -info info.dat -num 10 -bg bg.txt -vec samples_out.vec -show
```
