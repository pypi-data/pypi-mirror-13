/*
 * Python object definition of the libmsiecf leak item
 *
 * Copyright (C) 2009-2015, Joachim Metz <joachim.metz@gmail.com>
 *
 * Refer to AUTHORS for acknowledgements.
 *
 * This software is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Lesser General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This software is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with this software.  If not, see <http://www.gnu.org/licenses/>.
 */

#include <common.h>
#include <types.h>

#if defined( HAVE_STDLIB_H ) || defined( HAVE_WINAPI )
#include <stdlib.h>
#endif

#include "pymsiecf_error.h"
#include "pymsiecf_integer.h"
#include "pymsiecf_item.h"
#include "pymsiecf_leak.h"
#include "pymsiecf_libcerror.h"
#include "pymsiecf_libcstring.h"
#include "pymsiecf_libmsiecf.h"
#include "pymsiecf_python.h"
#include "pymsiecf_unused.h"

PyMethodDef pymsiecf_leak_object_methods[] = {

	/* Functions to access the leak values */

	{ "get_cached_file_size",
	  (PyCFunction) pymsiecf_leak_get_cached_file_size,
	  METH_NOARGS,
	  "get_cached_file_size() -> Integer\n"
	  "\n"
	  "Retrieves the cached file size." },

	{ "get_cache_directory_index",
	  (PyCFunction) pymsiecf_leak_get_cache_directory_index,
	  METH_NOARGS,
	  "get_cache_directory_index() -> Integer\n"
	  "\n"
	  "Retrieves the cache directory index." },

	{ "get_filename",
	  (PyCFunction) pymsiecf_leak_get_filename,
	  METH_NOARGS,
	  "get_filename() -> Unicode string or None\n"
	  "\n"
	  "Retrieves the location." },

	/* Sentinel */
	{ NULL, NULL, 0, NULL }
};

PyGetSetDef pymsiecf_leak_object_get_set_definitions[] = {

	{ "cached_file_size",
	  (getter) pymsiecf_leak_get_cached_file_size,
	  (setter) 0,
	  "The cached file size.",
	  NULL },

	{ "cache_directory_index",
	  (getter) pymsiecf_leak_get_cache_directory_index,
	  (setter) 0,
	  "The cache directory index.",
	  NULL },

	{ "filename",
	  (getter) pymsiecf_leak_get_filename,
	  (setter) 0,
	  "The filename.",
	  NULL },

	/* Sentinel */
	{ NULL, NULL, NULL, NULL, NULL }
};

PyTypeObject pymsiecf_leak_type_object = {
	PyVarObject_HEAD_INIT( NULL, 0 )

	/* tp_name */
	"pymsiecf.leak",
	/* tp_basicsize */
	sizeof( pymsiecf_item_t ),
	/* tp_itemsize */
	0,
	/* tp_dealloc */
	0,
	/* tp_print */
	0,
	/* tp_getattr */
	0,
	/* tp_setattr */
	0,
	/* tp_compare */
	0,
	/* tp_repr */
	0,
	/* tp_as_number */
	0,
	/* tp_as_sequence */
	0,
	/* tp_as_mapping */
	0,
	/* tp_hash */
	0,
	/* tp_call */
	0,
	/* tp_str */
	0,
	/* tp_getattro */
	0,
	/* tp_setattro */
	0,
	/* tp_as_buffer */
	0,
	/* tp_flags */
	Py_TPFLAGS_DEFAULT,
	/* tp_doc */
	"pymsiecf leak object (wraps libmsiecf_item_t type LIBMSIECF_ITEM_TYPE_LEAK)",
	/* tp_traverse */
	0,
	/* tp_clear */
	0,
	/* tp_richcompare */
	0,
	/* tp_weaklistoffset */
	0,
	/* tp_iter */
	0,
	/* tp_iternext */
	0,
	/* tp_methods */
	pymsiecf_leak_object_methods,
	/* tp_members */
	0,
	/* tp_getset */
	pymsiecf_leak_object_get_set_definitions,
	/* tp_base */
	&pymsiecf_item_type_object,
	/* tp_dict */
	0,
	/* tp_descr_get */
	0,
	/* tp_descr_set */
	0,
	/* tp_dictoffset */
	0,
	/* tp_init */
	0,
	/* tp_alloc */
	0,
	/* tp_new */
	0,
	/* tp_free */
	0,
	/* tp_is_gc */
	0,
	/* tp_bases */
	NULL,
	/* tp_mro */
	NULL,
	/* tp_cache */
	NULL,
	/* tp_subclasses */
	NULL,
	/* tp_weaklist */
	NULL,
	/* tp_del */
	0
};

/* Retrieves the cached file size
 * Returns a Python object if successful or NULL on error
 */
PyObject *pymsiecf_leak_get_cached_file_size(
           pymsiecf_item_t *pymsiecf_item,
           PyObject *arguments PYMSIECF_ATTRIBUTE_UNUSED )
{
	libcerror_error_t *error  = NULL;
	PyObject *integer_object  = NULL;
	static char *function     = "pymsiecf_leak_get_cached_file_size";
	uint64_t cached_file_size = 0;
	int result                = 0;

	PYMSIECF_UNREFERENCED_PARAMETER( arguments )

	if( pymsiecf_item == NULL )
	{
		PyErr_Format(
		 PyExc_TypeError,
		 "%s: invalid item.",
		 function );

		return( NULL );
	}
	Py_BEGIN_ALLOW_THREADS

	result = libmsiecf_leak_get_cached_file_size(
	          pymsiecf_item->item,
	          &cached_file_size,
	          &error );

	Py_END_ALLOW_THREADS

	if( result != 1 )
	{
		pymsiecf_error_raise(
		 error,
		 PyExc_IOError,
		 "%s: unable to retrieve cached file size.",
		 function );

		libcerror_error_free(
		 &error );

		return( NULL );
	}
	integer_object = pymsiecf_integer_unsigned_new_from_64bit(
	                  cached_file_size );

	return( integer_object );
}

/* Retrieves the cache directory index
 * Returns a Python object if successful or NULL on error
 */
PyObject *pymsiecf_leak_get_cache_directory_index(
           pymsiecf_item_t *pymsiecf_item,
           PyObject *arguments PYMSIECF_ATTRIBUTE_UNUSED )
{
	libcerror_error_t *error      = NULL;
	PyObject *integer_object      = NULL;
	static char *function         = "pymsiecf_leak_get_cache_directory_index";
	uint8_t cache_directory_index = 0;
	int result                    = 0;

	PYMSIECF_UNREFERENCED_PARAMETER( arguments )

	if( pymsiecf_item == NULL )
	{
		PyErr_Format(
		 PyExc_TypeError,
		 "%s: invalid item.",
		 function );

		return( NULL );
	}
	Py_BEGIN_ALLOW_THREADS

	result = libmsiecf_leak_get_cache_directory_index(
	          pymsiecf_item->item,
	          &cache_directory_index,
	          &error );

	Py_END_ALLOW_THREADS

	if( result != 1 )
	{
		pymsiecf_error_raise(
		 error,
		 PyExc_IOError,
		 "%s: unable to retrieve cache directory index.",
		 function );

		libcerror_error_free(
		 &error );

		return( NULL );
	}
#if PY_MAJOR_VERSION >= 3
	integer_object = PyLong_FromLong(
	                  (long) cache_directory_index );
#else
	integer_object = PyInt_FromLong(
	                  (long) cache_directory_index );
#endif
	return( integer_object );
}

/* Retrieves the filename
 * Returns a Python object if successful or NULL on error
 */
PyObject *pymsiecf_leak_get_filename(
           pymsiecf_item_t *pymsiecf_item,
           PyObject *arguments PYMSIECF_ATTRIBUTE_UNUSED )
{
	libcerror_error_t *error = NULL;
	PyObject *string_object  = NULL;
	const char *errors       = NULL;
	uint8_t *filename        = NULL;
	static char *function    = "pymsiecf_leak_get_filename";
	size_t filename_size     = 0;
	int result               = 0;

	PYMSIECF_UNREFERENCED_PARAMETER( arguments )

	if( pymsiecf_item == NULL )
	{
		PyErr_Format(
		 PyExc_TypeError,
		 "%s: invalid item.",
		 function );

		return( NULL );
	}
	Py_BEGIN_ALLOW_THREADS

	result = libmsiecf_leak_get_utf8_filename_size(
	          pymsiecf_item->item,
	          &filename_size,
	          &error );

	Py_END_ALLOW_THREADS

	if( result == -1 )
	{
		pymsiecf_error_raise(
		 error,
		 PyExc_IOError,
		 "%s: unable to retrieve filename size.",
		 function );

		libcerror_error_free(
		 &error );

		goto on_error;
	}
	else if( ( result == 0 )
	      || ( filename_size == 0 ) )
	{
		Py_IncRef(
		 Py_None );

		return( Py_None );
	}
	filename = (uint8_t *) PyMem_Malloc(
	                        sizeof( uint8_t ) * filename_size );

	if( filename == NULL )
	{
		PyErr_Format(
		 PyExc_IOError,
		 "%s: unable to create filename.",
		 function );

		goto on_error;
	}
	Py_BEGIN_ALLOW_THREADS

	result = libmsiecf_leak_get_utf8_filename(
		  pymsiecf_item->item,
		  filename,
		  filename_size,
		  &error );

	Py_END_ALLOW_THREADS

	if( result != 1 )
	{
		pymsiecf_error_raise(
		 error,
		 PyExc_IOError,
		 "%s: unable to retrieve filename.",
		 function );

		libcerror_error_free(
		 &error );

		goto on_error;
	}
	/* Pass the string length to PyUnicode_DecodeUTF8
	 * otherwise it makes the end of string character is part
	 * of the string
	 */
	string_object = PyUnicode_DecodeUTF8(
			 (char *) filename,
			 (Py_ssize_t) filename_size - 1,
			 errors );

	PyMem_Free(
	 filename );

	return( string_object );

on_error:
	if( filename != NULL )
	{
		PyMem_Free(
		 filename );
	}
	return( NULL );
}

