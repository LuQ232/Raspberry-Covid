import numpy as np
import cv2
import argparse


from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.models import load_model

# camera setup
cam = cv2.VideoCapture(0)



while True:
    
    capture_status, frame = cam.read()
    if not capture_status:
        print("ERR: Can't take camera frame!")
        break
    
    cv2.imshow("Input", frame)
    k = cv2.waitKey(1)
    
    
    #ESCAPE PRESED
    if k % 256 == 27:
        print("Escape hit, closing...")
        break
    # SPACE pressed
    elif k % 256 == 32:
        # loading weights and caffemodel for face detection
        net_caffe = cv2.dnn.readNetFromCaffe("./Face_detection_models/weights.txt", "./Face_detection_models/res.caffemodel")

        # loading model for mask detection
        mask_detection_model = load_model("./Mask_detection_model/mask_detector.model")

        # load and resize image to 300x300
        image = frame
        image = cv2.resize(image, (300, 300))
        (photo_height, photo_width) = image.shape[:2]

        photo_blob = cv2.dnn.blobFromImage(image, 1.0, (300, 300), (104, 117, 123))

        # make detections on the photo
        net_caffe.setInput(photo_blob)
        detections = net_caffe.forward()

        # loop over all detections
        for i in range(0, detections.shape[2]):
            # take confidence of prediction
            confidence = detections[0, 0, i, 2]

            # minimum confidence threshold
            if confidence > 0.5:
                box = detections[0, 0, i, 3:7] * np.array([photo_width, photo_height, photo_width, photo_height])
                (x1, y1, x2, y2) = box.astype("int")
                cv2.rectangle(image, (x1, y1), (x2, y2), (255, 0, 255), 2)
                
                #printing face coordinates
                print(f"x1={x1}")
                print(f"x2={x2}")
                print(f"y1={y1}")
                print(f"y2={y2}")
                
                #MASK DETECTION
                face = image[y1 : y2,x1 : x2]
                face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
                face = cv2.resize(face, (224,224))
                face = img_to_array(face)
                face = np.expand_dims(face, axis=0)
                
                #making mask predictions 
                (mask_prediction, no_mask_prediction) = mask_detection_model.predict(face)[0]
                print(f"mask prediction: {mask_prediction} ")
                print(f"no mask prediction: {no_mask_prediction}")
                
                if mask_prediction > no_mask_prediction:
                    label = "MASK"
                    label_color = (0,255,0)
                    label += f" {round(max(mask_prediction,no_mask_prediction) * 100)}%"
                else:
                    label = "NO MASK"
                    label_color = (0,0,255)
                    label += f" {round(max(mask_prediction,no_mask_prediction) * 100)}%"
                cv2.putText(image,label,(x1,y1 - 5),cv2.FONT_HERSHEY_SIMPLEX, 0.5, label_color, 2)
                
        
        image = cv2.resize(image, (800, 800))
        # show output
        cv2.imshow("Output", image)
        cv2.waitKey(0)


cam.release()
cv2.destroyAllWindows()
