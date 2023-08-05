dnl Functions for libbfio
dnl
dnl Version: 20130409

dnl Function to detect if libbfio is available
AC_DEFUN([AX_LIBBFIO_CHECK_LIB],
 [dnl Check if parameters were provided
 AS_IF(
  [test "x$ac_cv_with_libbfio" != x && test "x$ac_cv_with_libbfio" != xno && test "x$ac_cv_with_libbfio" != xauto-detect],
  [AS_IF(
   [test -d "$ac_cv_with_libbfio"],
   [CFLAGS="$CFLAGS -I${ac_cv_with_libbfio}/include"
   LDFLAGS="$LDFLAGS -L${ac_cv_with_libbfio}/lib"],
   [AC_MSG_WARN([no such directory: $ac_cv_with_libbfio])
   ])
  ])

 AS_IF(
  [test "x$ac_cv_with_libbfio" = xno],
  [ac_cv_libbfio=no],
  [dnl Check for a pkg-config file
  AS_IF(
   [test "x$cross_compiling" != "xyes" && test "x$PKGCONFIG" != "x"],
   [PKG_CHECK_MODULES(
    [libbfio],
    [libbfio >= 20120426],
    [ac_cv_libbfio=yes],
    [ac_cv_libbfio=no])
   ])

  AS_IF(
   [test "x$ac_cv_libbfio" = xyes],
   [ac_cv_libbfio_CPPFLAGS="$pkg_cv_libbfio_CFLAGS"
   ac_cv_libbfio_LIBADD="$pkg_cv_libbfio_LIBS"],
   [dnl Check for headers
   AC_CHECK_HEADERS([libbfio.h])

   AS_IF(
    [test "x$ac_cv_header_libbfio_h" = xno],
    [ac_cv_libbfio=no],
    [dnl Check for the individual functions
    ac_cv_libbfio=yes

    AC_CHECK_LIB(
     bfio,
     libbfio_get_version,
     [ac_cv_libbfio_dummy=yes],
     [ac_cv_libbfio=no])

    dnl Handle functions
    AC_CHECK_LIB(
     bfio,
     libbfio_handle_free,
     [ac_cv_libbfio_dummy=yes],
     [ac_cv_libbfio=no])
    AC_CHECK_LIB(
     bfio,
     libbfio_handle_open,
     [ac_cv_libbfio_dummy=yes],
     [ac_cv_libbfio=no])
    AC_CHECK_LIB(
     bfio,
     libbfio_handle_close,
     [ac_cv_libbfio_dummy=yes],
     [ac_cv_libbfio=no])
    AC_CHECK_LIB(
     bfio,
     libbfio_handle_exists,
     [ac_cv_libbfio_dummy=yes],
     [ac_cv_libbfio=no])
    AC_CHECK_LIB(
     bfio,
     libbfio_handle_read_buffer,
     [ac_cv_libbfio_dummy=yes],
     [ac_cv_libbfio=no])
    AC_CHECK_LIB(
     bfio,
     libbfio_handle_write_buffer,
     [ac_cv_libbfio_dummy=yes],
     [ac_cv_libbfio=no])
    AC_CHECK_LIB(
     bfio,
     libbfio_handle_seek_offset,
     [ac_cv_libbfio_dummy=yes],
     [ac_cv_libbfio=no])

    AC_CHECK_LIB(
     bfio,
     libbfio_handle_is_open,
     [ac_cv_libbfio_dummy=yes],
     [ac_cv_libbfio=no])
    AC_CHECK_LIB(
     bfio,
     libbfio_handle_get_offset,
     [ac_cv_libbfio_dummy=yes],
     [ac_cv_libbfio=no])
    AC_CHECK_LIB(
     bfio,
     libbfio_handle_get_size,
     [ac_cv_libbfio_dummy=yes],
     [ac_cv_libbfio=no])
    AC_CHECK_LIB(
     bfio,
     libbfio_handle_set_track_offsets_read,
     [ac_cv_libbfio_dummy=yes],
     [ac_cv_libbfio=no])
    AC_CHECK_LIB(
     bfio,
     libbfio_handle_get_number_of_offsets_read,
     [ac_cv_libbfio_dummy=yes],
     [ac_cv_libbfio=no])
    AC_CHECK_LIB(
     bfio,
     libbfio_handle_get_offset_read,
     [ac_cv_libbfio_dummy=yes],
     [ac_cv_libbfio=no])

    dnl File functions
    AC_CHECK_LIB(
     bfio,
     libbfio_file_initialize,
     [ac_cv_libbfio_dummy=yes],
     [ac_cv_libbfio=no])
    AC_CHECK_LIB(
     bfio,
     libbfio_file_get_name_size,
     [ac_cv_libbfio_dummy=yes],
     [ac_cv_libbfio=no])
    AC_CHECK_LIB(
     bfio,
     libbfio_file_get_name,
     [ac_cv_libbfio_dummy=yes],
     [ac_cv_libbfio=no])
    AC_CHECK_LIB(
     bfio,
     libbfio_file_set_name,
     [ac_cv_libbfio_dummy=yes],
     [ac_cv_libbfio=no])

    AS_IF(
     [test "x$ac_cv_enable_wide_character_type" != xno],
     [AC_CHECK_LIB(
      bfio,
      libbfio_file_get_name_size_wide,
      [ac_cv_libbfio_dummy=yes],
      [ac_cv_libbfio=no])
     AC_CHECK_LIB(
      bfio,
      libbfio_file_get_name_wide,
      [ac_cv_libbfio_dummy=yes],
      [ac_cv_libbfio=no])
     AC_CHECK_LIB(
      bfio,
      libbfio_file_set_name_wide,
      [ac_cv_libbfio_dummy=yes],
      [ac_cv_libbfio=no])
     ])

    dnl Pool functions
    AC_CHECK_LIB(
     bfio,
     libbfio_pool_initialize,
     [ac_cv_libbfio_dummy=yes],
     [ac_cv_libbfio=no])
    AC_CHECK_LIB(
     bfio,
     libbfio_pool_free,
     [ac_cv_libbfio_dummy=yes],
     [ac_cv_libbfio=no])
    AC_CHECK_LIB(
     bfio,
     libbfio_pool_clone,
     [ac_cv_libbfio_dummy=yes],
     [ac_cv_libbfio=no])
    AC_CHECK_LIB(
     bfio,
     libbfio_pool_open,
     [ac_cv_libbfio_dummy=yes],
     [ac_cv_libbfio=no])
    AC_CHECK_LIB(
     bfio,
     libbfio_pool_reopen,
     [ac_cv_libbfio_dummy=yes],
     [ac_cv_libbfio=no])
    AC_CHECK_LIB(
     bfio,
     libbfio_pool_close,
     [ac_cv_libbfio_dummy=yes],
     [ac_cv_libbfio=no])
    AC_CHECK_LIB(
     bfio,
     libbfio_pool_close_all,
     [ac_cv_libbfio_dummy=yes],
     [ac_cv_libbfio=no])
    AC_CHECK_LIB(
     bfio,
     libbfio_pool_read_buffer,
     [ac_cv_libbfio_dummy=yes],
     [ac_cv_libbfio=no])
    AC_CHECK_LIB(
     bfio,
     libbfio_pool_write_buffer,
     [ac_cv_libbfio_dummy=yes],
     [ac_cv_libbfio=no])
    AC_CHECK_LIB(
     bfio,
     libbfio_pool_seek_offset,
     [ac_cv_libbfio_dummy=yes],
     [ac_cv_libbfio=no])

    AC_CHECK_LIB(
     bfio,
     libbfio_pool_get_number_of_handles,
     [ac_cv_libbfio_dummy=yes],
     [ac_cv_libbfio=no])
    AC_CHECK_LIB(
     bfio,
     libbfio_pool_get_handle,
     [ac_cv_libbfio_dummy=yes],
     [ac_cv_libbfio=no])
    AC_CHECK_LIB(
     bfio,
     libbfio_pool_set_handle,
     [ac_cv_libbfio_dummy=yes],
     [ac_cv_libbfio=no])
    AC_CHECK_LIB(
     bfio,
     libbfio_pool_append_handle,
     [ac_cv_libbfio_dummy=yes],
     [ac_cv_libbfio=no])
    AC_CHECK_LIB(
     bfio,
     libbfio_pool_get_offset,
     [ac_cv_libbfio_dummy=yes],
     [ac_cv_libbfio=no])
    AC_CHECK_LIB(
     bfio,
     libbfio_pool_get_size,
     [ac_cv_libbfio_dummy=yes],
     [ac_cv_libbfio=no])
    AC_CHECK_LIB(
     bfio,
     libbfio_pool_set_maximum_number_of_open_handles,
     [ac_cv_libbfio_dummy=yes],
     [ac_cv_libbfio=no])

    ac_cv_libbfio_LIBADD="-lbfio"
    ])
   ])
  ])

 AS_IF(
  [test "x$ac_cv_libbfio" = xyes],
  [AC_DEFINE(
   [HAVE_LIBBFIO],
   [1],
   [Define to 1 if you have the `bfio' library (-lbfio).])
  ])

 AS_IF(
  [test "x$ac_cv_libbfio" = xyes],
  [AC_SUBST(
   [HAVE_LIBBFIO],
   [1]) ],
  [AC_SUBST(
   [HAVE_LIBBFIO],
   [0])
  ])
 ])

dnl Function to detect how to enable libbfio
AC_DEFUN([AX_LIBBFIO_CHECK_ENABLE],
 [AX_COMMON_ARG_WITH(
  [libbfio],
  [libbfio],
  [search for libbfio in includedir and libdir or in the specified DIR, or no if to use local version],
  [auto-detect],
  [DIR])

 dnl Check for a shared library version
 AX_LIBBFIO_CHECK_LIB

 dnl Check if the dependencies for the local library version
 AS_IF(
  [test "x$ac_cv_libbfio" != xyes],
  [AC_DEFINE(
   [HAVE_LOCAL_LIBBFIO],
   [1],
   [Define to 1 if the local version of libbfio is used.])
  AC_SUBST(
   [HAVE_LOCAL_LIBBFIO],
   [1])

  ac_cv_libbfio_CPPFLAGS="-I../libbfio";
  ac_cv_libbfio_LIBADD="../libbfio/libbfio.la";

  ac_cv_libbfio=local
  ])

 AM_CONDITIONAL(
  [HAVE_LOCAL_LIBBFIO],
  [test "x$ac_cv_libbfio" = xlocal])
 AS_IF(
  [test "x$ac_cv_libbfio_CPPFLAGS" != "x"],
  [AC_SUBST(
   [LIBBFIO_CPPFLAGS],
   [$ac_cv_libbfio_CPPFLAGS])
  ])
 AS_IF(
  [test "x$ac_cv_libbfio_LIBADD" != "x"],
  [AC_SUBST(
   [LIBBFIO_LIBADD],
   [$ac_cv_libbfio_LIBADD])
  ])

 AS_IF(
  [test "x$ac_cv_libbfio" = xyes],
  [AC_SUBST(
   [ax_libbfio_pc_libs_private],
   [-lbfio])
  ])

 AS_IF(
  [test "x$ac_cv_libbfio" = xyes],
  [AC_SUBST(
   [ax_libbfio_spec_requires],
   [libbfio])
  AC_SUBST(
   [ax_libbfio_spec_build_requires],
   [libbfio-devel])
  ])
 ])

