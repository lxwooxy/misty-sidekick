import cv2

# Load the image
image = cv2.imread("lola_1.jpg")

# Apply a strong Gaussian blur to the whole image
blurred_image = cv2.GaussianBlur(image, (199, 199), 30)  # Increase kernel size for more blur

# Save and show the result
cv2.imwrite("blurred_whole_image.jpg", blurred_image)
cv2.imshow("Blurred Image", blurred_image)
cv2.waitKey(0)
cv2.destroyAllWindows()
