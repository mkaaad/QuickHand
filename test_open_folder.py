"""测试打开文件夹的跨平台方法"""
import os
import sys
import subprocess

def open_folder(path):
    """使用系统默认方式打开文件夹"""
    path = path.strip()
    if path.startswith('file://'):
        from urllib.parse import urlparse
        path = urlparse(path).path
    if not os.path.isdir(path):
        print(f'路径不存在：{path}')
        return False
    if sys.platform == 'win32':
        p = subprocess.Popen(['explorer', path])
    elif sys.platform == 'darwin':
        p = subprocess.Popen(['open', path])
    else:
        p = subprocess.Popen(['xdg-open', path])
    print(f'已尝试打开：{path}  (PID={p.pid})')
    return True

if __name__ == '__main__':
    # 测试各种路径格式
    test_paths = [
        os.getcwd(),
        os.getcwd() + '/output',
        'file://' + os.getcwd(),
    ]
    for p in test_paths:
        print(f'\n测试路径: {p}')
        open_folder(p)
