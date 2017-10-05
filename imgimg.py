from PIL import Image, ImageDraw
import sys
import math

def interpolate_clr(f, b, a):
	R = a[0]*f + b[0]*(1-f)
	G = a[1]*f + b[1]*(1-f)
	B = a[2]*f + b[2]*(1-f)

	return (int(R), int(G), int(B))

def to_clr_m(f):
	blue = (0, 0, 255)
	red = (255, 0, 0)
	green = (0, 255, 0)
	f = 1-f
	R = 255.0 * (1-f*f)
	G = 255.0 * (1-f)
	B = 255.0 * f

	print (R,G,B)

	return (int(R),int(G),int(B))

def to_clr(f):
	if f >= 0.00 and f <= 0.25:
		return interpolate_clr(f/0.25, (0, 0, 128), (0, 255, 255))
	elif f >= 0.25 and f <= 0.5:
		f -= 0.25
		return interpolate_clr(f/0.25, (0, 255, 255), (0, 255, 0))
	elif f >= 0.5 and f <= 0.75:
		f -= 0.5
		return interpolate_clr(f/0.25, (0, 255, 0), (255, 255, 0))
	else:
		f -= 0.75
		return interpolate_clr(f/0.25, (255, 255, 0), (255, 0, 0))

	return (0,0,0)

def open_rgb(path):
	return Image.open(path).convert('RGB')

def calc_hist(im, method):
	(w,h) = im.size

	hist = [0]*(get_l_max(method)+1)

	y = 0
	while y < h:
		x = 0
		while x < w:
			(r,g,b) = im.getpixel((x,y))
			l = get_l((r,g,b), method)

			hist[l] += 1

			x += 1
		y += 1

	return hist

def calc_histbs(im, method, bs = 1):
	(w,h) = im.size

	l_max = get_l_max(method)
	hist = [0]*(l_max+1)

	y = 0
	while y < h:
		x = 0
		while x < w:
			lsum = 0
			n = 0
			ref_pixel = im.getpixel((x,y))
			(ref_r, ref_g, ref_b) = ref_pixel

			dy = -bs
			while dy <= bs:
				dx = -bs
				while dx <= bs:
					if dy == 0 and dx == 0: dx += 1; continue
					if x+dx < 0 or x+dx >= w: dx += 1; continue
					if y+dy < 0 or y+dy >= h: dx += 1; continue

					n += 1

					(r,g,b) = im.getpixel((x+dx,y+dy))
					l = get_l((ref_r-r,ref_g-g,ref_b-b), method)

					if l < 0: l = 0
					if l > l_max: l = l_max
		
					lsum += l

					dx += 1
				dy += 1

			lsum /= n
			hist[lsum] += 1

			x += 1
		y += 1

	return hist

def calc_hists(im):
	(w, h) = im.size

	rhist = [0]*256
	ghist = [0]*256
	bhist = [0]*256
	ahist = [0]*256
	dhist = [0]*442
	maxhist = [0]*256
	minhist = [0]*256

	y = 0
	while y < h:
		x = 0
		while x < w:
			(r,g,b) = im.getpixel((x,y))
			a = int((r+g+b)/3)
			d = int(math.sqrt(r*r + g*g + b*b))

			rhist[r] += 1
			ghist[g] += 1
			bhist[b] += 1
			ahist[a] += 1
			dhist[d] += 1

			mx = max(r,max(g,b))
			mi = min(r,min(g,b))

			maxhist[mx] += 1
			minhist[mi] += 1

			x += 1
		y += 1

	return (rhist, ghist, bhist, ahist, dhist, maxhist, minhist)

def f_version(args):
	print "0.0.0.0.0"
	return 0

def f_hist(args):
	if len(args) != 4:
		print "Correct args: <path> <output> <heat> <method>"
		return -1

	im = open_rgb(args[0])
	method = args[3]
	the_hist = calc_hist(im, method)
	m = float(max(the_hist))

	hist = Image.new("RGB", (len(the_hist)*2, 100))
	drw = ImageDraw.Draw(hist)

	x = 0
	while x < len(the_hist):
		freq = the_hist[x]/m
		clr = (128, 128, 128)
		if args[2] == 'yes':
			clr = to_clr(freq)
		drw.rectangle([(x*2, 100-(freq*100)),(x*2+2, 100)], fill=clr)
		x += 1

	hist.save(args[1], 'PNG')

	return 0

def f_histbs(args):
	if len(args) != 4:
		print "Correct args: <path> <output> <heat> <method>"
		return -1

	im = open_rgb(args[0])
	method = args[3]
	the_hist = calc_histbs(im, method)
	m = float(max(the_hist))

	hist = Image.new("RGB", (len(the_hist)*2, 100))
	drw = ImageDraw.Draw(hist)

	x = 0
	while x < len(the_hist):
		freq = the_hist[x]/m
		clr = (128, 128, 128)
		if args[2] == 'yes':
			clr = to_clr(freq)
		drw.rectangle([(x*2, 100-(freq*100)),(x*2+2, 100)], fill=clr)
		x += 1

	hist.save(args[1], 'PNG')

	return 0

def f_dhist(args):
	if len(args) != 3:
		print "Correct args: <path> <output> <heat>"
		return -1

	im = open_rgb(args[0])
	dhist = calc_hists(im)[4]
	m = float(max(dhist))

	hist = Image.new("RGB", (442*2, 100))
	drw = ImageDraw.Draw(hist)

	x = 0
	while x < len(dhist):
		freq = dhist[x]/m
		clr = (128, 128, 128)
		if args[2] == 'yes':
			clr = to_clr(freq)
		drw.rectangle([(x*2, 100-(freq*100)),(x*2+2, 100)], fill=clr)
		x += 1

	hist.save(args[1], 'PNG')

	return 0

def get_l_max(method):
	if method == "d":
		return 441
	return 255

def get_l(rgb, method):
	l = 0
	(r,g,b) = rgb

	if method == "rgb":
		l = int((r+g+b)/3)
	elif method == "rg":
		l = int((r+g)/2)
	elif method == "rb":
		l = int((r+b)/2)
	elif method == "gb":
		l = int((g+b)/2)
	elif method == "r":
		l = r
	elif method == "g":
		l = g
	elif method == "b":
		l = b
	elif method == "d":
		d = int(math.sqrt(r*r + g*g + b*b))
		l = d
	elif method == "max":
		l = max(r,max(g,b))
	elif method == "min":
		l = min(r,min(g,b))
	elif method == "minmax":
		mi = min(r,min(g,b))
		mx = max(r,max(g,b))
		l = int((mi+mx)/2)
	elif method == "y":
		l = int(0.2616*r + 0.7152*g + 0.0722*b)
	elif method == "Y":
		l = int(0.2999*r + 0.587*g + 0.114*b)
	elif method == "r+g":
		l = int(r+g)
		if l >= 255: l = 255
	elif method == "r+b":
		l = int(r+b)
		if l >= 255: l = 255
	elif method == "g+b":
		l = int(g+b)
		if l >= 255: l = 255
	elif method == "r/g":
		if g == 0: g = 1
		g = float(g)
		l = int((r/g)*255.0)
	elif method == "r/b":
		if b == 0: b = 1
		b = float(b)
		l = int((r/b)*255.0)
	elif method == "g/b":
		if b == 0: b = 1
		b = float(b)
		l = int((g/b)*255.0)
	elif method == "r+g+b":
		l = int(r+g+b)
	elif method == "rd":
		l = int(abs(r))
	elif method == "gd":
		l = int(abs(g))
	elif method == "bd":
		l = int(abs(b))

	return l

def f_hist2d(args):
	if len(args) != 3:
		print "Correct args: <path> <output> <method>"
		return -1

	im = open_rgb(args[0])
	(w,h) = im.size
	out = Image.new("RGB", (w,h))
	method = args[2]

	hist = calc_hist(im, method)
	mx = float(max(hist))

	y = 0
	while y < h:
		x = 0
		while x < w:
			(r,g,b) = im.getpixel((x,y))
			l = get_l((r,g,b), method)
			
			p = hist[l]/mx
			p = int(p * 255.0)

			out.putpixel((x,y), (p,p,p))

			x += 1
		y += 1

	out.save(args[1], 'PNG')

def f_hist2dbs(args, bs = 1):
	if len(args) != 3:
		print "Correct args: <path> <output> <method>"
		return -1

	im = open_rgb(args[0])
	(w,h) = im.size
	out = Image.new("RGB", (w,h))
	method = args[2]

	hist = calc_histbs(im, method)
	mx = float(max(hist))
	print mx
	l_max = get_l_max(method)

	y = 0
	while y < h:
		x = 0
		while x < w:
			lsum = 0
			n = 0
			ref_pixel = im.getpixel((x,y))
			(ref_r, ref_g, ref_b) = ref_pixel

			dy = -bs
			while dy <= bs:
				dx = -bs
				while dx <= bs:
					if dy == 0 and dx == 0: dx += 1; continue
					if x+dx < 0 or x+dx >= w: dx += 1; continue
					if y+dy < 0 or y+dy >= h: dx += 1; continue

					n += 1

					(r,g,b) = im.getpixel((x+dx,y+dy))
					l = get_l((ref_r-r,ref_g-g,ref_b-b), method)

					if l < 0: l = 0
					if l > l_max: l = l_max
		
					lsum += l

					dx += 1
				dy += 1

			lsum /= n

			p = hist[lsum]/mx
			p = int(p * 255.0)

			out.putpixel((x,y), (p,p,p))

			x += 1
		y += 1

	out.save(args[1], 'PNG')

def f_trshldl(args):
	if len(args) != 4:
		print "Correct args: <path> <output> <method> <threshold>"

	threshold = float(args[3])
	method = args[2]

	im = open_rgb(args[0])
	(w,h) = im.size
	out = Image.new("RGB", (w,h))

	y = 0
	while y < h:
		x = 0
		while x < w:
			(r,g,b) = im.getpixel((x,y))

			l = 0

			l = get_l((r,g,b), method)

			if l < threshold:
				out.putpixel((x,y),(l,l,l))
			else:
				out.putpixel((x,y),(255,255,255))

			x += 1
		y += 1

	out.save(args[1], 'PNG')

def f_to_gray(args):
	if len(args) != 3:
		print "Correct args: <path> <output> <method>"
		return -1

	im = open_rgb(args[0])
	(w,h) = im.size
	out = Image.new("RGB", (w,h))
	method = args[2]

	y = 0
	while y < h:
		x = 0
		while x < w:
			(r,g,b) = im.getpixel((x,y))

			l = 0

			l = get_l((r,g,b), method)

			out.putpixel((x,y),(l,l,l))

			x += 1
		y += 1

	out.save(args[1], 'PNG')

def main(func, args):
	funcs = {
		"version" : f_version,
		"dhist" : f_dhist,
		"hist"  : f_hist,
		"histbs" : f_histbs,
		"to_gray" : f_to_gray,
		"hist2d" : f_hist2d,
		"hst2dbs" : f_hist2dbs,
		"trshldl" : f_trshldl,
	}

	return (funcs[func])(args)

def usage():
	print "Correct usage: imgimg <function> <args>"
	print " .[ Functions ]. <function>"
	print "   version print the version"
	print "   dhist   generate histogram of sqrt(r*r + g*g + b*b)"
	print "   hist    generate histogram"
	print "   histbs  generate histogram"
	print "   hist2d  generate a pseudo-3d histogram (projected onto a 2d surface)"
	print "   heatmap convert image to heatmap"
	print "   pixeq   compare images pixel by pixel removing all pixels that do not match"
	print "   pixdiff diff images pixel by pixel abs(p1 - p2)"
	print "   pixxor	xor each pixel by a value"
	print "   pixand  and each pixel by a value"
	print "   pixxor  or each pixel by a value"
	print "   pixneg  negate each pixel"
	print "   pixlsh  left shift each pixel by a value"
	print "   pixrsh  right shift each pixel by a value"
	print "   to_gray convert to grayscale"
	print "   to_rgb  convert three grayscale images to an rgb image"
	print "           first image is r, second image is b, third image is g"
	print "   trshldl only keep pixels that are below a certain threshold"
	print " .[ Methods ]. <args:method>"
	print "   rgb     average of r,g,b"
	print "   rg      average of r,g"
	print "   rb      average of r,b"
	print "   bg      average of b,g"
	print "   max     maximum of r,g,b"
	print "   min     minimum of r,g,b"
	print "   minmax  average of maximum of r,g,b and minimum of r,g,b"
	print "   d       use sqrt(r*r + g*g + b*b)"
	print "   rd      use abs(r)"
	print "   gd      use abs(g)"
	print "   bd      use abs(b)"
	print "   r       r only"
	print "   g       g only"
	print "   b       b only"
	print "   y       use 0.2616*r + 0.7152*g + 0.0722*b"
	print "   Y       use 0.2999*r + 0.587*g + 0.114*b"
	print "   r+g     use r+g"
	print "   r+b     use r+b"
	print "   g+b     use g+b"
	print "   r/g     use r/g"
	print "   r/b     use r/b"
	print "   g/b     use g/b"
	print "   :u;v;x  use u*r + v*g + x*b"

if __name__ == "__main__":
	if len(sys.argv) < 3:
		usage()
	else:
		main(sys.argv[1], sys.argv[2:])


