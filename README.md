# Face Detection Project
This is a CNN face detection project made with Dlib in C++, along with pre processing scripts in python. The pre processing techniques were pretty basic, just resizing the face and centering it, as well as adding a black padding when the resulting centered image is smaller than the defined new size (images that would leave blank spaces, thus not fitting in the defined size). The pre processing techniques also updates the bounding boxes coordinates accordingly.

After pre processing, the resulting training.xml would be too large for any common GPU to load it all. So, i created a script that would split the training into several xmls. You can execute it by passing how many images you would like for it to have in each xml training file. After that, you would have to configure your training program to be able to load an already trained model and continue its training. In my case, i loaded the model and overwrited the learning rate. That way, it would start at the beginning (0.1) and would try to learn something from the new training batch before deciding it can no longer learn and stop the model. On my tests, the heavy learning would happen on the first xml file, and then the next would help the model raise very small amounts of performance on each training (more or less 0.0016 of recall at each xml). So, on the first training batch, i achieved 0.998774 0.967155 0.966189, and on the eighth i got 0.999193 0.980214 0.98005 (Precision, Recall, Average Precision).
 
This project was done aiming Celeb Faces dataset (CelebA), but can be used to any object detection dataset, since it will just resize and crop based on the bounding box coordinates.

The preliminary results with just using the first 40000 processed images from CelebA (split into batches of 5000 images) were:

training results: 0.998364   0.9762 0.975864 

testing results:  0.999193 0.980214  0.98005