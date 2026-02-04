from PIL import Image, ImageDraw, ImageFont

def create_icon():
    # 1. Setup Canvas (512x512 for high res)
    size = (512, 512)
    # Apple Health-like Dark Background
    bg_color = (0, 0, 0) # Black
    
    img = Image.new('RGB', size, color=bg_color)
    d = ImageDraw.Draw(img)
    
    # 2. Draw a Sleek Abstract "Pulse" / Activity Ring
    # iOS Blue: #007AFF -> RGB (0, 122, 255)
    # Health Red: #FF2D55 -> RGB (255, 45, 85)
    # Activity Green: #34C759 -> RGB (52, 199, 89)
    
    center = (256, 256)
    radius = 180
    width = 40
    
    # Draw Blue Ring
    # Bounding box: [x0, y0, x1, y1]
    bbox = [
        center[0] - radius, center[1] - radius,
        center[0] + radius, center[1] + radius
    ]
    
    # Draw arc (Health Ring Style)
    # Start at top (270) and go around
    d.arc(bbox, start=140, end=40, fill=(0, 122, 255), width=width)
    
    # Draw Red Accent (Pulse)
    bbox_inner = [
        center[0] - radius + 50, center[1] - radius + 50,
        center[0] + radius - 50, center[1] + radius - 50
    ]
    d.arc(bbox_inner, start=40, end=380, fill=(255, 45, 85), width=width-10)

    # 3. Add a simple "D" for Dheeraj in the middle? 
    # Or just keep it abstract geometrical. Abstract is classier.
    # Let's add a small central dot to make it look like a target/tracker.
    
    d.ellipse(
        [center[0]-20, center[1]-20, center[0]+20, center[1]+20],
        fill=(255, 255, 255)
    )

    # Save
    img.save("icon.png")
    print("Icon generated as icon.png")

if __name__ == "__main__":
    create_icon()
