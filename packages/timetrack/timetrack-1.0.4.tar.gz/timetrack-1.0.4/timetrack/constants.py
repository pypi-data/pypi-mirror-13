metadata = {
	"name": "Time Track",
	"version": "1.0.4",
	"description": "Track the time you spend on activities easily with simple commands.\nAlso includes pretty exports to JSON and TXT formats.\n\nCurrent version: v1.0.4",
	"helps": {
		"start": {
			"description": "stop the current activity (if any) and start a new one",
			"metavar": "NAME"
		},
		"stop": {
			"description": "start the previously started activity (if any)"
		},
		"backup": {
			"description": "make a copy of the database as a backup"
		},
		"restore": {
			"description": "restore from the last backup made"
		},
		"export": {
			"description": "export the database as a JSON or a TXT;\nyou may use '>' to write to a file",
			"metavar": "FORMAT"
		},
		"pretty": {
			"description": "displays the output in a pretty format:\n - JSON: Formats to a readable format\n - TXT: Creates an aggregate table sorted by activity name"
		},
		"clear": {
			"description": "clear the database"
		},
		"clear_backup": {
			"description": "clear the backup database"
		},
		"version": {
			"description": "print time-track version and exit"
		}
	}
}

strings = {
	"default_activity_name": "Unnamed Activity"
}
