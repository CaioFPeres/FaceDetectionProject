// The contents of this file are in the public domain. See LICENSE_FOR_EXAMPLE_PROGRAMS.txt
/*
    This example shows how to train a CNN based object detector using dlib's 
    loss_mmod loss layer.  This loss layer implements the Max-Margin Object
    Detection loss as described in the paper:
        Max-Margin Object Detection by Davis E. King (http://arxiv.org/abs/1502.00046).
    This is the same loss used by the popular SVM+HOG object detector in dlib
    (see fhog_object_detector_ex.cpp) except here we replace the HOG features
    with a CNN and train the entire detector end-to-end.  This allows us to make
    much more powerful detectors.

    It would be a good idea to become familiar with dlib's DNN tooling before
    reading this example.  So you should read dnn_introduction_ex.cpp and
    dnn_introduction2_ex.cpp before reading this example program.
    
    Just like in the fhog_object_detector_ex.cpp example, we are going to train
    a simple face detector based on the very small training dataset in the
    examples/faces folder.  As we will see, even with this small dataset the
    MMOD method is able to make a working face detector.  However, for real
    applications you should train with more data for an even better result.
*/


#include <iostream>
#include <dlib/dnn.h>
#include <dlib/data_io.h>
#include <dlib/gui_widgets.h>

using namespace std;
using namespace dlib;

// The first thing we do is define our CNN.  The CNN is going to be evaluated
// convolutionally over an entire image pyramid.  Think of it like a normal
// sliding window classifier.  This means you need to define a CNN that can look
// at some part of an image and decide if it is an object of interest.  In this
// example I've defined a CNN with a receptive field of approximately 50x50
// pixels.  This is reasonable for face detection since you can clearly tell if
// a 50x50 image contains a face.  Other applications may benefit from CNNs with
// different architectures.  
// 
// In this example our CNN begins with 3 downsampling layers.  These layers will
// reduce the size of the image by 8x and output a feature map with
// 32 dimensions.  Then we will pass that through 4 more convolutional layers to
// get the final output of the network.  The last layer has only 1 channel and
// the values in that last channel are large when the network thinks it has
// found an object at a particular location.


// Let's begin the network definition by creating some network blocks.
/*
// A 5x5 conv layer that does 2x downsampling
template <long num_filters, typename SUBNET> using con5d = con<num_filters,5,5,2,2,SUBNET>;
// A 3x3 conv layer that doesn't do any downsampling
template <long num_filters, typename SUBNET> using con3  = con<num_filters,3,3,1,1,SUBNET>;

// Now we can define the 8x downsampling block in terms of conv5d blocks.  We
// also use relu and batch normalization in the standard way.
template <typename SUBNET> using downsampler  = relu<bn_con<con5d<32, relu<bn_con<con5d<32, relu<bn_con<con5d<32,SUBNET>>>>>>>>>;

// The rest of the network will be 3x3 conv layers with batch normalization and
// relu.  So we define the 3x3 block we will use here.
template <typename SUBNET> using rcon3  = relu<bn_con<con3<32,SUBNET>>>;

// Finally, we define the entire network.   The special input_rgb_image_pyramid
// layer causes the network to operate over a spatial pyramid, making the detector
// scale invariant.  
using net_type  = loss_mmod<con<1,6,6,1,1,rcon3<rcon3<rcon3<downsampler<input_rgb_image_pyramid<pyramid_down<6>>>>>>>>;
*/

// replacing all affine by bn_con

template <long num_filters, typename SUBNET> using con5d = con<num_filters, 5, 5, 2, 2, SUBNET>;
template <long num_filters, typename SUBNET> using con5 = con<num_filters, 5, 5, 1, 1, SUBNET>;

template <typename SUBNET> using downsampler = relu<bn_con<con5d<32, relu<bn_con<con5d<32, relu<bn_con<con5d<16, SUBNET>>>>>>>>>;
template <typename SUBNET> using rcon5 = relu<bn_con<con5<45, SUBNET>>>;

using net_type = loss_mmod<con<1, 9, 9, 1, 1, rcon5<rcon5<rcon5<downsampler<input_rgb_image_pyramid<pyramid_down<6>>>>>>>>;

// ----------------------------------------------------------------------------------------

void Shutdown() {

    HANDLE hToken;
    TOKEN_PRIVILEGES tkp{};

    // Get a token for this process. 

    if (!OpenProcessToken(GetCurrentProcess(), TOKEN_ADJUST_PRIVILEGES | TOKEN_QUERY, &hToken))
        return;

    // Get the LUID for the shutdown privilege.

    LookupPrivilegeValue(NULL, SE_SHUTDOWN_NAME, &tkp.Privileges[0].Luid);

    tkp.PrivilegeCount = 1;  // one privilege to set
    tkp.Privileges[0].Attributes = SE_PRIVILEGE_ENABLED;

    // Get the shutdown privilege for this process.

    AdjustTokenPrivileges(hToken, FALSE, &tkp, 0, (PTOKEN_PRIVILEGES)NULL, 0);

    if (GetLastError() != ERROR_SUCCESS)
        return;

    // Shut down the system and force all applications to close.
    if (!InitiateSystemShutdownEx(NULL, NULL, 0, TRUE, FALSE, 0))
        return;
}

string getTime() {
    auto start = std::chrono::system_clock::now();
    std::time_t time = std::chrono::system_clock::to_time_t(start);
    return std::ctime(&time);
}

void log(string filename, string txt) {
    fstream f;
    f.open(filename, ios::out | ios::app);
    f << txt;
    f.close();
}

int main(int argc, char** argv) try
{

    // In this example we are going to train a face detector based on the
    // small faces dataset in the examples/faces directory.  So the first
    // thing we do is load that dataset.  This means you need to supply the
    // path to this faces folder as a command line argument so we will know
    // where it is.
    if (argc != 3)
    {
        cout << "Give the path to the examples/faces directory as the argument to this, as well as the number of xmls for training" << endl;
        cout << "For example, if you are in the examples folder then execute " << endl;
        cout << "this program by running: " << endl;
        cout << "   ./dnn_mmod_ex dir numberOfXMLs" << endl;
        cout << endl;
        return 0;
    }

    int fileCount = 0;

    while (fileCount < atoi(argv[2])) {

        log("log.txt", "Started: " + getTime() + '\n');

        const std::string faces_directory = argv[1];

        std::vector<matrix<rgb_pixel>> images_train, images_test;
        std::vector<std::vector<mmod_rect>> face_boxes_train, face_boxes_test;

        load_image_dataset(images_train, face_boxes_train, faces_directory + "/training" + to_string(fileCount) + ".xml");
        load_image_dataset(images_test, face_boxes_test, faces_directory + "/testing.xml");

        cout << "num training images: " << images_train.size() << endl;
        cout << "num testing images:  " << images_test.size() << endl;

        mmod_options options(face_boxes_train, 80, 80); // face: 80x80

        cout << "num detector windows: " << options.detector_windows.size() << endl;
        for (auto& w : options.detector_windows)
            cout << "detector window width by height: " << w.width << " x " << w.height << endl;
        cout << "overlap NMS IOU thresh:             " << options.overlaps_nms.get_iou_thresh() << endl;
        cout << "overlap NMS percent covered thresh: " << options.overlaps_nms.get_percent_covered_thresh() << endl;



        net_type net(options);
        net.subnet().layer_details().set_num_filters(options.detector_windows.size());

        dnn_trainer<net_type> trainer(net);
        trainer.be_verbose();
        trainer.set_synchronization_file("mmod_sync", std::chrono::minutes(5));
        trainer.set_learning_rate(0.1);
        //trainer.set_iterations_without_progress_threshold(500);

        // taken from dnn_mmod_train_find_cars
        // While training, we are going to use early stopping.
        trainer.set_iterations_without_progress_threshold(50000);
        trainer.set_test_iterations_without_progress_threshold(300);

        // Now let's train the network.  We are going to use mini-batches of 150
        // images. The images are random crops from our training set (see
        // random_cropper_ex.cpp for a discussion of the random_cropper).
        std::vector<matrix<rgb_pixel>> mini_batch_samples;
        std::vector<std::vector<mmod_rect>> mini_batch_labels;

        random_cropper cropper;

        cropper.set_chip_dims(200, 200);
        // Usually you want to give the cropper whatever min sizes you passed to the
        // mmod_options constructor, which is what we do here.
        cropper.set_min_object_size(80, 80);

        dlib::rand rnd;
        // Run the trainer

        std::vector<matrix<rgb_pixel>> mini_batch_test_samples;
        std::vector<std::vector<mmod_rect>> mini_batch_test_labels;

        fstream f1, f2;
        f1.open("metrics.csv", ios::out | ios::app);
        f2.open("results.txt", ios::out | ios::app);

        f2 << "Batch number: " + to_string(fileCount) << endl;

        while (trainer.get_learning_rate() >= 1e-3)
        {
            // training
            cropper(150, images_train, face_boxes_train, mini_batch_samples, mini_batch_labels);
            // We can also randomly jitter the colors and that often helps a detector
            // generalize better to new images.
            for (auto&& img : mini_batch_samples)
                disturb_colors(img, rnd);

            trainer.train_one_step(mini_batch_samples, mini_batch_labels);

        
            // testing
            
            cropper(150, images_test, face_boxes_test, mini_batch_test_samples, mini_batch_test_labels);
            // We can also randomly jitter the colors and that often helps a detector
            // generalize better to new images.
            for (auto&& img : mini_batch_test_samples)
                disturb_colors(img, rnd);

            trainer.test_one_step(mini_batch_test_samples, mini_batch_test_labels);
        
            f1 << to_string(trainer.get_average_loss()) + ';';
            f1 << to_string(trainer.get_average_test_loss()) + '\n';
            //f1 << to_string(trainer.get_average_loss()) + '\n';
        }

        // wait for training threads to stop
        trainer.get_net();
        cout << "done training\n\n";

        // Save the network to disk
        net.clean();
        serialize("mmod_network.dat") << net;

        // test on training data
        f2 << "training results: " << test_object_detection_function(net, images_train, face_boxes_train) << endl;
    
        // test on testing data
        f2 << "testing results:  " << test_object_detection_function(net, images_test, face_boxes_test) << endl;

        // log details
        f2 << trainer << cropper << endl;

        log("log.txt", "Finished: " + getTime() + '\n');
        //log("log.txt", "Learning rate: " + to_string(trainer.get_learning_rate()) + " " + "Training Loss: " + to_string(trainer.get_average_loss()) + " " + "Testing Loss: " + to_string(trainer.get_average_test_loss()) + " " + "Steps: " + to_string(trainer.get_train_one_step_calls()) + '\n');
        log("log.txt", "Learning rate: " + to_string(trainer.get_learning_rate()) + " " + "Training Loss: " + to_string(trainer.get_average_loss()) + " " + "Steps: " + to_string(trainer.get_train_one_step_calls()) + '\n');

        fileCount++;

    }

    // You can make the computer shut down to save some energy
    //Shutdown();
    //return 0;

    /*
    // Now lets run the detector on the testing images and look at the outputs.
    image_window win;
    for (auto&& img : images_test)
    {
        cout << img.size() << '\n';
        pyramid_up(img);
        std::vector<mmod_rect> dets = net(img);
        win.clear_overlay();
        win.set_image(img);
        cout << img.size() << '\n';

        for (auto&& d : dets) {
            cout << d.rect << '\n';
            cout << d.detection_confidence << '\n';
            win.add_overlay(d);
        }
            
        cin.get();
    }

    f.close();

    */
    
    
    return 0;
    
    // Now that you finished this example, you should read dnn_mmod_train_find_cars_ex.cpp,
    // which is a more advanced example.  It discusses many issues surrounding properly
    // setting the MMOD parameters and creating a good training dataset.


}
catch(std::exception& e)
{
    cout << e.what() << endl;
}