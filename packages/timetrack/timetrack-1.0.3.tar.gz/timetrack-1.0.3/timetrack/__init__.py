import pymongo
import utils
import time
import datetime
import sys
import json
import tabulate
import constants

def stop_last(db):
	if db.activities.count() == 0:
		print("No running activities.")
		return
	res = db.activities.find().sort([
		("start_time", pymongo.DESCENDING)
	])
	if res[0] and "end_time" not in res[0]:
		db.activities.update_one({
			"_id": res[0]["_id"]
		}, {
			"$set": {
				"end_time": datetime.datetime.now()
			}
		})
		print("Tracked stop of '" + res[0]["name"] + "' successfully.")

def start(db, activity):
	result = db.activities.insert_one({
		"name": activity,
		"start_time": datetime.datetime.now()
	})
	print("Tracked start of '" + activity + "' successfully.")

def copy(dest, src):
	for act in src.find():
		res = dict(act)
		del res['_id']
		dest.insert_one(res)

def backup(db):
	if "activities_backup" in db.collection_names() and db.activities_backup.count() > 0:
		print("Entries in database: " + str(db.activities.count()))
		print("Entries in backup:   " + str(db.activities_backup.count()))
		overwrite = input("There already exists a backup. Overwrite? (y/N) ").lower() == 'y'
		if not overwrite:
			return
		else:
			db.activities_backup.drop()
	copy(db.activities_backup, db.activities)
	print("Backup created successfully.")

def restore(db):
	if "activities_backup" not in db.collection_names():
		print("No backup database found.")
	if "activities" in db.collection_names() and db.activities.count() > 0:
		print("Entries in database: " + str(db.activities.count()))
		print("Entries in backup:   " + str(db.activities_backup.count()))
		overwrite = input("Restoring from backup will delete current entries. Continue? (y/N) ").lower() == 'y'
		if not overwrite:
			return
	db.activities.drop()
	copy(db.activities, db.activities_backup)
	print("Successfully restored from backup.")

def clear(db):
	if "activities" not in db.collection_names():
		print("No database found")
		return
	print("Entries in database: " + str(db.activities.count()))
	delete = input("Clearing the database cannot be undone. Continue? (y/N) ").lower() == 'y'
	if delete:
		db.activities.delete_many({})
		print("Database cleared successfully.")
		if "activities_backup" in db.collection_names():
			print("Entries in backup database: " + str(db.activities_backup.count()))
			delete = input("Do you also want to clear the backup database? (y/N) ").lower() == 'y'
			if delete:
				db.activities_backup.delete_many({})
				print("Backup database cleared successfully.")

def clear_backup(db):
	if "activities_backup" in db.collection_names():
		print("Entries in backup database: " + str(db.activities_backup.count()))
		delete = input("Are you sure you want to clear the backup database? (y/N) ").lower() == 'y'
		if delete:
			db.activities_backup.delete_many({})
			print("Backup database cleared successfully.")


def export(db, format, pretty):
	if format.lower() == "json":
		arr = []
		for d in list(db.activities.find()):
			del d['_id']
			d['start_time'] = str(d['start_time'])
			if "end_time" in d:
				d["end_time"] = str(d["end_time"])
			arr.append(d)
		if pretty == True:
			print(json.dumps(arr, sort_keys=True, indent=2, separators=(',', ': ')))
		else:
			print(json.dumps(arr))
	elif format.lower() == "txt":
		if pretty == True:
			arr = {}
			for d in list(db.activities.find()):
				if d["name"] not in arr:
					arr[d["name"]] = 0
				arr[d["name"]] += (d["end_time"] - d["start_time"]).seconds
			ret = []
			if sys.version_info.major == 2:
				x = arr.iteritems()
			else:
				x = arr.items()
			for key, value in x:
				ret.append([key, value])
			ret = sorted(ret, key=lambda tup: -tup[1])
			res = []
			for d in ret:
				s = ""
				if d[1] >= 3600 * 24 * 7:
					qq = "s"
					if d[1] / (3600 * 24 * 7) == 1:
						qq = ""
					s += str(d[1] / (3600 * 24 * 7)) + " week" + qq + " "
				if d[1] >= 3600 * 24 and (d[1] / (3600 * 24)) % 7 != 0:
					qq = "s"
					if (d[1] / (3600 * 24)) % 7 == 1:
						qq = ""
					s += str((d[1] / (3600 * 24)) % 7) + " day" + qq + " "
				if d[1] >= 3600 and (d[1] / (3600)) % 24 != 0:
					qq = "s"
					if (d[1] / (3600)) % 24 == 1:
						qq = ""
					s += str((d[1] / (3600)) % 24) + " hour" + qq + " "
				if d[1] >= 60 and (d[1] / 60) % 60 != 0:
					qq = "s"
					if (d[1] / (60)) % 60 == 1:
						qq = ""
					s += str((d[1] / (60)) % 60) + " min" + qq + " "
				if d[1] % 60 != 0:
					qq = "s"
					if d[1] % 60 == 1:
						qq = ""
					s += str(d[1] % 60) + " sec" + qq + " "
				if s == "":
					s = "-"
				res.append([d[0], s])
			print(tabulate.tabulate(res, headers=["Name", "Duration"], tablefmt="psql"))
		else:
			flag = False
			for d in list(db.activities.find()):
				if flag:
					print("")
				flag = True
				print("Name:       " + d["name"])
				print("Duration:   " + str(d["end_time"] - d["start_time"]).split('.', 2)[0])
				print("Start time: " + d["start_time"].strftime("%H:%M:%S, %d %B %Y"))
				print("End time:   " + d["end_time"].strftime("%H:%M:%S, %d %B %Y"))
	else:
		sys.stderr.write("Unrecognized format '" + format + "'\n")


def main():
	args = utils.arg_parse()
	db = utils.init_db()

	if args.version:
		print(constants.metadata["name"] + " v" + constants.metadata["version"])

	if args.stop:
		stop_last(db)

	if args.start:
		start(db, args.start)

	if args.backup:
		backup(db)

	if args.restore:
		restore(db)

	if args.clear:
		clear(db)

	if args.clear_backup:
		clear_backup(db)

	if args.export:
		export(db, args.export[0], args.pretty)
