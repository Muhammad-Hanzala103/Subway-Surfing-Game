import PyInstaller.__main__
import os
import shutil

def build():
    print("Building Subway Surfing Game...")
    
    # Clean previous builds
    for dir_name in ['build', 'dist']:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            
    # Run PyInstaller
    PyInstaller.__main__.run([
        'main.py',
        '--name=RailRunners',
        '--windowed',
        '--noconfirm',
        '--add-data=assets;assets',
        '--hidden-import=pygame',
        '--hidden-import=OpenGL',
    ])
    
    print("Build complete! Check the 'dist' folder.")

if __name__ == "__main__":
    build()
