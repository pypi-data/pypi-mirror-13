import constants
import argparse
import sys
from pymongo import MongoClient

def arg_parse():
	parser = argparse.ArgumentParser(description=constants.metadata["description"], formatter_class=argparse.RawTextHelpFormatter)
	parser.add_argument("--start",
			nargs=1,
			help=constants.metadata["helps"]["start"]["description"],
			metavar=constants.metadata["helps"]["start"]["metavar"]
	)
	parser.add_argument("--stop",
			action='store_true',
			help=constants.metadata["helps"]["stop"]["description"]
	)
	parser.add_argument("--export",
			nargs=1,
			help=constants.metadata["helps"]["export"]["description"],
			metavar=constants.metadata["helps"]["export"]["metavar"]
	)
	parser.add_argument("--pretty",
			action='store_true',
			help=constants.metadata["helps"]["pretty"]["description"]
	)
	parser.add_argument("--backup",
			action='store_true',
			help=constants.metadata["helps"]["backup"]["description"]
	)
	parser.add_argument("--restore",
			action='store_true',
			help=constants.metadata["helps"]["backup"]["description"]
	)
	parser.add_argument("--clear",
			action='store_true',
			help=constants.metadata["helps"]["clear"]["description"]
	)
	parser.add_argument("--clear-backup",
			action='store_true',
			help=constants.metadata["helps"]["clear_backup"]["description"]
	)
	parser.add_argument("-v", "--version",
			action='store_true',
			help=constants.metadata["helps"]["version"]["description"]
	)

	if len(sys.argv) > 1:
		args = parser.parse_args()
		if args.start:
			args.stop = True
			args.start = " ".join(args.start)
	else:
		parser.print_help()
		sys.exit(0)

	return args


def init_db():
	client = MongoClient()
	db = client.timetracker
	return db
