import cv2
import time

def AuthenticateFace():
    # Initialize face recognition components
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read('engine\\auth\\trainer\\trainer.yml')
    cascadePath = "engine\\auth\\haarcascade_frontalface_default.xml"
    faceCascade = cv2.CascadeClassifier(cascadePath)
    font = cv2.FONT_HERSHEY_SIMPLEX
    
    # Configuration
    id = 2  # Number of persons you want to recognize
    names = ['', 'Abhinav']  # Names corresponding to IDs
    cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cam.set(3, 640)  # Frame width
    cam.set(4, 480)  # Frame height
    minW = 0.1 * cam.get(3)
    minH = 0.1 * cam.get(4)
    
    # Track authentication state
    last_recognition = None
    last_recognition_time = 0
    
    while True:
        ret, img = cam.read()
        if not ret:
            break
            
        # Face detection
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(
            gray,
            scaleFactor=1.2,
            minNeighbors=5,
            minSize=(int(minW), int(minH)),
        )
        
        current_recognition = None
        
        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
            # Face recognition
            id, confidence = recognizer.predict(gray[y:y+h, x:x+w])
            
            if confidence < 100:  # Recognized face
                name = names[id]
                confidence_text = "  {0}%".format(round(100 - confidence))
                current_recognition = name
                
                cv2.putText(img, name, (x+5, y-5), font, 1, (255, 255, 255), 2)
                cv2.putText(img, confidence_text, (x+5, y+h-5), 
                           font, 1, (255, 255, 0), 1)
            else:  # Unknown face
                cv2.putText(img, "unknown", (x+5, y-5), font, 1, (0, 0, 255), 2)
        
        # Update last recognition if we see the same face for 5 consecutive frames
        if current_recognition == last_recognition:
            if time.time() - last_recognition_time > 0.5:  # ~5 frames at 10fps
                last_recognition = current_recognition
        else:
            last_recognition = current_recognition
            last_recognition_time = time.time()
        
        # Display instructions
        status = f"Recognized: {last_recognition}" if last_recognition else "No face recognized"
        cv2.putText(img, status, (10, 30), font, 0.8, (0, 255, 0), 2)
        cv2.putText(img, "Press ESC to confirm", (10, img.shape[0]-10), 
                   font, 0.5, (255, 255, 255), 1)
        
        cv2.imshow('Face Authentication (Press ESC)', img)
        
        # Check for ESC key
        k = cv2.waitKey(10) & 0xff
        if k == 27:  # ESC pressed
            break
    
    # Cleanup
    cam.release()
    cv2.destroyAllWindows()
    
    # Return 1 if recognized, 0 otherwise
    return 1 if last_recognition == "Abhinav" else 0

