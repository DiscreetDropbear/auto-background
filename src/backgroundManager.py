import subprocess


"""
    uses the feh utility to set the background
"""
def set_background(backgroundPath, shell=True, backgroundSettings=["--bg-fill"]):
    args = "feh" 

    for setting in backgroundSettings:

        args += " "
        args += setting

    args += " "
    args += backgroundPath

    result = subprocess.Popen(args, shell=True, universal_newlines=True)
    returncode = result.returncode
