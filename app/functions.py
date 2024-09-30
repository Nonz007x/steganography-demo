from PIL import Image
import numpy as np
import math
import base64
from io import BytesIO

def text_to_image(text, image_name):
  grayscale_values = atoi(text)

  length = len(grayscale_values)
  side_length = math.ceil(math.sqrt(length))

  while len(grayscale_values) < side_length ** 2:
    grayscale_values.append(255)

  grayscale_arr = np.array(grayscale_values, dtype=np.uint8)
  image_arr = grayscale_arr.reshape((side_length, side_length))

  img = Image.fromarray(image_arr, 'L')
  img.save(f'{image_name}.png')
  print(f"Image saved as {image_name}.png")

def read_image(image_name):
  img = Image.open(image_name)
  img_arr = np.array(img)
  return [x for x in img_arr.flatten() if x != 0]

def lsb_encode(text, b64, image_name='image'):
  text_num = [ord(x) for x in text] 
  text_chunk = []
  
  for num in text_num:
    chunk = []
    while num > 0:
      chunk.append(num & 0b11)
      num >>= 2
    while len(chunk) < 4:  # Divide each number to 4 chunks 2 bits per chunk
      chunk.append(0)  # Pad with zeros
    text_chunk.extend(reversed(chunk))

  terminator = [1, 3, 3, 3]
  text_chunk.extend(terminator)
  
  image = b64toi(b64)
  image_arr = np.array(image)
  height, width = image_arr.shape[:2]

  if len(text_chunk) > height * width * (3 if image_arr.ndim == 3 else 1):
    print('Image is too small!')
    return None

  if image_arr.ndim == 3: # RGB
    for i in range(len(text_chunk)):
      pixel_index = i // 3  # Each pixel has 3 channels (R, G, B)
      channel_index = i % 3  # Cycle through 0 (R), 1 (G), 2 (B)

      row = pixel_index // width
      col = pixel_index % width

      image_arr[row, col, channel_index] &= 0b11111100
      image_arr[row, col, channel_index] |= text_chunk[i]
  else:  # Grayscale
    for i in range(len(text_chunk)):
      row = i // width
      col = i % width
      image_arr[row, col] &= 0b11111100
      image_arr[row, col] |= text_chunk[i]

  img = Image.fromarray(image_arr.astype(np.uint8), 'RGB' if image_arr.ndim == 3 else 'L')
  # img.save(f'{image_name}.png')
  print(f"Image saved as {image_name}.png")
  return img

def lsb_decode(image_path):
  text_chunk = read_image(image_path)
  text_chunk = [x & 0b11 for x in text_chunk]
  text = list()

  for i in range(len(text_chunk)):
    text_idx = i // 4
    if text_idx >= len(text):
      text.append(0)
    text[text_idx] += text_chunk[i] << (6 - (i % 4) * 2)
    
    if i % 4 == 3 and text[text_idx] == 127:  # Null terminator check
      text[text_idx] = 0
      break

  return text

def itoa(i_arr):
  c_arr = [chr(num) for num in i_arr]
  return ''.join(c_arr)

def atoi(c_arr):
  return [ord(char) for char in c_arr]

def b64toi(base64_string):
  base64_data = base64_string.split(',')[1]
  image_data = base64.b64decode(base64_data)
  image = Image.open(BytesIO(image_data))
  image_array = np.array(image)

  return image_array