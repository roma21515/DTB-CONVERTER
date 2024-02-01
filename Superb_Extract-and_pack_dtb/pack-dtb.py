import os
import argparse
import shutil
import subprocess

def convert_dts_to_dtb(dts_path, dtb_path):
    """Convert a dts file to dtb using dtc."""
    cmd = ["bin/dtc", "-I", "dts", "-O", "dtb", dts_path, "-o", dtb_path]

    try:
        subprocess.run(cmd, check=True)
        print(f"Converted {dts_path} to {dtb_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error converting {dts_path} to dtb: {e}")
        print(f"Command: {' '.join(cmd)}")

def delete_dtb_files(directory):
    """Delete all files with the .dtb extension in the specified directory."""
    dtb_files = [file for file in os.listdir(directory) if file.endswith(".dtb")]
    for dtb_file in dtb_files:
        dtb_path = os.path.join(directory, dtb_file)
        os.remove(dtb_path)
        print(f"Deleted {dtb_path}")

# Укажите путь к папке с файлами DTS и DTB
dtb_directory = "dtb"

# Удалите все существующие файлы DTB в папке dtb_directory
delete_dtb_files(dtb_directory)

# Проход по всем файлам DTS в папке dtb_directory и их конвертация в DTB
for dts_file in os.listdir(dtb_directory):
    if dts_file.endswith(".dts"):
        dts_path = os.path.join(dtb_directory, dts_file)
        dtb_file = dts_file.replace(".dts", "")
        dtb_path = os.path.join(dtb_directory, dtb_file)
        convert_dts_to_dtb(dts_path, dtb_path)
        
def pack_dtb_files(input_dir="dtb", original_kernel_image="work.img", output_kernel_image="your_new_file.img", offsets_file="dtb_offsets.txt"):
    # Copy the original kernel image to the output file
    shutil.copy(original_kernel_image, output_kernel_image)

    with open(offsets_file, 'r') as offsets:
        dtb_offsets = [int(line.split(':')[1].strip()) for line in offsets]

    dtb_files = [file for file in os.listdir(input_dir) if file.endswith(".dtb")]

    if not dtb_files:
        print("No DTB files found in the specified directory.")
        return

    dtb_files.sort()  # Ensure files are in the correct order

    with open(output_kernel_image, "r+b") as kernel_image:
        # Add DTB files to the kernel image using the correct offsets
        for dtb_file, dtb_offset in zip(dtb_files, dtb_offsets):
            dtb_path = os.path.join(input_dir, dtb_file)
            with open(dtb_path, "rb") as dtb:
                dtb_content = dtb.read()
                kernel_image.seek(dtb_offset)
                kernel_image.write(dtb_content)
    
    print ("")
    print(f"DTB files successfully added to {output_kernel_image}")

if __name__ == "__main__":
    pack_dtb_files()