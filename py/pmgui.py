#!/usr/bin/env python

# Poor Man's GUI

import re
import io, os, sys, time, select, socket
import binascii

import Tkinter

from PIL import Image, ImageTk

# components are strings like:
# 
# 'image <width> <height>'	'image 640 480
# 'label <text>'			'label field of view (fov):'
# 'slider <min> <max>'		'slider 0 1000'
#
class PmGui():
	def __init__(self, widg_txt):
		self.root = Tkinter.Tk()
		self.widgets_in = []
		self.widgets_out = []
	
		for c in widg_txt:
			m = re.match(r'^window (\d+) (\d+) (.*)$', c)
			if m:
				(width, height, title) = m.group(1,2,3)
				self.root.geometry('%sx%s' % (width, height))
				self.root.title(title)
				continue

			m = re.match(r'^slider (.+) (.+) (.+) (.+)$', c)
			if m:
				(minval, maxval, resolution, default) = m.group(1,2,3,4)
				widg = Tkinter.Scale(self.root, from_=minval, to=maxval, resolution=float(resolution), orient=Tkinter.HORIZONTAL)
				widg.set(float(default))
				widg.pack()
				self.widgets_in.append(('slider', widg))
				continue
	
			m = re.match(r'^label (.*)$', c)
			if m:
				ltext = m.group(1)
				widg = Tkinter.Label(self.root, text=ltext)
				widg.pack()
				continue

			m = re.match(r'^image (\d+) (\d+)$', c)
			if m:
				(w, h) = map(int, m.group(1,2))

				# create photo image
				img = Image.new('RGB', (int(w), int(h)))
				px = img.load()
				for i in range(w):
					for j in range(h):
						px[i,j] = (0xFF,0,0)
				photo = ImageTk.PhotoImage(img)

				# create canvas
				canv = Tkinter.Canvas(self.root, width=w, height=h, borderwidth=0, highlightthickness=0)
				canv.create_image(0, 0, anchor=Tkinter.NW, image=photo)
				canv.pack()

				self.widgets_out.append(('image', w, h, canv, photo))
				continue

			raise Exception('unknown GUI element: %s' % c)

	def get(self):
		self.root.update_idletasks()
		self.root.update()

		return map(lambda x: x[1].get(), self.widgets_in)

	def set(self, values):
		for (i,wtuple) in enumerate(self.widgets_out):

			value = values[0]

			wtype = wtuple[0]
			if wtype == 'image':
				(wtype, w, h, canvas, photo) = wtuple

				# photo image
				img = Image.new('RGB', (w, h))
				px = img.load()
				for col in range(w):
					for row in range(h):
						px[col,row] = values[row*w + col]
				photo = ImageTk.PhotoImage(img)

				# delete canvas members, add back
				canvas.delete(Tkinter.ALL)
				canvas.create_image(0, 0, anchor=Tkinter.NW, image=photo)

				# save tuple, holding photo reference
				self.widgets_out[i] = (wtype, w, h, canvas, photo)

			values = values[1:]

if __name__ == '__main__':
	widgets_txt = [	
			'window 640 480 GUI test',
			'label red:',
			'slider 0 255 1 50',
			'label green:',
			'slider 0 255 1 150',
			'label blue:',
			'slider 0 255 1 250',
			'image 320 160'
		]

	pmg = PmGui(widgets_txt)

	i = 0
	while True:
		(red, green, blue) = pmg.get()

		print 'invocation %d: got back values: %d %d %d' % (i, red, green, blue)

		data = [(red, green, blue)]*320*160
		pmg.set(data)

		i += 1
