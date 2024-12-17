import os, shutil
from tqdm import tqdm

def swap_underscore_and_dash(string):
    return string.replace("-", ";").replace("_", "-").replace(";", "_")

# path = "./data/individual"
# for f in tqdm(os.listdir(path)):
#     old_path = os.path.join(path, f)
#     new_path = os.path.join(path, swap_underscore_and_dash(f))
#     _ = shutil.move(old_path, new_path)
