import os
from distutils.sysconfig import get_python_lib

if __name__ == "__main__":  # TODO Test if works in virtualenv
    lib_paths = [get_python_lib()]
    if lib_paths[0].startswith("/usr/lib/"):
        # We have to try also with an explicit prefix of /usr/local in order to
        # catch Debian's custom user site-packages directory.
        lib_paths.append(get_python_lib(prefix="/usr/local"))
    overlay_warning = False
    for lib_path in lib_paths:
        existing_path = os.path.abspath(os.path.join(lib_path, "peoples_advisor.pth"))
        if os.path.exists(existing_path):
            # We note the need for the warning here, but present it after the
            # command is run, so it's more likely to be seen.
            overlay_warning = True
            break

    if overlay_warning:
        pass  # Print message overriding the thing and allow for canceling

    pth_file = os.path.join(lib_paths[0], "peoples_advisor.pth")
    pa_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(pth_file, "w") as f:
        f.write(str(pa_path))
