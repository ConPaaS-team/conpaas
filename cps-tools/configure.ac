

AC_INIT([cps-tools], [205])

AM_INIT_AUTOMAKE
AM_PATH_PYTHON([2.7])  # require at least python 2.7 because of argparse module

AM_SILENT_RULES

#AX_PYTHON_MODULE(conpaas)
#AS_IF([test "x${HAVE_PYMOD_CONPAAS}" = "xno"],
#        [AC_MSG_ERROR([conpaas (cpslib) Python module is mandatory.])])

AX_PYTHON_MODULE(argcomplete)
AS_IF([test "x${HAVE_PYMOD_ARGCOMPLETE}" = "xno"],
        [AC_MSG_ERROR([argcomplete Python module is mandatory.])])

AC_CONFIG_FILES(Makefile)
AC_CONFIG_FILES(src/Makefile)
AC_CONFIG_FILES(src/cps_tools/Makefile)

AC_OUTPUT
