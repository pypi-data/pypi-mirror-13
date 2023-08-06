#!/usr/bin/env python

"""Produce CSV listings of board physical locations."""

import argparse

from spinner.utils import folded_torus

from spinner import transforms
from spinner import topology

from spinner.scripts import arguments


def main(args=None):
	parser = argparse.ArgumentParser(
		description="Produce CSV listing of board physical locations.")
	arguments.add_version_args(parser)
	arguments.add_topology_args(parser)
	arguments.add_cabinet_args(parser)
	
	# Process command-line arguments
	args = parser.parse_args(args)
	(w, h), transformation, uncrinkle_direction, folds =\
		arguments.get_topology_from_args(parser, args)
	
	cabinet, num_frames = arguments.get_cabinets_from_args(parser, args)
	
	# Generate folded system
	hex_boards, folded_boards = folded_torus(w, h,
	                                         transformation,
	                                         uncrinkle_direction,
	                                         folds)
	
	# Divide into cabinets
	cabinetised_boards = transforms.cabinetise(folded_boards,
	                                           cabinet.num_cabinets,
	                                           num_frames,
	                                           cabinet.boards_per_frame)
	cabinetised_boards = transforms.remove_gaps(cabinetised_boards)
	
	# Generate the output
	print("cabinet,frame,board,x,y,z")
	b2c = dict(cabinetised_boards)
	for board, hex_coord in sorted(hex_boards, key=(lambda v: v[1])):
		x, y, z = hex_to_board_coordinates(hex_coord)
		c, f, b = b2c[board]
		print(",".join(map(str, [c,f,b, x,y,z])))
	
	
	return 0


if __name__=="__main__":  # pragma: no cover
	import sys
	sys.exit(main())



