import glob
import os

target_dir = "c:/Users/ASUS/Downloads/Gastric-Cancer-Risk-Estimation---main/Gastric-Cancer-Risk-Estimation---main/templates"
for filepath in glob.glob(os.path.join(target_dir, "*.html")):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace references
    new_content = content.replace("http://localhost:5173/login", "/logout")
    new_content = new_content.replace("http://localhost:5173/signup", "/signup")
    
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated {os.path.basename(filepath)}")
