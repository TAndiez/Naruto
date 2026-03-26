import gdown
import os

OUTPUT_DIR = "AI/checkpoints"

os.makedirs(OUTPUT_DIR, exist_ok=True)

url = f"https://drive.google.com/drive/folders/1OhvO6fnedi1UYS46_ZX4ypJPK3pOcaAU"
gdown.download_folder(url, output=OUTPUT_DIR, quiet=False)
