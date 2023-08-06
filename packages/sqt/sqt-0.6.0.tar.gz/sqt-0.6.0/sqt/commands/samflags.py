#!/usr/bin/env python3
import sys

flag = int(sys.argv[1])

FLAGS = [
	(0x0001, 'p', 'paired/multiple segments'),
	(0x0002, 'P', 'proper pair'),
	(0x0004, 'u', 'segment unmapped'),
	(0x0008, 'U', 'next segment unmapped'),
	(0x0010, 'r', 'segment is reverse complemented'),
	(0x0020, 'R', 'next segment (mate) is reverse complemented'),
	(0x0040, '1', 'segment is first (first read in pair)'),
	(0x0080, '2', 'segment is last (second read in pair)'),
	(0x0100, 's', 'secondary alignment'),
	(0x0200, 'f', 'fails quality control'),
	(0x0400, 'd', 'PCR or optical duplicate'),
	(0x0800, '', 'supplementary alignment'),
]

short = ''
for f, char, description in FLAGS:
	if flag & f != 0:
		short += char
		print('*', description)

print(short)
