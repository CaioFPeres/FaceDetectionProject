# Face Detection Project
This is a face detection project made with Dlib in C++, along with pre processing scripts in python. The pre processing techniques were pretty basic, just resizing the face and centering it, as well as adding a black padding when the resulting centered image is smaller than the defined new size (images that would leave blank spaces, thus not fitting in the defined size). The pre processing techniques also updates the bounding boxes coordinates accordingly.

This project was done aiming Celeb Faces dataset (CelebA), but can be used to any object detection dataset, since it will just resize and crop based on the bounding box coordinates.

The preliminary results with just using the first 5000 processed images from CelebA were:

training results: 0.999171   0.9638 0.963757 

testing results:  0.998778 0.969925  0.96879 