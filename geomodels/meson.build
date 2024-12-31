
use_subproject = false
if get_option('geographiclib') == 'external'
    geographiclib_dep = dependency('geographiclib', required: true)  # , version: '>=2.5')
elif get_option('geographiclib') == 'internal'
    use_subproject = true
else  # get_option('geographiclib') == 'auto'
    geographiclib_dep = dependency('geographiclib')  # , version: '>=2.5')
    use_subproject = not geographiclib_dep.found()
endif

if use_subproject
    message('use_subproject: ' + use_subproject.to_string())
    cmake = import('cmake')
    opt_var = cmake.subproject_options()
    opt_var.add_cmake_defines(
        {
            'BUILD_BOTH_LIBS': false,
            'BUILD_SHARED_LIBS': false,
            'BUILD_MANPAGES': false,
            'CMAKE_POSITION_INDEPENDENT_CODE': true,
            'BINDIR': '',
        }
    )

    geographiclib_proj = cmake.subproject('geographiclib', options: opt_var)
    geographiclib_dep = geographiclib_proj.dependency('GeographicLib_STATIC')
endif

py = import('python').find_installation(pure: false)

py.extension_module(
    '_ext',
    '_ext.pyx',
    dependencies: geographiclib_dep,
    install: true,
    subdir: meson.project_name(),
    override_options : ['cython_language=cpp'],
)

python_sources = [
    'cli.py',
    'data.py',
    'error.py',
    '__init__.py',
    '__main__.py',
    '_typing.py',
    '_utils.py',
    '_version.py',
    'wmmf.py',
]

py.install_sources(
    python_sources,
    # pure: false,
    subdir: meson.project_name(),
)

python_tests_sources = [
    'tests/__init__.py',
    'tests/test_cli.py',
    'tests/test_common.py',
    'tests/test_data.py',
    'tests/test_geoid.py',
    'tests/test_gravity.py',
    'tests/test_magnetic.py',
    'tests/test_wmmf.py',
    'tests/utils.py',
]

py.install_sources(
    python_tests_sources,
    # pure: false,
    subdir: meson.project_name() + '/tests',
)

python_test_data = [
    'tests/data/igrf12coeffs.txt',
]

py.install_sources(
    python_test_data,
    # pure: false,
    subdir: meson.project_name() + '/tests/data',
)
