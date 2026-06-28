import os
import io
import urllib.request
import textwrap
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.conf import settings
from products.models import Product
from PIL import Image, ImageDraw, ImageFont

# Define category colors matching the design system
CATEGORY_COLORS = {
    'electronics': '#1a1a2e',  # dark navy
    'clothing': '#16213e',     # deep blue
    'books': '#e94560',        # accent
    'home': '#0f3460',         # standard surface
    'sports': '#2c3e50',
    'beauty': '#e94560',
    'toys': '#16213e',
    'grocery': '#2c3e50',
}

def draw_icon(draw, category, center_x, center_y, size=96):
    """Draws a stylized geometric icon centered at (center_x, center_y)"""
    half = size // 2
    color = "white"
    width = 4
    
    if category == 'electronics':
        # Laptop shape
        # Screen
        draw.rectangle([center_x - half, center_y - half, center_x + half, center_y + half - 20], outline=color, width=width)
        # Base
        draw.polygon([(center_x - half - 10, center_y + half - 20),
                      (center_x + half + 10, center_y + half - 20),
                      (center_x + half + 20, center_y + half),
                      (center_x - half - 20, center_y + half)], outline=color, width=width)
    elif category == 'books':
        # Book shape
        draw.rectangle([center_x - half, center_y - half, center_x + half, center_y + half], outline=color, width=width)
        draw.line((center_x, center_y - half, center_x, center_y + half), fill=color, width=width)
        # Pages
        draw.line((center_x - half + 15, center_y - half + 15, center_x - 15, center_y - half + 15), fill=color, width=3)
        draw.line((center_x - half + 15, center_y - half + 35, center_x - 15, center_y - half + 35), fill=color, width=3)
        draw.line((center_x - half + 15, center_y - half + 55, center_x - 15, center_y - half + 55), fill=color, width=3)
    elif category == 'clothing':
        # Hanger shape
        draw.polygon([(center_x, center_y - half + 30), 
                      (center_x - half, center_y + half - 20), 
                      (center_x + half, center_y + half - 20)], outline=color, width=width)
        # Hook
        draw.arc([center_x - 15, center_y - half, center_x + 15, center_y - half + 30], 180, 0, fill=color, width=width)
    else:
        # Generic box shape (shopping bag)
        draw.rectangle([center_x - half + 10, center_y - half + 20, center_x + half - 10, center_y + half], outline=color, width=width)
        # Handles
        draw.arc([center_x - 20, center_y - half, center_x + 20, center_y - half + 40], 180, 0, fill=color, width=width)

class Command(BaseCommand):
    help = 'Generates clean, branded placeholder images for all products using pure CSS/SVG equivalents in PIL.'

    def handle(self, *args, **kwargs):
        font_path = 'C:/Windows/Fonts/arial.ttf'
        
        try:
            # 28 point size looks roughly like 20px
            font = ImageFont.truetype(font_path, 28)
        except IOError:
            self.stdout.write(self.style.WARNING("Could not load Arial font. Using default."))
            font = ImageFont.load_default()

        products = Product.objects.all()
        count = 0
        
        for product in products:
            # Overwrite all product images since current ones are broken placeholders
            self.stdout.write(f"Generating branded placeholder for: {product.name}")
            
            bg_color = CATEGORY_COLORS.get(product.category, '#1a1a2e')
            img = Image.new('RGB', (600, 600), color=bg_color)
            draw = ImageDraw.Draw(img, 'RGBA')
            
            # 1. Subtle dot grid overlay (5% opacity white)
            dot_color = (255, 255, 255, 13)
            for x in range(0, 600, 20):
                for y in range(0, 600, 20):
                    draw.point((x, y), fill=dot_color)
                    
            # 2. Draw centered geometric icon
            draw_icon(draw, product.category, 300, 250, size=110)
            
            # 3. Product Title Text (wrapped to 2 lines max)
            wrapper = textwrap.TextWrapper(width=34)
            name_lines = wrapper.wrap(text=product.name)[:2]
            
            y_text = 380
            for line in name_lines:
                # Center text horizontally
                if hasattr(font, 'getbbox'):
                    bbox = font.getbbox(line)
                    w = bbox[2] - bbox[0]
                    h = bbox[3] - bbox[1]
                else:
                    w, h = draw.textsize(line, font=font)
                    
                draw.text(((600 - w) / 2, y_text), line, font=font, fill="white")
                y_text += h + 15
                
            # Save to buffer
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            
            # Assign image to product via ContentFile
            filename = f"{product.slug}-branded.png"
            product.image.save(filename, ContentFile(buffer.getvalue()), save=True)
            count += 1
                
        self.stdout.write(self.style.SUCCESS(f"Successfully generated {count} branded placeholder images!"))
