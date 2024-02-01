import os

def extract_offsets():
    script_dir = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(script_dir, 'work.img')
    
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found.")
        return

    try:
        with open(file_path, 'rb') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File {file_path} not found.")
        return

    offsets = []
    offset = content.find(b'\xd0\x0d\xfe\xed')
    while offset != -1:
        offsets.append(offset)
        offset = content.find(b'\xd0\x0d\xfe\xed', offset + 1)

    if not offsets:
        print("No DTB headers found in the specified file.")
        return

    with open('dtb_offsets.txt', 'w') as f:
        for i, offset in enumerate(offsets, 1):
            f.write(f"DTB{i} Offset: {offset}\n")

    print(f"DTB offsets extracted and saved to dtb_offsets.txt")

if __name__ == '__main__':
    extract_offsets()