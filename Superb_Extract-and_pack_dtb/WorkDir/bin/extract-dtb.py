#!/usr/bin/env python3

import sys
import argparse
import os
import subprocess

extract_offsets_script = "./bin/extract_offsets.py"  # Замените на фактический путь к скрипту
subprocess.run([sys.executable, extract_offsets_script])

__version__ = "1.5"

DTB_HEADER = b"\xd0\x0d\xfe\xed"


def dump_file(filename, content):
    """Dump the content to a file."""
    with open(filename, "wb") as fp:
        fp.write(content)


def safe_output_path(output_dir, dtb_filename_new):
    """Safely combine the output folder with the relative path of the dtb
    (which may contain subfolders) and create the necessary folder structure.

    :returns: the resulting file name
    """
    if "../" in dtb_filename_new + "/":
        raise RuntimeError("DTB file path points outside of extraction"
                           " directory: " + dtb_filename_new)
    ret = os.path.join(output_dir, dtb_filename_new)
    os.makedirs(os.path.dirname(ret), exist_ok=True)
    return ret


def convert_dtb_to_dts(dtb_filename):
    """Convert a dtb file to dts using dtc."""
    dts_filename = dtb_filename + ".dts"

    cmd = ["bin/dtc", "-I", "dtb", "-O", "dts", dtb_filename, "-o", dts_filename]

    try:
        subprocess.run(cmd, check=True)
        print(f"Converted {dtb_filename} to {dts_filename}")
    except subprocess.CalledProcessError as e:
        print(f"Error converting {dtb_filename} to dts: {e}")
        print(f"Command: {' '.join(cmd)}")


def split(args):
    """Read a file and look for DTB_HEADER occurrences (beginning of each DTB).
    Then extract each one. If possible, use the device model as filename.
    """
    positions = []

    with open(args.filename, "rb") as fp:
        content = fp.read()

    dtb_next = content.find(DTB_HEADER)
    while dtb_next != -1:
        positions.append(dtb_next)
        dtb_next = content.find(DTB_HEADER, dtb_next + 1)

    if len(positions) == 0:
        print("No appended dtbs found")
        return

    if args.extract:
        os.makedirs(args.output_dir, exist_ok=True)
        begin_pos = 0
        for n, pos in enumerate(positions, 0):
            dtb_filename = get_dtb_filename(n)
            
            # Добавим условие, чтобы извлекать только файлы с расширением .dtb
            if dtb_filename.endswith(".dtb"):
                filepath = os.path.join(args.output_dir, dtb_filename)

                # Добавим уникальный суффикс к имени файла, если файл уже существует
                counter = 1
                while os.path.exists(filepath):
                    dtb_filename = get_dtb_filename(n, suffix=f"_{counter}")
                    filepath = os.path.join(args.output_dir, dtb_filename)
                    counter += 1

                dump_file(filepath, content[begin_pos:pos])

                # Добавим конвертацию dtb в dts только для файлов с расширением .dtb
                convert_dtb_to_dts(filepath)

                if n > 0:
                    dtb_filename_new = get_dtb_filename(n)
                    dtb_filename_new_full = safe_output_path(args.output_dir,
                                                             dtb_filename_new)
                    os.rename(filepath, dtb_filename_new_full)
                    dtb_filename = dtb_filename_new
                print(f"Dumped {dtb_filename}, start={begin_pos} end={pos}")
            begin_pos = pos

        # Last chunk
        dtb_filename = get_dtb_filename(n + 1)
        filepath = os.path.join(args.output_dir, dtb_filename)

        # Добавим уникальный суффикс к имени файла, если файл уже существует
        counter = 1
        while os.path.exists(filepath):
            dtb_filename = get_dtb_filename(n + 1, suffix=f"_{counter}")
            filepath = os.path.join(args.output_dir, dtb_filename)
            counter += 1

        dump_file(filepath, content[begin_pos:])
        dtb_filename_new = get_dtb_filename(n + 1)
        os.rename(os.path.join(filepath),
                  os.path.join(args.output_dir, dtb_filename_new))
        dtb_filename = dtb_filename_new

        # Добавим конвертацию dtb в dts только для файлов с расширением .dtb
        if filepath.endswith(".dtb"):
            convert_dtb_to_dts(filepath)

        print(f"Dumped {dtb_filename}, start={begin_pos} end={len(content)}")
        print ("")
        print(f"Extracted {len(positions)} appended dts and dtb to folder / {args.output_dir}")
    else:
        print(f"Found {len(positions)} appended dtbs")


def get_dtb_filename(n, suffix=""):
    """Get the filename for the DTB."""
    if n == 0:
        return "00_kernel"
    n = str(n).zfill(2)
    basename = f"{n}_dtbdump"
    if suffix != "":
        basename += f"_{suffix}"
    return f"{basename}.dtb"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract dtbs from kernel images.")
    parser.add_argument("filename", help="Android kernel image")
    parser.add_argument("-o", dest="output_dir", default="dtb",
                        required=False, help="Output directory")
    parser.add_argument("-n", dest="extract", action="store_false", default=True,
                        required=False, help="Do not extract, just output information")
    parser.add_argument("-V", "--version", action="version", version=__version__)

    args = parser.parse_args()

    split(args)