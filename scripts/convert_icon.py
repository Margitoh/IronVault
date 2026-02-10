from PIL import Image
import os

img_path = "ironvault_icon.png"
if os.path.exists(img_path):
    img = Image.open(img_path)
    img.save("ironvault.ico", format='ICO', sizes=[(256, 256)])
    print("Converted to ironvault.ico")
else:
    print("Image not found")
