import os
import shutil
from PIL import Image, ImageDraw

def create_icons(source_path, res_dir):
    img = Image.open(source_path).convert("RGBA")
    
    # Create circular version
    mask = Image.new('L', img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + img.size, fill=255)
    round_img = Image.new("RGBA", img.size)
    round_img.paste(img, (0, 0), mask)
    
    sizes = {
        'mipmap-mdpi': 48,
        'mipmap-hdpi': 72,
        'mipmap-xhdpi': 96,
        'mipmap-xxhdpi': 144,
        'mipmap-xxxhdpi': 192
    }
    
    for folder, size in sizes.items():
        folder_path = os.path.join(res_dir, folder)
        os.makedirs(folder_path, exist_ok=True)
        
        # Standard square/squircle
        resized = img.resize((size, size), Image.Resampling.LANCZOS)
        resized.save(os.path.join(folder_path, "ic_launcher.png"))
        
        # Round icon
        resized_round = round_img.resize((size, size), Image.Resampling.LANCZOS)
        resized_round.save(os.path.join(folder_path, "ic_launcher_round.png"))
        
        # We can also put a foreground icon to override if anydpi is still somewhat active
        # though we will delete anydpi-v26 below
        fg_size = int(size * (108/48)) # Adaptive foreground size formula
        resized_fg = img.resize((fg_size, fg_size), Image.Resampling.LANCZOS)
        resized_fg.save(os.path.join(folder_path, "ic_launcher_foreground.png"))
        
    print("Icons generated successfully in all densities.")
    
    # Remove adaptive icon xmls so it falls back to PNGs safely
    anydpi_path = os.path.join(res_dir, "mipmap-anydpi-v26")
    if os.path.exists(anydpi_path):
        shutil.rmtree(anydpi_path)
        print("Removed mipmap-anydpi-v26 to fallback to standard icons.")

if __name__ == "__main__":
    source = r"C:\Users\www-r\.gemini\antigravity\brain\8f765f97-2771-44a3-9f56-33b97dd847c8\app_icon_ai_finance_1782597114561.png"
    res_dir = r"c:\Users\www-r\expense-tracker-bot\android\app\src\main\res"
    create_icons(source, res_dir)
