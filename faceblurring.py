import cv2

# Load Haar cascade for face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Load the image
image = cv2.imread("person.jpg")
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Detect faces
faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

# Apply median blur to detected faces
for (x, y, w, h) in faces:
    face_roi = image[y:y+h, x:x+w]
    blurred_face = cv2.GaussianBlur(face_roi, (199, 199), 30)

    image[y:y+h, x:x+w] = blurred_face

# Save or display
cv2.imwrite("median_blurred_face.jpg", image)
cv2.imshow("Blurred Face", image)
cv2.waitKey(0)
cv2.destroyAllWindows()
