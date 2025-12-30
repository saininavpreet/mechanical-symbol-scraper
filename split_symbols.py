import cv2
import os

def extract_symbols_from_image(image_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # binary threshold
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)

    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    H, W = img.shape[:2]
    count = 0

    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)

        # ignore full sheet / big region
        if w > 0.7 * W or h > 0.7 * H:
            continue

        # ignore very small noise
        if w < 25 or h < 25:
            continue

        # extract
        symbol = img[y:y+h, x:x+w]

        # add padding
        pad = 10
        symbol = cv2.copyMakeBorder(symbol, pad, pad, pad, pad,
                                    cv2.BORDER_CONSTANT, value=[255,255,255])

        # resize standard size
        symbol = cv2.resize(symbol, (256, 256), interpolation=cv2.INTER_AREA)

        file_name = f"symbol_{count}.png"
        save_path = os.path.join(output_dir, file_name)
        cv2.imwrite(save_path, symbol)

        print(f"✔ Saved {file_name}")
        count += 1

    print(f"🎯 Completed — extracted {count} symbols from {os.path.basename(image_path)}")

def process_folder(folder="data"):
    for category in os.listdir(folder):
        category_path = os.path.join(folder, category)
        if not os.path.isdir(category_path):
            continue

        out_dir = os.path.join("cleaned_symbols", category)
        for file in os.listdir(category_path):
            if file.lower().endswith((".jpg", ".png", ".jpeg", ".webp")):
                extract_symbols_from_image(os.path.join(category_path, file), out_dir)

if __name__ == "__main__":
    process_folder()
