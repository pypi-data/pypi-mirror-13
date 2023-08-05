/*
 * The internal type definitions
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

#if !defined( _LIBVMDK_INTERNAL_TYPES_H )
#define _LIBVMDK_INTERNAL_TYPES_H

#include <common.h>
#include <types.h>

/* Define HAVE_LOCAL_LIBVMDK for local use of libvhdi
 * The definitions in <libvhdi/types.h> are copied here
 * for local use of libvhdi
 */
#if defined( HAVE_LOCAL_LIBVMDK )

/* The following type definitions hide internal data structures
 */
#if defined( HAVE_DEBUG_OUTPUT )
typedef struct libvhdi_extent_descriptor {}	libvhdi_extent_descriptor_t;
typedef struct libvhdi_handle {}		libvhdi_handle_t;

#else
typedef intptr_t libvhdi_extent_descriptor_t;
typedef intptr_t libvhdi_handle_t;

#endif /* defined( HAVE_DEBUG_OUTPUT ) */

#endif /* defined( HAVE_LOCAL_LIBVMDK ) */

/* The largest primary (or scalar) available
 * supported by a single load and store instruction
 */
typedef unsigned long int libvmdk_aligned_t;

#endif

