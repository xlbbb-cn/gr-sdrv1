find_package(PkgConfig)

PKG_CHECK_MODULES(PC_GR_SDRV1 gnuradio-sdrv1)

FIND_PATH(
    GR_SDRV1_INCLUDE_DIRS
    NAMES gnuradio/sdrv1/api.h
    HINTS $ENV{SDRV1_DIR}/include
        ${PC_SDRV1_INCLUDEDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/include
          /usr/local/include
          /usr/include
)

FIND_LIBRARY(
    GR_SDRV1_LIBRARIES
    NAMES gnuradio-sdrv1
    HINTS $ENV{SDRV1_DIR}/lib
        ${PC_SDRV1_LIBDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/lib
          ${CMAKE_INSTALL_PREFIX}/lib64
          /usr/local/lib
          /usr/local/lib64
          /usr/lib
          /usr/lib64
          )

include("${CMAKE_CURRENT_LIST_DIR}/gnuradio-sdrv1Target.cmake")

INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(GR_SDRV1 DEFAULT_MSG GR_SDRV1_LIBRARIES GR_SDRV1_INCLUDE_DIRS)
MARK_AS_ADVANCED(GR_SDRV1_LIBRARIES GR_SDRV1_INCLUDE_DIRS)
