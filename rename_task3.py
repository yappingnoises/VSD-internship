import shutil, os

base = '/home/toshi/Desktop/vsd/VSD-internship/images/task3'

mapping = {
    'Screenshot from 2026-06-15 17-33-39.png': 'a.png',
    'Screenshot from 2026-06-15 17-35-06.png': 'b.png',
    'Screenshot from 2026-06-15 17-38-37.png': 'c.png',
    'Screenshot from 2026-06-15 17-39-55.png': 'd.png',
    'Screenshot from 2026-06-15 23-03-31.png': 'e.png',
    'Screenshot from 2026-06-15 23-05-12.png': 'f.png',
    'Screenshot from 2026-06-15 23-06-49.png': 'g.png',
    'Screenshot from 2026-06-15 23-17-47.png': 'h.png',
}

for src_name, dst_name in mapping.items():
    src = os.path.join(base, src_name)
    dst = os.path.join(base, dst_name)
    if os.path.exists(src):
        shutil.copy2(src, dst)
        print(f'Copied: {src_name} -> {dst_name}')
    else:
        print(f'NOT FOUND: {src_name}')

print('Done.')
