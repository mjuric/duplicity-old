# Copyright 2002 Ben Escoto
#
# This file is part of duplicity.
#
# duplicity is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, Inc., 675 Mass Ave, Cambridge MA
# 02139, USA; either version 2 of the License, or (at your option) any
# later version; incorporated herein by reference.

import tempfile
import librsync, errno, log, path

tmp_file_index = 1

def check_common_error(error_handler, function, args = ()):
	"""Apply function to args, if error, run error_handler on exception

	This only catches certain exceptions which seem innocent
	enough.

	"""
	try: return function(*args)
	#except (EnvironmentError, SkipFileException, DSRPPermError,
	#		RPathException, Rdiff.RdiffException,
	#		librsync.librsyncError, C.UnknownFileTypeError), exc:
	#	TracebackArchive.add()
	except (EnvironmentError, librsync.librsyncError, path.PathException), exc:
		if (not isinstance(exc, EnvironmentError) or
			(errno.errorcode[exc[0]] in
			 ['EPERM', 'ENOENT', 'EACCES', 'EBUSY', 'EEXIST',
			  'ENOTDIR', 'ENAMETOOLONG', 'EINTR', 'ENOTEMPTY',
			  'EIO', 'ETXTBSY', 'ESRCH', 'EINVAL'])):
			#Log.exception()
			if error_handler: return error_handler(exc, *args)
		else:
			#Log.exception(1, 2)
			raise

def listpath(path):
	"""Like path.listdir() but return [] if error, and sort results"""
	def error_handler(exc):
		log.Log("Error listing directory %s" % path.name, 2)
		return []
	dir_listing = check_common_error(error_handler, path.listdir)
	dir_listing.sort()
	return dir_listing

