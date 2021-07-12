#### Download negative samples
```javascript
anthony@ghost ~/Documents/Python/Dogsitter/images/dataset $ python ../../src/flickr_image_search.py -q'boat' -c150 -d
Image(https://live.staticflickr.com/65535/51307863563_bce8b49465.jpg) sucessfully Downloaded.
Image(https://live.staticflickr.com/65535/51308387664_a749849401.jpg) sucessfully Downloaded.
Image(https://live.staticflickr.com/65535/51308671900_68f9598b25.jpg) sucessfully Downloaded.
...
...
...
anthony@ghost ~/Documents/Python/Dogsitter/images/dataset $
```

#### Run the downloaded images through the parser
```javascript
anthony@ghost ~/Documents/Python/Dogsitter/images/dataset $ python ../../src/image_parser.py -b'dog' -e'jpg' -p'/home/anthony/Documents/Python/Dogsitter/images/dataset/'
2021-07-12 19:30:32.980534: W tensorflow/stream_executor/platform/default/dso_loader.cc:60] Could not load dynamic library 'libcudart.so.11.0'; dlerror: libcudart.so.11.0: cannot open shared object file: No such file or directory; LD_LIBRARY_PATH: /usr/lib/python3.7/site-packages/cv2/../../../../lib64:
2021-07-12 19:30:32.980555: I tensorflow/stream_executor/cuda/cudart_stub.cc:29] Ignore above cudart dlerror if you do not have a GPU set up on your machine.
[INFO] Dog found in image: 51308263204_75a4d3595e.jpg
anthony@ghost ~/Documents/Python/Dogsitter/images/dataset $```

#### Check the image manually
```javascript
anthony@ghost ~/Documents/Python/Dogsitter/images/dataset $ feh 51308263204_75a4d3595e.jpg
anthony@ghost ~/Documents/Python/Dogsitter/images/dataset $ 
```

![51308263204_75a4d3595e.jpg](https://user-images.githubusercontent.com/2100258/125368473-4c2b7900-e348-11eb-8ba3-3ab2ee759755.jpg)


#### Move the images to the negatives folder
```javascript
anthony@ghost ~/Documents/Python/Dogsitter/images/dataset $ mv -i *.jpg negatives/
mv: overwrite 'negatives/51306448242_4b7e452e9c.jpg'? n
mv: overwrite 'negatives/51307501456_00b22713ea.jpg'? n
anthony@ghost ~/Documents/Python/Dogsitter/images/dataset $
```




