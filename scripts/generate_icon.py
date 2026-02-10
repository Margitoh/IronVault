from PIL import Image, ImageDraw, ImageFont
import os

def create_icon():
    # Settings
    size = (512, 512)
    bg_color = (30, 30, 30) # Dark Grey
    accent_color = (127, 90, 240) # Purple
    secondary_color = (44, 255, 230) # Cyan-ish
    
    # Create Image
    img = Image.new('RGB', size, bg_color)
    draw = ImageDraw.Draw(img)
    
    # Draw Shield Shape (Simplified)
    # Points for a shield
    shield_pts = [
        (256, 50),   # Top Center
        (450, 100),  # Top Right
        (450, 300),  # Mid Right
        (256, 480),  # Bottom Tip
        (62, 300),   # Mid Left
        (62, 100)    # Top Left
    ]
    draw.polygon(shield_pts, fill=bg_color, outline=accent_color, width=20)
    
    # Draw "Lock" body inside
    lock_body = [180, 250, 332, 380] # [x0, y0, x1, y1]
    draw.rectangle(lock_body, fill=accent_color)
    
    # Draw "Lock" shackle
    shackle_bbox = [180+30, 150, 332-30, 250+50]
    draw.arc(shackle_bbox, start=180, end=0, fill=secondary_color, width=20)
    draw.line([(180+30, 200), (180+30, 250)], fill=secondary_color, width=20)
    draw.line([(332-30, 200), (332-30, 250)], fill=secondary_color, width=20)

    # Save as PNG
    img.save("ironvault_icon.png")
    print("Saved ironvault_icon.png")
    
    # Save as ICO
    img.save("ironvault.ico", format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
    print("Saved ironvault.ico")

if __name__ == "__main__":
    create_icon()
