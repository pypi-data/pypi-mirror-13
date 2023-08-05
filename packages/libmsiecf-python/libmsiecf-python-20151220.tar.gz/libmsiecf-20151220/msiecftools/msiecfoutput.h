/*
 * Common output functions for the msiecftools
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

#if !defined( _MSIECFOUTPUT_H )
#define _MSIECFOUTPUT_H

#include <common.h>
#include <file_stream.h>
#include <types.h>

#if defined( __cplusplus )
extern "C" {
#endif

void msiecfoutput_copyright_fprint(
      FILE *stream );

void msiecfoutput_version_fprint(
      FILE *stream,
      const char *program );

void msiecfoutput_version_detailed_fprint(
      FILE *stream,
      const char *program );

#if defined( __cplusplus )
}
#endif

#endif

