from src import netflix

n = netflix()
for entry in n.get_entry('documentary'):
	print (n.json_pretty(entry))