# DogSitter

[ **OVERVIEW** ]

This app was made to record my neighbor's dogs while their dogs are shitting while walking their dogs. This is achieved by using OpenCV and Tensorflow on a Raspberry Pi cluster. 

I have four overclocked Raspberry Pi's that all run Gentoo Linux. Three of these Pi's are 4b's and one is a 3b which will eventually be swapped out for another 4b.

[ **HOW IT WORKS** ]
 
The main Raspberry Pi 4b is overclocked @ 2Ghz and runs the motiondetection software. Once motion is detected then pictures are taken and ran through Tensorflow's common object detection method to recognize a dog and person together. Once this is done then i came each frame to a custom base cascade classifier template that i made with the help of imagenet. 

Once a dog is detected in the shitting position, the system starts taking pictures for 120 seconds. This is where the cluster comes in. They each have their own tasks while collectively performing a single task.

The single collective task is to process 3 images at a time. Will finish at a later time.
