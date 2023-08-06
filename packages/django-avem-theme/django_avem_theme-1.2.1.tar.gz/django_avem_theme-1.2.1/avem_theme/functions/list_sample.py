

def list_sample(collection, limit = 3):
	"""
		given an ordered collection (list, tuple, ...), return a string representation
		of the first limit items (or fewer), e.g. "itemA, itemB, itemC and 7 more"
	"""
	ln = len(collection)
	if ln > 1:
		if ln <= limit:
			return '%s and %s' % (', '.join(str(ws) for ws in collection[:min(limit, ln)]), collection[min(limit, ln)])
		return '%s and %d others' % (', '.join(str(ws) for ws in collection[:min(limit, ln)]), ln - limit)
	if ln > 0:
		return collection[0]
	return ''


def list_sample_special(collection, special_item, special_name = 'you', limit = 3):
	"""
		special version with 'special_name' as first extra item where applicable
	"""
	def jcs(items):
		return ', '.join(str(item) for item in items)
	try:
		collection.remove(special_item)
		has_special = True
		limit -= 1
	except ValueError:
		has_special = False
	ln = len(collection)
	if ln == 0:
		if has_special:
			return special_name
		return None
	if ln == 1:
		if has_special:
			return '%s and %s' % (special_name, collection[0])
		return collection[0]
	if ln - limit == 1:
		limit += 1
	if ln <= limit:
		if has_special:
			return '%s, %s and %s' % (special_name, jcs(collection[:-1]), collection[-1])
		return '%s and %s' % (jcs(collection[:-1]), collection[-1])
	if has_special:
		return '%s, %s and %d other%s' % (special_name, jcs(collection[:limit]), ln - limit, 's' if ln - limit > 1 else '')
	return '%s and %d other%s' % (jcs(collection[:limit]), ln - limit, 's' if ln - limit > 1 else '')


