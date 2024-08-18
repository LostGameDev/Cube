import shutil
import os
import PyInstaller.__main__

PyInstaller.__main__.run([
    'cube.py',
    '--onefile',
    '--noconsole',
    '--icon=icon.ico',
    '--add-data=icon.ico;.'
])

if os.path.exists("./dist/Objects") != True:
    shutil.copytree("./Objects", "./dist/Objects")
else:
    shutil.rmtree("./dist/Objects")
    shutil.copytree("./Objects", "./dist/Objects")