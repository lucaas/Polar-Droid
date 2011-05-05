from PIL import Image, ImageChops, ImageEnhance, ImageOps

from polardroid import settings

#filter_path = "%s%s" % settings.MEDIA_ROOT, "filters/"
filter_path = '/home/lucas/django/polardroid/uploads/filters/'
R,G,B = (0,1,2)


def multiply_image(img, file, amount=1.0):
	path = "%s%s" % (filter_path, file)
	filterImg = Image.open(path)
	
	if (amount != 1.0):
		filterImg = ImageChops.add(filterImg, ImageChops.constant(filterImg, (1-amount)*255).convert("RGB"))
	
	return ImageChops.multiply(filterImg, img)
	

	
def apply_vignette(img, amount=1.0):
	return multiply_image(img, "vignette.png", amount)
	
def contrast(img, amount=1.3):
	enhancer = ImageEnhance.Contrast(img)
	return enhancer.enhance(amount)

def color(img, amount=1.3):
	enhancer = ImageEnhance.Color(img)
	return enhancer.enhance(amount)
	
def brightness(img, amount=1.3):
	enhancer = ImageEnhance.Brightness(img)
	return enhancer.enhance(amount)
	
def lomo(img):
	img = apply_vignette(img, 0.5)
	img = contrast(img)
	img = color(img, 0.6)
	return img
	
def bw(img):
	img = multiply_image(img, "noise.png")
	img = apply_vignette(img, 0.5)
	img = contrast(img, 1.5)
	return img.convert("L")
	
def bw2(img):
	img = multiply_image(img, "noise.png")
	img = brightness(img, 0.6)
	img = contrast(img, 1.4)
	return img.convert("L")
	
def agfa(img):
	img = multiply_image(img, "noise.png")
	img = apply_vignette(img, 0.75)
	img = contrast(img)
	img.load()
	r,g,b = img.split()
	g = brightness(g, 1.2)
	b = brightness(b, 1.2)
	r = brightness(r, 0.7)
	r = ImageChops.add(r, ImageChops.constant(r, 0.3*255))
	img = Image.merge("RGB", (r,g,b))
	img = color(img, 0.7)
	return img