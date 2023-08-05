import cv2
import pytesseract

def extract_license_plate(frame):
    pytesseract.pytesseract.tesseract_cmd = r'C:\Users\LENOVO\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 11, 17, 17)
    edged = cv2.Canny(gray, 30, 200)
    
    contours, _ = cv2.findContours(edged, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]
    
    for contour in contours:
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.018 * peri, True)

        if len(approx) == 4:
            x, y, w, h = cv2.boundingRect(approx)
            plate_cropped = frame[y:y+h, x:x+w]
            return plate_cropped, (x, y, w, h)

    return None, None
def main():
    pytesseract.pytesseract.tesseract_cmd = r'C:\Users\LENOVO\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'
    video_path = 'a.mp4' 
    video_capture = cv2.VideoCapture(video_path)

    while True:
        ret, frame = video_capture.read()

        if not ret:
            break

        plate, plate_coords = extract_license_plate(frame)

        if plate is not None:
            gray_plate = cv2.cvtColor(plate, cv2.COLOR_BGR2GRAY)
            text = pytesseract.image_to_string(gray_plate, config='--psm 11')
            print("Detected License Plate: ", text)
            x, y, w, h = plate_coords
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.imshow("License Plate Detection", plate)

        cv2.imshow("Video", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
