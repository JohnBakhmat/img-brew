import numpy as np
from PIL import Image
import colorsys as cs
import os
import math
import time
from IPython.display import clear_output

time_start = time.time()

sector_size = 4
input_file_name = "./john.png"

pixels = np.asarray(Image.open(input_file_name))

res = np.zeros_like(pixels)
(height, width, bands) = pixels.shape

time_read_file = time.time()

sector_hash_map = {}


def process_sector(sector):
    (width, height, bands) = sector.shape
    if width == 0 or height == 0:
        return None
    avg_color = np.mean(sector, axis=(0, 1))
    std = np.std(sector)
    return (avg_color, std)

def clamp (val, min, max):
    if val < min:
        return min
    if val > max:
        return max
    return val



def kuwahara(dataset, i, j):
    def check_cached(left, right, top, bottom):
            if (left, right, top, bottom) in sector_hash_map:
                return (
                    True,
                    (left, right, top, bottom),
                    sector_hash_map[(left, right, top, bottom)],
                )
            else:
                return (False, (left, right, top, bottom), dataset[left:right, top:bottom])
                
    left = clamp(i - sector_size, 0, height)
    right = clamp(i + sector_size, 0, height)
    top = clamp(j - sector_size, 0, width)
    bottom = clamp(j + sector_size, 0, width)
    
    sector1 = check_cached(left, i, top, j)
    sector2 = check_cached(i, right, top, j)
    sector3 = check_cached(i, right, j, bottom)
    sector4 = check_cached(left, i, j, bottom)

    sectors = [sector1, sector2, sector3, sector4]
    processed_sectors = [0, 0, 0, 0]

    for i in range(4):
        if sectors[i][0]:
            processed_sectors[i] = sectors[i][2]
        else:
            data = process_sector(sectors[i][2])
            processed_sectors[i] = data
            sector_hash_map[sectors[i][1]] = data

    clr = [0, 0, 0]
    minStd = 5000

    for i in range(4):
        if processed_sectors[i] == None:
            continue
        if processed_sectors[i][1] <= minStd:
            minStd = processed_sectors[i][1]
            clr = processed_sectors[i][0]
    return clr


time_start_processing = time.time()

end = height * width
prev_percent = 0
for i in range(height):
    for j in range(width):
        cur = height * i + j
        percent = math.floor((cur / end * 100))
        if prev_percent != percent:
            prev_percent = percent
            clear_output(wait=False)
            print(percent, "%")

        res[i, j] = kuwahara(pixels, i, j)

time_end_processing = time.time()


Image.fromarray(res).save(
    os.path.splitext(input_file_name)[0]
    + "optimized-clamp-out-"
    + str(sector_size)
    + "px"
    + ".png"
)
time_save = time.time()

print(
    "Time to read file: ",
    time_read_file - time_start,
    "\nTime to process: ",
    time_end_processing - time_start_processing,
    "\nTime to save file: ",
    time_save - time_end_processing,
    "\nTotal time: ",
    time_save - time_start,
)
