import os
import shutil
import zipfile
from pathlib import Path
from pprint import pprint

path_zonetool = Path("S:\\Call of Duty\\CoD 6 (MW2)\\zonetool_iw4.exe")
path_zonebuilder = Path("S:\\Call of Duty\\CoD 6 (MW2)\\_TOOLS\\ZoneBuilder\\ZoneBuilder.exe")

log_file = open(__file__[:-3] + ".log", "w")

def log(*args, **kwargs):
    print(*args, **kwargs)
    print(*args, **kwargs, file=log_file)

def dump_iwd_files(src_dir, dest_dir):
    log("dest_dir",dest_dir)
    f = 0;e = []
    for root, _, files in os.walk(src_dir):
        for file in files:
            if file.endswith(('.iwd', '.iwd.disabled')):
                f += 1
                src_path = os.path.join(root, file)
                # dest_dir_rel = os.path.join(dest_dir, os.path.relpath(root, src_dir), file[:-4])
                # log("dest_dir_rel",dest_dir_rel)
                if not os.path.exists(dest_dir):
                    os.makedirs(dest_dir)
                # else:
                #     shutil.rmtree(dest_dir)
                try:
                    with zipfile.ZipFile(src_path, 'r') as zfile:
                        log("Extracting",src_path,"...")
                        zfile.extractall(dest_dir)
                except Exception as ex:
                    e.append((file, ex))
                    log((file,ex))
    print("Extracted", f, "files with", e, "errors.")
    return f, e

if __name__ == "__main__":
    dest_folder = "G:/CoD 6 (Dump)/"
    f = 0;e = []
    _f, _e = dump_iwd_files("S:/Call of Duty/CoD 6 (MW2)", dest_folder)
    f += _f;e += _e
    _f, _e = dump_iwd_files("S:/Call of Duty/CoD 6 (Steam)", dest_folder)
    f += _f;e += _e
    _f, _e = dump_iwd_files("S:/Call of Duty/CoD 6 (Server)", dest_folder)
    f += _f;e += _e
    log("Extracted", f, "files with", len(e), "errors.")
    pprint(e)
    input("Press Enter to exit...")
    log_file.flush()
    log_file.close()
