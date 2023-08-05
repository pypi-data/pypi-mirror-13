/*
 * Handle functions
 *
 * Copyright (C) 2009-2016, Joachim Metz <joachim.metz@gmail.com>
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

#if !defined( _LIBVMDK_INTERNAL_HANDLE_H )
#define _LIBVMDK_INTERNAL_HANDLE_H

#include <common.h>
#include <types.h>

#include "libvmdk_descriptor_file.h"
#include "libvmdk_extent_table.h"
#include "libvmdk_extern.h"
#include "libvmdk_grain_table.h"
#include "libvmdk_io_handle.h"
#include "libvmdk_libbfio.h"
#include "libvmdk_libcerror.h"
#include "libvmdk_libcthreads.h"
#include "libvmdk_libfcache.h"
#include "libvmdk_libfdata.h"

#if defined( _MSC_VER ) || defined( __BORLANDC__ ) || defined( __MINGW32_VERSION ) || defined( __MINGW64_VERSION_MAJOR )

/* This inclusion is needed otherwise some linkers
 * mess up exporting the metadata functions
 */
#include "libvmdk_metadata.h"
#endif

#if defined( __cplusplus )
extern "C" {
#endif

typedef struct libvmdk_internal_handle libvmdk_internal_handle_t;

struct libvmdk_internal_handle
{
	/* The current (storage media) offset
	 */
	off64_t current_offset;

	/* The descriptor file
	 */
	libvmdk_descriptor_file_t *descriptor_file;

	/* The extent (file) table
	 */
	libvmdk_extent_table_t *extent_table;

	/* The grain table
	 */
	libvmdk_grain_table_t *grain_table;

	/* The grains cache
	 */
	libfcache_cache_t *grains_cache;

	/* The io handle
	 */
	libvmdk_io_handle_t *io_handle;

	/* The extent data file IO pool
	 */
	libbfio_pool_t *extent_data_file_io_pool;

	/* Value to indicate if the file IO pool was created inside the library
	 */
	uint8_t extent_data_file_io_pool_created_in_library;

	/* The access flags
	 */
	int access_flags;

	/* The maximum number of open handles in the pool
	 */
	int maximum_number_of_open_handles;

	/* The parent handle
	 */
	libvmdk_handle_t *parent_handle;

#if defined( HAVE_LIBVMDK_MULTI_THREAD_SUPPORT )
	/* The read/write lock
	 */
	libcthreads_read_write_lock_t *read_write_lock;
#endif
};

LIBVMDK_EXTERN \
int libvmdk_handle_initialize(
     libvmdk_handle_t **handle,
     libcerror_error_t **error );

LIBVMDK_EXTERN \
int libvmdk_handle_free(
     libvmdk_handle_t **handle,
     libcerror_error_t **error );

LIBVMDK_EXTERN \
int libvmdk_handle_signal_abort(
     libvmdk_handle_t *handle,
     libcerror_error_t **error );

LIBVMDK_EXTERN \
int libvmdk_handle_open(
     libvmdk_handle_t *handle,
     const char *filename,
     int access_flags,
     libcerror_error_t **error );

#if defined( HAVE_WIDE_CHARACTER_TYPE )
LIBVMDK_EXTERN \
int libvmdk_handle_open_wide(
     libvmdk_handle_t *handle,
     const wchar_t *filename,
     int access_flags,
     libcerror_error_t **error );
#endif

LIBVMDK_EXTERN \
int libvmdk_handle_open_file_io_handle(
     libvmdk_handle_t *handle,
     libbfio_handle_t *file_io_handle,
     int access_flags,
     libcerror_error_t **error );

LIBVMDK_EXTERN \
int libvmdk_handle_open_extent_data_files(
     libvmdk_handle_t *handle,
     libcerror_error_t **error );

LIBVMDK_EXTERN \
int libvmdk_handle_open_extent_data_files_file_io_pool(
     libvmdk_handle_t *handle,
     libbfio_pool_t *file_io_pool,
     libcerror_error_t **error );

int libvmdk_handle_open_extent_data_file(
     libvmdk_internal_handle_t *internal_handle,
     libbfio_pool_t *file_io_pool,
     int extent_index,
     const char *filename,
     libcerror_error_t **error );

#if defined( HAVE_WIDE_CHARACTER_TYPE )
int libvmdk_handle_open_extent_data_file_wide(
     libvmdk_internal_handle_t *internal_handle,
     libbfio_pool_t *file_io_pool,
     int extent_index,
     const wchar_t *filename,
     libcerror_error_t **error );
#endif

int libvmdk_handle_open_extent_data_file_io_handle(
     libvmdk_internal_handle_t *internal_handle,
     libbfio_pool_t *file_io_pool,
     int extent_index,
     libbfio_handle_t *file_io_handle,
     libcerror_error_t **error );

LIBVMDK_EXTERN \
int libvmdk_handle_close(
     libvmdk_handle_t *handle,
     libcerror_error_t **error );

int libvmdk_handle_open_read_grain_table(
     libvmdk_internal_handle_t *internal_handle,
     libbfio_pool_t *file_io_pool,
     libcerror_error_t **error );

int libvmdk_handle_open_read_signature(
     libbfio_handle_t *file_io_handle,
     uint8_t *file_type,
     libcerror_error_t **error );

ssize_t libvmdk_internal_handle_read_buffer_from_file_io_pool(
         libvmdk_internal_handle_t *internal_handle,
         libbfio_pool_t *file_io_pool,
         void *buffer,
         size_t buffer_size,
         libcerror_error_t **error );

LIBVMDK_EXTERN \
ssize_t libvmdk_handle_read_buffer(
         libvmdk_handle_t *handle,
         void *buffer,
         size_t buffer_size,
         libcerror_error_t **error );

LIBVMDK_EXTERN \
ssize_t libvmdk_handle_read_buffer_at_offset(
         libvmdk_handle_t *handle,
         void *buffer,
         size_t buffer_size,
         off64_t offset,
         libcerror_error_t **error );

#ifdef TODO_WRITE_SUPPORT

ssize_t libvmdk_internal_handle_write_buffer_to_file_io_pool(
         libvmdk_internal_handle_t *internal_handle,
         libbfio_pool_t *file_io_pool,
         void *buffer,
         size_t buffer_size,
         libcerror_error_t **error );

LIBVMDK_EXTERN \
ssize_t libvmdk_handle_write_buffer(
         libvmdk_handle_t *handle,
         const void *buffer,
         size_t buffer_size,
         libcerror_error_t **error );

LIBVMDK_EXTERN \
ssize_t libvmdk_handle_write_buffer_at_offset(
         libvmdk_handle_t *handle,
         const void *buffer,
         size_t buffer_size,
         off64_t offset,
         libcerror_error_t **error );

#endif /* TODO_WRITE_SUPPORT */

off64_t libvmdk_internal_handle_seek_offset(
         libvmdk_internal_handle_t *internal_handle,
         off64_t offset,
         int whence,
         libcerror_error_t **error );

LIBVMDK_EXTERN \
off64_t libvmdk_handle_seek_offset(
         libvmdk_handle_t *handle,
         off64_t offset,
         int whence,
         libcerror_error_t **error );

LIBVMDK_EXTERN \
int libvmdk_handle_get_offset(
     libvmdk_handle_t *handle,
     off64_t *offset,
     libcerror_error_t **error );

LIBVMDK_EXTERN \
int libvmdk_handle_set_maximum_number_of_open_handles(
     libvmdk_handle_t *handle,
     int maximum_number_of_open_handles,
     libcerror_error_t **error );

LIBVMDK_EXTERN \
int libvmdk_handle_set_parent_handle(
     libvmdk_handle_t *handle,
     libvmdk_handle_t *parent_handle,
     libcerror_error_t **error );

#if defined( __cplusplus )
}
#endif

#endif

