#!/usr/bin/python3

from sys import argv
from subprocess import Popen, PIPE

class Command:
  def __init__(self, output, error, return_code):
    self.output = output.decode("UTF-8")
    self.error = error.decode("UTF-8")
    self.return_code = return_code

class Window:
    def __init__(self, window_id, title, pos_x, pos_y, size_x, size_y):
        self.window_id = window_id
        self.title = title
        self.pos_x = int(pos_x)
        self.pos_y = int(pos_y)
        self.size_x = int(size_x)
        self.size_y = int(size_y)
    
    def debug(self):
        print("[DEBUG] Window %s, %s ,%s ,%s ,%s ,%s" % (
            self.window_id, 
            self.title, 
            self.pos_x, 
            self.pos_y, 
            self.size_x, 
            self.size_y)
        )

def exec(cmd):
    pipe = Popen(cmd.split(' '), stdin=PIPE, stdout=PIPE, stderr=PIPE)
    output, error = pipe.communicate()
    return_code = pipe.returncode
    return Command(output, error, return_code)

def debug(cmd):
    print("[DEBUG] Output: %s" % cmd.output)
    print("[DEBUG] Error: %s" % cmd.error)
    print("[DEBUG] Return code: %s" % cmd.return_code)

# Check arguments
if len(argv) < 2:
    print("Usage: %s <window>" % argv[0])
    exit()

args_key = argv[1]

# Find current active windows
active_windows = []
for window in exec("wmctrl -lG").output.strip().split('\n'):
    window_id = window[0:10]
    pos_x = window[14:18]
    pos_y = window[19:23]
    size_x = window[24:28]
    size_y = window[29:33]
    title = window[41:]
    active_windows.append(Window(window_id, title, pos_x, pos_y, size_x, size_y))

# Select config from args key
config_windows = []
configs = open('/home/anon/Templates/shuffler/window.config', 'r')
for config in configs:
    # Skip comments and blank lines
    if config[0] == '#' or config[0] == '\n':
        continue

    config = config.split(',')

    # Match selected config
    key = config[0].strip()
    if (key != args_key):
        continue

    title = config[1].strip()
    pos_x = config[2].strip()
    pos_y = config[3].strip()
    size_x = config[4].strip()
    size_y = config[5].strip()
    config_windows.append(Window('0x0', title, pos_x, pos_y, size_x, size_y))

# Error handle zero or multiple matches
if (len(config_windows) == 0):
    print("[ERROR] Found no config for key: %s" % args_key)
    exit()
elif (len(config_windows) > 1):
    print("[ERROR] Found multiple windows for key: %s" % args_key)
    exit()

window = config_windows[0]

# Find window key
for active_window in active_windows:
    if (window.title in active_window.title):
        window.window_id = active_window.window_id

if (window.window_id == "0x0"):
    print("[ERROR] Failed to find active window for key: %s" % args_key)
    exit()

move_cmd = exec('wmctrl -i -r %s -e 0,%s,%s,%s,%s' % (window.window_id, window.pos_x, window.pos_y,window.size_x, window.size_y))
debug(move_cmd)