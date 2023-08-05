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

#if !defined( _LIBUNA_INTERNAL_DEFINITIONS_H )
#define _LIBUNA_INTERNAL_DEFINITIONS_H

#include <common.h>

/* Define HAVE_LOCAL_LIBUNA for local use of libuna
 */
#if !defined( HAVE_LOCAL_LIBUNA )
#include <libuna/definitions.h>

/* The definitions in <libuna/definitions.h> are copied here
 * for local use of libuna
 */
#else
#include <byte_stream.h>

#define LIBUNA_VERSION						20150927

/* The libuna version string
 */
#define LIBUNA_VERSION_STRING					"20150927"

/* The endian definitions
 */
#define	LIBUNA_ENDIAN_BIG					_BYTE_STREAM_ENDIAN_BIG
#define	LIBUNA_ENDIAN_LITTLE					_BYTE_STREAM_ENDIAN_LITTLE

/* The codepage definitions
 */
enum LIBUNA_CODEPAGES
{
	LIBUNA_CODEPAGE_ASCII					= 20127,

	LIBUNA_CODEPAGE_ISO_8859_1				= 28591,
	LIBUNA_CODEPAGE_ISO_8859_2				= 28592,
	LIBUNA_CODEPAGE_ISO_8859_3				= 28593,
	LIBUNA_CODEPAGE_ISO_8859_4				= 28594,
	LIBUNA_CODEPAGE_ISO_8859_5				= 28595,
	LIBUNA_CODEPAGE_ISO_8859_6				= 28596,
	LIBUNA_CODEPAGE_ISO_8859_7				= 28597,
	LIBUNA_CODEPAGE_ISO_8859_8				= 28598,
	LIBUNA_CODEPAGE_ISO_8859_9				= 28599,
	LIBUNA_CODEPAGE_ISO_8859_10				= 28600,
	LIBUNA_CODEPAGE_ISO_8859_11				= 28601,
	LIBUNA_CODEPAGE_ISO_8859_13				= 28603,
	LIBUNA_CODEPAGE_ISO_8859_14				= 28604,
	LIBUNA_CODEPAGE_ISO_8859_15				= 28605,
	LIBUNA_CODEPAGE_ISO_8859_16				= 28606,

	LIBUNA_CODEPAGE_KOI8_R					= 20866,
	LIBUNA_CODEPAGE_KOI8_U					= 21866,

	LIBUNA_CODEPAGE_OEM_437					= 437,
	LIBUNA_CODEPAGE_OEM_720					= 720,
	LIBUNA_CODEPAGE_OEM_737					= 737,
	LIBUNA_CODEPAGE_OEM_775					= 775,
	LIBUNA_CODEPAGE_OEM_850					= 850,
	LIBUNA_CODEPAGE_OEM_852					= 852,
	LIBUNA_CODEPAGE_OEM_855					= 855,
	LIBUNA_CODEPAGE_OEM_857					= 857,
	LIBUNA_CODEPAGE_OEM_858					= 858,
	LIBUNA_CODEPAGE_OEM_862					= 862,
	LIBUNA_CODEPAGE_OEM_866					= 866,

	LIBUNA_CODEPAGE_WINDOWS_874				= 874,
	LIBUNA_CODEPAGE_WINDOWS_932				= 932,
	LIBUNA_CODEPAGE_WINDOWS_936				= 936,
	LIBUNA_CODEPAGE_WINDOWS_949				= 949,
	LIBUNA_CODEPAGE_WINDOWS_950				= 950,
	LIBUNA_CODEPAGE_WINDOWS_1250				= 1250,
	LIBUNA_CODEPAGE_WINDOWS_1251				= 1251,
	LIBUNA_CODEPAGE_WINDOWS_1252				= 1252,
	LIBUNA_CODEPAGE_WINDOWS_1253				= 1253,
	LIBUNA_CODEPAGE_WINDOWS_1254				= 1254,
	LIBUNA_CODEPAGE_WINDOWS_1255				= 1255,
	LIBUNA_CODEPAGE_WINDOWS_1256				= 1256,
	LIBUNA_CODEPAGE_WINDOWS_1257				= 1257,
	LIBUNA_CODEPAGE_WINDOWS_1258				= 1258
};

#define LIBUNA_CODEPAGE_US_ASCII				LIBUNA_CODEPAGE_ASCII

#define LIBUNA_CODEPAGE_ISO_WESTERN_EUROPEAN			LIBUNA_CODEPAGE_ISO_8859_1
#define LIBUNA_CODEPAGE_ISO_CENTRAL_EUROPEAN			LIBUNA_CODEPAGE_ISO_8859_2
#define LIBUNA_CODEPAGE_ISO_SOUTH_EUROPEAN			LIBUNA_CODEPAGE_ISO_8859_3
#define LIBUNA_CODEPAGE_ISO_NORTH_EUROPEAN			LIBUNA_CODEPAGE_ISO_8859_4
#define LIBUNA_CODEPAGE_ISO_CYRILLIC				LIBUNA_CODEPAGE_ISO_8859_5
#define LIBUNA_CODEPAGE_ISO_ARABIC				LIBUNA_CODEPAGE_ISO_8859_6
#define LIBUNA_CODEPAGE_ISO_GREEK				LIBUNA_CODEPAGE_ISO_8859_7
#define LIBUNA_CODEPAGE_ISO_HEBREW				LIBUNA_CODEPAGE_ISO_8859_8
#define LIBUNA_CODEPAGE_ISO_TURKISH				LIBUNA_CODEPAGE_ISO_8859_9
#define LIBUNA_CODEPAGE_ISO_NORDIC				LIBUNA_CODEPAGE_ISO_8859_10
#define LIBUNA_CODEPAGE_ISO_THAI				LIBUNA_CODEPAGE_ISO_8859_11
#define LIBUNA_CODEPAGE_ISO_BALTIC				LIBUNA_CODEPAGE_ISO_8859_13
#define LIBUNA_CODEPAGE_ISO_CELTIC				LIBUNA_CODEPAGE_ISO_8859_14

#define LIBUNA_CODEPAGE_ISO_LATIN_1				LIBUNA_CODEPAGE_ISO_8859_1
#define LIBUNA_CODEPAGE_ISO_LATIN_2				LIBUNA_CODEPAGE_ISO_8859_2
#define LIBUNA_CODEPAGE_ISO_LATIN_3				LIBUNA_CODEPAGE_ISO_8859_3
#define LIBUNA_CODEPAGE_ISO_LATIN_4				LIBUNA_CODEPAGE_ISO_8859_4
#define LIBUNA_CODEPAGE_ISO_LATIN_5				LIBUNA_CODEPAGE_ISO_8859_9
#define LIBUNA_CODEPAGE_ISO_LATIN_6				LIBUNA_CODEPAGE_ISO_8859_10
#define LIBUNA_CODEPAGE_ISO_LATIN_7				LIBUNA_CODEPAGE_ISO_8859_13
#define LIBUNA_CODEPAGE_ISO_LATIN_8				LIBUNA_CODEPAGE_ISO_8859_14
#define LIBUNA_CODEPAGE_ISO_LATIN_9				LIBUNA_CODEPAGE_ISO_8859_15
#define LIBUNA_CODEPAGE_ISO_LATIN_10				LIBUNA_CODEPAGE_ISO_8859_16

#define LIBUNA_CODEPAGE_KOI8_RUSSIAN				LIBUNA_CODEPAGE_KOI8_R
#define LIBUNA_CODEPAGE_KOI8_UKRAINIAN				LIBUNA_CODEPAGE_KOI8_U

#define LIBUNA_CODEPAGE_OEM_874					LIBUNA_CODEPAGE_WINDOWS_874
#define LIBUNA_CODEPAGE_OEM_932					LIBUNA_CODEPAGE_WINDOWS_932
#define LIBUNA_CODEPAGE_OEM_936					LIBUNA_CODEPAGE_WINDOWS_936
#define LIBUNA_CODEPAGE_OEM_949					LIBUNA_CODEPAGE_WINDOWS_949
#define LIBUNA_CODEPAGE_OEM_950					LIBUNA_CODEPAGE_WINDOWS_950
#define LIBUNA_CODEPAGE_OEM_1258				LIBUNA_CODEPAGE_WINDOWS_1258

#define LIBUNA_CODEPAGE_OEM_US_ENGLISH				LIBUNA_CODEPAGE_OEM_437
#define LIBUNA_CODEPAGE_OEM_ARABIC				LIBUNA_CODEPAGE_OEM_720
#define LIBUNA_CODEPAGE_OEM_GREEK				LIBUNA_CODEPAGE_OEM_737
#define LIBUNA_CODEPAGE_OEM_BALTIC				LIBUNA_CODEPAGE_OEM_775
#define LIBUNA_CODEPAGE_OEM_LATIN_1				LIBUNA_CODEPAGE_OEM_850
#define LIBUNA_CODEPAGE_OEM_LATIN_2				LIBUNA_CODEPAGE_OEM_852
#define LIBUNA_CODEPAGE_OEM_CYRILLIC				LIBUNA_CODEPAGE_OEM_855
#define LIBUNA_CODEPAGE_OEM_TURKISH				LIBUNA_CODEPAGE_OEM_857
#define LIBUNA_CODEPAGE_OEM_LATIN_1_WITH_EURO			LIBUNA_CODEPAGE_OEM_858
#define LIBUNA_CODEPAGE_OEM_HEBREW				LIBUNA_CODEPAGE_OEM_862
#define LIBUNA_CODEPAGE_OEM_RUSSIAN				LIBUNA_CODEPAGE_OEM_866
#define LIBUNA_CODEPAGE_OEM_THAI				LIBUNA_CODEPAGE_WINDOWS_874
#define LIBUNA_CODEPAGE_OEM_JAPANESE				LIBUNA_CODEPAGE_WINDOWS_932
#define LIBUNA_CODEPAGE_OEM_CHINESE_SIMPLIFIED			LIBUNA_CODEPAGE_WINDOWS_936
#define LIBUNA_CODEPAGE_OEM_KOREAN				LIBUNA_CODEPAGE_WINDOWS_949
#define LIBUNA_CODEPAGE_OEM_CHINESE_TRADITIONAL			LIBUNA_CODEPAGE_WINDOWS_950
#define LIBUNA_CODEPAGE_OEM_VIETNAMESE				LIBUNA_CODEPAGE_WINDOWS_1258

#define LIBUNA_CODEPAGE_WINDOWS_THAI				LIBUNA_CODEPAGE_WINDOWS_874
#define LIBUNA_CODEPAGE_WINDOWS_JAPANESE			LIBUNA_CODEPAGE_WINDOWS_932
#define LIBUNA_CODEPAGE_WINDOWS_CHINESE_SIMPLIFIED		LIBUNA_CODEPAGE_WINDOWS_936
#define LIBUNA_CODEPAGE_WINDOWS_KOREAN				LIBUNA_CODEPAGE_WINDOWS_949
#define LIBUNA_CODEPAGE_WINDOWS_CHINESE_TRADITIONAL		LIBUNA_CODEPAGE_WINDOWS_950
#define LIBUNA_CODEPAGE_WINDOWS_CENTRAL_EUROPEAN		LIBUNA_CODEPAGE_WINDOWS_1250
#define LIBUNA_CODEPAGE_WINDOWS_CYRILLIC			LIBUNA_CODEPAGE_WINDOWS_1251
#define LIBUNA_CODEPAGE_WINDOWS_WESTERN_EUROPEAN		LIBUNA_CODEPAGE_WINDOWS_1252
#define LIBUNA_CODEPAGE_WINDOWS_GREEK				LIBUNA_CODEPAGE_WINDOWS_1253
#define LIBUNA_CODEPAGE_WINDOWS_TURKISH				LIBUNA_CODEPAGE_WINDOWS_1254
#define LIBUNA_CODEPAGE_WINDOWS_HEBREW				LIBUNA_CODEPAGE_WINDOWS_1255
#define LIBUNA_CODEPAGE_WINDOWS_ARABIC				LIBUNA_CODEPAGE_WINDOWS_1256
#define LIBUNA_CODEPAGE_WINDOWS_BALTIC				LIBUNA_CODEPAGE_WINDOWS_1257
#define LIBUNA_CODEPAGE_WINDOWS_VIETNAMESE			LIBUNA_CODEPAGE_WINDOWS_1258

#define LIBUNA_CODEPAGE_SHIFT_JIS				LIBUNA_CODEPAGE_WINDOWS_932
#define LIBUNA_CODEPAGE_GB2312					LIBUNA_CODEPAGE_WINDOWS_936

/* Base16 variants
 * Byte:
 * 0 - 1	Character limit
 * 2 - 3	Reserved
 * 4		Case (0 not supported)
 * 5 - 6	Reserved
 * 7		String encoding (0 is byte stream)
 */
enum LIBUNA_BASE16_VARIANTS
{
	LIBUNA_BASE16_VARIANT_CASE_LOWER			= 0x00010000UL,
	LIBUNA_BASE16_VARIANT_CASE_MIXED			= 0x00020000UL,
	LIBUNA_BASE16_VARIANT_CASE_UPPER			= 0x00030000UL,

	LIBUNA_BASE16_VARIANT_CHARACTER_LIMIT_NONE		= 0x00000000UL,
	LIBUNA_BASE16_VARIANT_CHARACTER_LIMIT_64		= 0x00000040UL,
	LIBUNA_BASE16_VARIANT_CHARACTER_LIMIT_76		= 0x0000004cUL,

	LIBUNA_BASE16_VARIANT_ENCODING_UTF16_BIG_ENDIAN		= 0x10000000UL,
	LIBUNA_BASE16_VARIANT_ENCODING_UTF16_LITTLE_ENDIAN	= 0x20000000UL,
	LIBUNA_BASE16_VARIANT_ENCODING_UTF32_BIG_ENDIAN		= 0x30000000UL,
	LIBUNA_BASE16_VARIANT_ENCODING_UTF32_LITTLE_ENDIAN	= 0x40000000UL
};

#define LIBUNA_BASE16_VARIANT_RFC4648 \
	LIBUNA_BASE16_VARIANT_CASE_MIXED | LIBUNA_BASE16_VARIANT_CHARACTER_LIMIT_NONE

/* Base16 processing flags
 */
enum LIBUNA_BASE16_FLAGS
{
	LIBUNA_BASE16_FLAG_STRIP_WHITESPACE			= 0x01
};

/* Base32 variants
 * Byte:
 * 0 - 1	Character limit
 * 2 - 3	Reserved
 * 4		Alphabet type (0 not supported)
 * 5		Reserved
 * 6    	Padding (0 not supported)
 * 7		String encoding (0 is byte stream)
 */
enum LIBUNA_BASE32_VARIANTS
{
	LIBUNA_BASE32_VARIANT_ALPHABET_NORMAL			= 0x00010000UL,
	LIBUNA_BASE32_VARIANT_ALPHABET_HEX			= 0x00020000UL,

	LIBUNA_BASE32_VARIANT_CHARACTER_LIMIT_NONE		= 0x00000000UL,
	LIBUNA_BASE32_VARIANT_CHARACTER_LIMIT_64		= 0x00000040UL,

	LIBUNA_BASE32_VARIANT_PADDING_NONE			= 0x01000000UL,
	LIBUNA_BASE32_VARIANT_PADDING_OPTIONAL			= 0x02000000UL,
	LIBUNA_BASE32_VARIANT_PADDING_REQUIRED			= 0x03000000UL,

	LIBUNA_BASE32_VARIANT_ENCODING_UTF16_BIG_ENDIAN		= 0x10000000UL,
	LIBUNA_BASE32_VARIANT_ENCODING_UTF16_LITTLE_ENDIAN	= 0x20000000UL,
	LIBUNA_BASE32_VARIANT_ENCODING_UTF32_BIG_ENDIAN		= 0x30000000UL,
	LIBUNA_BASE32_VARIANT_ENCODING_UTF32_LITTLE_ENDIAN	= 0x40000000UL
};

#define LIBUNA_BASE32_VARIANT_RFC4648 \
	LIBUNA_BASE32_VARIANT_ALPHABET_NORMAL | LIBUNA_BASE32_VARIANT_CHARACTER_LIMIT_NONE | LIBUNA_BASE32_VARIANT_PADDING_REQUIRED

#define LIBUNA_BASE32_VARIANT_HEX \
	LIBUNA_BASE32_VARIANT_ALPHABET_HEX | LIBUNA_BASE32_VARIANT_CHARACTER_LIMIT_NONE | LIBUNA_BASE32_VARIANT_PADDING_REQUIRED

/* Base32 processing flags
 */
enum LIBUNA_BASE32_FLAGS
{
	LIBUNA_BASE32_FLAG_STRIP_WHITESPACE			= 0x01
};

/* Base64 variants
 * Byte:
 * 0 - 1	Character limit
 * 2 - 3	Reserved
 * 4		Alphabet type (0 not supported)
 * 5		Reserved
 * 6    	Padding (0 not supported)
 * 7		String encoding (0 is byte stream)
 */
enum LIBUNA_BASE64_VARIANTS
{
	LIBUNA_BASE64_VARIANT_ALPHABET_NORMAL			= 0x00010000UL,
	LIBUNA_BASE64_VARIANT_ALPHABET_URL			= 0x00020000UL,

	LIBUNA_BASE64_VARIANT_CHARACTER_LIMIT_NONE		= 0x00000000UL,
	LIBUNA_BASE64_VARIANT_CHARACTER_LIMIT_64		= 0x00000040UL,
	LIBUNA_BASE64_VARIANT_CHARACTER_LIMIT_76		= 0x0000004cUL,

	LIBUNA_BASE64_VARIANT_PADDING_NONE			= 0x01000000UL,
	LIBUNA_BASE64_VARIANT_PADDING_OPTIONAL			= 0x02000000UL,
	LIBUNA_BASE64_VARIANT_PADDING_REQUIRED			= 0x03000000UL,

	LIBUNA_BASE64_VARIANT_ENCODING_UTF16_BIG_ENDIAN		= 0x10000000UL,
	LIBUNA_BASE64_VARIANT_ENCODING_UTF16_LITTLE_ENDIAN	= 0x20000000UL,
	LIBUNA_BASE64_VARIANT_ENCODING_UTF32_BIG_ENDIAN		= 0x30000000UL,
	LIBUNA_BASE64_VARIANT_ENCODING_UTF32_LITTLE_ENDIAN	= 0x40000000UL
};

#define LIBUNA_BASE64_VARIANT_RFC1421 \
	LIBUNA_BASE64_VARIANT_ALPHABET_NORMAL | LIBUNA_BASE64_VARIANT_CHARACTER_LIMIT_64 | LIBUNA_BASE64_VARIANT_PADDING_REQUIRED

#define LIBUNA_BASE64_VARIANT_PEM \
	LIBUNA_BASE64_VARIANT_RFC1421

#define LIBUNA_BASE64_VARIANT_RFC1642 \
	LIBUNA_BASE64_VARIANT_ALPHABET_NORMAL | LIBUNA_BASE64_VARIANT_CHARACTER_LIMIT_NONE | LIBUNA_BASE64_VARIANT_PADDING_NONE

#define LIBUNA_BASE64_VARIANT_UTF7 \
	LIBUNA_BASE64_VARIANT_RFC1642

#define LIBUNA_BASE64_VARIANT_RFC2045 \
	LIBUNA_BASE64_VARIANT_ALPHABET_NORMAL | LIBUNA_BASE64_VARIANT_CHARACTER_LIMIT_76 | LIBUNA_BASE64_VARIANT_PADDING_REQUIRED

#define LIBUNA_BASE64_VARIANT_MIME \
	LIBUNA_BASE64_VARIANT_RFC2045

#define LIBUNA_BASE64_VARIANT_URL \
	LIBUNA_BASE64_VARIANT_ALPHABET_URL | LIBUNA_BASE64_VARIANT_CHARACTER_LIMIT_NONE | LIBUNA_BASE64_VARIANT_PADDING_OPTIONAL

/* TODO
#define LIBUNA_BASE64_VARIANT_RFC3548
#define LIBUNA_BASE64_VARIANT_RFC4648
*/

/* Base64 processing flags
 */
enum LIBUNA_BASE64_FLAGS
{
	LIBUNA_BASE64_FLAG_STRIP_WHITESPACE			= 0x01
};

#endif

#define LIBUNA_BASE16_VARIANT_ENCODING_BYTE_STREAM		0
#define LIBUNA_BASE32_VARIANT_ENCODING_BYTE_STREAM		0
#define LIBUNA_BASE64_VARIANT_ENCODING_BYTE_STREAM		0

/* Character case definitions
 */
enum LIBUNA_CASE
{
	LIBUNA_CASE_LOWER					= (uint8_t) 'l',
	LIBUNA_CASE_MIXED					= (uint8_t) 'm',
	LIBUNA_CASE_UPPER					= (uint8_t) 'u'
};

/* Strip mode definitions
 */
enum LIBUNA_STRIP_MODES
{
	LIBUNA_STRIP_MODE_LEADING_WHITESPACE,
	LIBUNA_STRIP_MODE_NON_WHITESPACE,
	LIBUNA_STRIP_MODE_TRAILING_WHITESPACE,
	LIBUNA_STRIP_MODE_INVALID_CHARACTER
};

/* Character definitions
 */
#define LIBUNA_UNICODE_REPLACEMENT_CHARACTER			0x0000fffdUL
#define LIBUNA_UNICODE_BASIC_MULTILINGUAL_PLANE_MAX		0x0000ffffUL
#define LIBUNA_UNICODE_SURROGATE_LOW_RANGE_START		0x0000dc00UL
#define LIBUNA_UNICODE_SURROGATE_LOW_RANGE_END			0x0000dfffUL
#define LIBUNA_UNICODE_SURROGATE_HIGH_RANGE_START		0x0000d800UL
#define LIBUNA_UNICODE_SURROGATE_HIGH_RANGE_END			0x0000dbffUL
#define LIBUNA_UNICODE_CHARACTER_MAX				0x0010ffffUL

#define LIBUNA_UTF16_CHARACTER_MAX				0x0010ffffUL
#define LIBUNA_UTF32_CHARACTER_MAX				0x7fffffffUL

#define LIBUNA_ASCII_REPLACEMENT_CHARACTER			0x1a

/* UTF-7 definitions
 */
#define	LIBUNA_UTF7_IS_BASE64_ENCODED				0x80000000UL

#endif

