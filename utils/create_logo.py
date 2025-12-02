"""
Create a professional logo for Smart Study Assistant
"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_logo():
    # Create a 128x128 image with transparent background
    size = 128
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Color scheme - modern gradient blue/purple
    primary_color = (66, 133, 244)  # Google blue
    secondary_color = (156, 39, 176)  # Purple
    accent_color = (255, 193, 7)  # Gold for star
    
    # Draw circular background with gradient effect
    center = size // 2
    radius = 58
    
    # Outer circle (shadow effect)
    draw.ellipse([center-radius-2, center-radius-2, 
                  center+radius+2, center+radius+2], 
                 fill=(primary_color[0], primary_color[1], primary_color[2], 200))
    
    # Main circle
    draw.ellipse([center-radius, center-radius, 
                  center+radius, center+radius], 
                 fill=primary_color)
    
    # Draw graduation cap
    # Cap top (square board)
    cap_top_y = center - 15
    cap_width = 50
    cap_points = [
        (center - cap_width//2, cap_top_y),
        (center + cap_width//2, cap_top_y),
        (center + cap_width//2 + 5, cap_top_y + 8),
        (center - cap_width//2 + 5, cap_top_y + 8)
    ]
    draw.polygon(cap_points, fill='white')
    
    # Cap base (head part)
    base_y = cap_top_y + 8
    draw.ellipse([center-20, base_y, center+20, base_y+25], fill='white')
    
    # Tassel
    draw.line([center + cap_width//2 - 10, cap_top_y + 3, 
               center + cap_width//2, cap_top_y - 5], 
              fill=accent_color, width=2)
    draw.ellipse([center + cap_width//2 - 3, cap_top_y - 8,
                  center + cap_width//2 + 3, cap_top_y - 2], 
                 fill=accent_color)
    
    # Draw book below cap
    book_y = center + 15
    # Book cover
    draw.rectangle([center-25, book_y, center+25, book_y+20], 
                   fill='white', outline=None)
    # Book pages (side lines)
    for i in range(3):
        x_offset = -20 + i * 2
        draw.line([center+x_offset, book_y+3, center+x_offset, book_y+17], 
                  fill=primary_color, width=1)
    
    # Add a small star for "smart" element
    star_y = center - 35
    star_points = []
    for i in range(10):
        angle = i * 36  # 360/10
        if i % 2 == 0:
            r = 8
        else:
            r = 4
        import math
        x = center + r * math.cos(math.radians(angle - 90))
        y = star_y + r * math.sin(math.radians(angle - 90))
        star_points.append((x, y))
    draw.polygon(star_points, fill=accent_color)
    
    # Save the logo
    logo_path = os.path.join(os.path.dirname(__file__), 'logo.png')
    img.save(logo_path, 'PNG')
    print(f"✅ Logo created successfully: {logo_path}")
    
    # Also create a smaller version for window icon
    icon_img = img.resize((64, 64), Image.Resampling.LANCZOS)
    icon_path = os.path.join(os.path.dirname(__file__), 'icon.png')
    icon_img.save(icon_path, 'PNG')
    print(f"✅ Icon created successfully: {icon_path}")
    
    return logo_path, icon_path

if __name__ == "__main__":
    create_logo()
