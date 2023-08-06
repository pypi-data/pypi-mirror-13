import numpy as np

# Uses the standard RGB to gray formula from:
# http://www.johndcook.com/blog/2009/08/24/algorithms-convert-color-grayscale/
# In other words: 0.21R + 0.72G + 0.07B
# Input: RGB numpy array
# Output: modified monochrome numpy array
# To Do: Add other algorithms for rgbtogray
def rgb2gray(img):
	ret = np.zeros(img.shape[0:2])
	red = img[:,:,0]
	green = img[:,:,1]
	blue = img[:,:,2]

	ret = red * 0.21 + green * 0.72 + blue * 0.07

	return ret

# Inserts a square from one image into the other dead center by default
# Input: two monochrome numpy arrays, size of square
# Output: One monochrome numpy array.
# To Do: Implement it for RGB numpy arrays
def square2Image(img1, img2, size):
	l1 = len(img1)
	w1 = len(img1[0])

	l2 = len(img2)
	w2 = len(img2[0])

	square = img1[(l1 - size)/2: (l1 + size)/2, (w1 - size)/2 : (w1 + size)/2]

	img2[(l2 - size)/2: (l2 + size)/2, (w2 - size)/2: (w2 + size)/2] = square

	return img2

# Adds gaussian noise to each of the color channels
# Input: one RGB numpy array
# Output: one RGB numpy array
# To Do: Make gaussian bw sharpener based on this function
def gaussianNoise(img, multiplier):
	noise = np.random.standard_normal(img.shape)
	processed = (img + multiplier * noise)

	minimum = np.min(processed)
	processed = processed - minimum

	maximum = np.max(processed)

	normalized = ((processed / maximum) * 255).astype(np.uint8)

	return normalized

# Convolves two inputs, in particular an image and a filter
# Input: two monochrome numpy arrays, first one the image, second one the filter
# Output: One monochrome numpy array
def convolution(img, f):
	ret = np.zeros(img.shape, dtype=np.uint8)
	f = np.fliplr(np.flipud(f))

	filter_size = f.shape
	img_size = img.shape

	max_size = int(np.floor(max(filter_size)/2))

	img = np.pad(img, max_size, mode="constant")

	for img_y in range(0,img_size[0]):
		for img_x in range(0,img_size[1]):
			result = 0
			for filter_y in range(0,filter_size[0]):
				for filter_x in range(0,filter_size[1]):
					img_index_y = img_y + max_size - int(np.floor(filter_size[0]/2)) + filter_y
					img_index_x = img_x + max_size - int(np.floor(filter_size[1]/2)) + filter_x
					result = result + f[filter_y][filter_x] * img[img_index_y][img_index_x]
			ret[img_y][img_x] = result

	return ret
