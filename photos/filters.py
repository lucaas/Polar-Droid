from PIL import Image, ImageChops, ImageEnhance, ImageOps, ImageMath, ImageFilter, ImageDraw

from polardroid import settings

#filter_path = "%s%s" % settings.MEDIA_ROOT, "filters/"
filter_path = '/home/lucas/django/polardroid/uploads/filters/'
R,G,B = (0,1,2)
size = (640,640)

def add_image(img, file, amount=1.0):
	path = "%s%s" % (filter_path, file)
	filterImg = Image.open(path)
	
	result = ImageChops.add(filterImg, img)
	
	if (amount != 1.0):
		result = Image.blend(img, result, amount)
	
	return result
	
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

def overlay_helper(a,b):
	mask = b.point(lambda i: i < 128 and 255)
	dark = ImageMath.eval("2 * B * L / 255", L=a, B=b).convert('L')
	light = ImageMath.eval("255 - 2 * (255 - B) * (255 - L) / 255", L=a, B=b).convert('L')
	return Image.composite(dark, light, mask)
	
def overlay_blend(a, b, amount=1.0):
	a.load()
	b.load()
	ra,ga,ba = a.split()
	rb,gb,bb = b.split()
	
	rc = overlay_helper(ra,rb)
	gc = overlay_helper(ga,gb)
	bc = overlay_helper(ba,bb)
	
	result = Image.merge("RGB", (rc, gc, bc))
	if (amount != 1.0):
		result = Image.blend(a, result, amount)
		
	return result
	
def army(img):

	# Darken shadows
	layer1 = color(img, 0.8)
	result = ImageChops.multiply(img, layer1)

	# Lighten Highlights
	layer2 = color(img, 0.8)
	result = Image.blend(result, ImageChops.add(result, layer2), 0.5)
	
	# Overlay blend
	result = overlay_blend(img, result)

	# Tint Orange
	r = ImageChops.constant(img, 255)
	g = ImageChops.constant(img, 150)
	b = ImageChops.constant(img, 80)
	orange = Image.merge("RGB",(r,g,b))
	result = Image.blend(overlay_blend(orange, result), result, 0.6)

	return result
	
def cyan_glow(img):
	glow = img.filter(ImageFilter.BLUR).filter(ImageFilter.BLUR)
	glow = brightness(glow, 1.25)
	result = Image.blend(overlay_blend(glow, img), img, 0.3)
	
	# Tint Cyan
	r = ImageChops.constant(img, 64)
	g = ImageChops.constant(img, 255)
	b = ImageChops.constant(img, 255)
	cyan = Image.merge("RGB",(r,g,b))
	result = Image.blend(overlay_blend(cyan, result), result, 0.8)
	result = apply_vignette(result, 0.5)
	return result
	
def oldie(img):

	# desaturate
	img = color(img, 0.1)
	
	# Tint Brown
	r = ImageChops.constant(img, 230)
	g = ImageChops.constant(img, 200)
	b = ImageChops.constant(img, 170)
	tint = Image.merge("RGB",(r,g,b))
	result = ImageChops.multiply(img, tint)
	
	# add noise and texture
	result = add_image(result, "add_noise_gradient_2.png")
	result = multiply_image(result, "stains_and_torn_bottom.png")

	return result

def halftone(img):
	smallsize = 80
	factor = int(size[0] / smallsize)
	small = img.resize((smallsize, smallsize), Image.ANTIALIAS)
	smallval = small.load()
	
	result_r = Image.new("L", size, 255)
	result_g = Image.new("L", size, 255)
	result_b = Image.new("L", size, 255)
	draw_r = ImageDraw.Draw(result_r)
	draw_g = ImageDraw.Draw(result_g)
	draw_b = ImageDraw.Draw(result_b)
	
	for i in range(smallsize):
		for j in range(smallsize + 2):
			try:
				values = smallval[i,j]
			except IndexError:
				values = smallval[i,j-(j-smallsize + 1)]
				
			size_r = 1.25*int(factor*(255-values[0])/255)
			size_g = 1.25*int(factor*(255-values[1])/255)
			size_b = 1.25*int(factor*(255-values[2])/255)

			xy_r = (i*factor, j*factor - i%8)
			xy_g = (i*factor, j*factor - i%7)
			xy_b = (i*factor, j*factor - i%3)
			
			draw_r.ellipse((xy_r[0], xy_r[1], xy_r[0]+size_r, xy_r[1]+size_r), fill=0)
			draw_g.ellipse((xy_g[0], xy_g[1], xy_g[0]+size_g, xy_g[1]+size_g), fill=0)
			draw_b.ellipse((xy_b[0], xy_b[1], xy_b[0]+size_b, xy_b[1]+size_b), fill=0)			
		
			
	result = Image.merge("RGB", (result_r, result_g, result_b))
	return overlay_blend(img, result, 0.5)
			
		