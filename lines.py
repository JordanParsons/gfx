import cv2
import numpy as np
import random
import time
import hashlib
from PIL import Image, ImageDraw, ImageColor

tw = 3840  # Output Width
th = 2160  # Output Height
margin_bottom = 500  # How far up from the bottom can the last curve be
curve_area_height = 750  # How much space can be taken up by ridges
peak_size_range = (-75, 200)  # How much can a ridge move up or down each step
peak_spacing_jitter = 50  # How much can we move the tips around so they dont line up
max_peaks = 9
min_peaks = 3
background = (25, 25, 25, 255)

colors = [
    ImageColor.getrgb('#F2F2F2'),
    ImageColor.getrgb('#8C8C88'),
    ImageColor.getrgb('#9DA65D'),
    ImageColor.getrgb('#6C733D'),
    ImageColor.getrgb('#202426'),
    background
]

sf = 2  # scale factor for smoothing

w = tw * sf  # rendering width
h = th * sf  # rendering height


def getImage():
  print('\tGenerating image...')
  def getPeaks(sx, ex, h, count):
    pts = []
    width = ex - sx
    spacing = int(width / count)
    for x in range(count+1):
      xPos = x * spacing
      if x > 0 and x < count:
        xPos += random.randint(-peak_spacing_jitter, peak_spacing_jitter)
      pts.append(
          (xPos, h+(random.randint(peak_size_range[0], peak_size_range[1]))))
    return pts

  def addEnds(pts):
    pts.append((w, h))
    pts.append((0, h))
    return pts

  img = Image.new('RGBA', (w, h), background)  # make a blank
  draw = ImageDraw.Draw(img)  # make the draw object

  # calc where curves can happen
  curve_range = (h-curve_area_height-margin_bottom, h-margin_bottom)
  curve_starts = [random.randint(curve_range[0], curve_range[1])
                  for _ in range(len(colors))]
  curve_starts.sort(reverse=False)  # sort so colors lay correctly

  # Draw the ridges
  for x in range(len(colors)):
    # calc points
    pts = addEnds(
        getPeaks(0, w, curve_starts[x], random.randint(min_peaks, max_peaks)))
    draw.polygon(pts, fill=colors[x])  # draw the polygon

  # return a smoothed image
  return img.resize((tw, th), Image.Resampling.LANCZOS)

print('Press [s] to save an image, [q] to quit, [any] key to make a new one...')

# Convert that image for cv2 imshow. 
# It needs BGRA, who things BGRA is a good idea? No one...
output = cv2.cvtColor(np.array(getImage()), cv2.COLOR_RGBA2BGRA)

# main Loop
try:
  while True:
    # Show the last image
    cv2.imshow('Peaks', output)
    key = cv2.waitKey(0) & 0xFF
    if key == ord('q'):  # quit!
      print('\tExiting...')
      break
    elif key == ord('s'):  # save!
      rand_junk = hashlib.md5(f'{time.time()}'.encode('utf-8')).hexdigest()[:8]
      name = f'out/{rand_junk}_layers.png'
      print(f'\tSaving: [{name}]')
      cv2.imwrite(name, output)
    else:  # gen a new one after pressing any key
      output = np.array(getImage())
      output = cv2.cvtColor(output, cv2.COLOR_RGBA2BGRA)
except KeyboardInterrupt:
  cv2.destroyAllWindows()
finally:
  cv2.destroyAllWindows()
