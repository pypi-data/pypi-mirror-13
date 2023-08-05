/*
 * The internal definitions
 *
 * Copyright (C) 2008-2015, Joachim Metz <joachim.metz@gmail.com>
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

#if !defined( LIBFOLE_INTERNAL_DEFINITIONS_H )
#define LIBFOLE_INTERNAL_DEFINITIONS_H

#include <common.h>
#include <types.h>

/* Define HAVE_LOCAL_LIBFOLE for local use of libfole
 */
#if !defined( HAVE_LOCAL_LIBFOLE )
#include <libfole/definitions.h>

/* The definitions in <libfole/definitions.h> are copied here
 * for local use of libfole
 */
#else
#include <byte_stream.h>

#define LIBFOLE_VERSION					20150104

/* The version string
 */
#define LIBFOLE_VERSION_STRING				"20150104"

/* The byte order definitions
 */
#define LIBFOLE_ENDIAN_BIG				_BYTE_STREAM_ENDIAN_BIG
#define LIBFOLE_ENDIAN_LITTLE				_BYTE_STREAM_ENDIAN_LITTLE

#endif

#endif

