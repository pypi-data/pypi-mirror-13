import py, sys, os
import _cffi_backend

def test_no_unknown_exported_symbols():
    if not hasattr(_cffi_backend, '__file__'):
        py.test.skip("_cffi_backend module is built-in")
    if not sys.platform.startswith('linux'):
        py.test.skip("linux-only")
    g = os.popen("objdump -T '%s'" % _cffi_backend.__file__, 'r')
    for line in g:
        if not line.startswith('0'):
            continue
        if '*UND*' in line:
            continue
        name = line.split()[-1]
        if name.startswith('_') or name.startswith('.'):
            continue
        if name not in ('init_cffi_backend', 'PyInit__cffi_backend'):
            raise Exception("Unexpected exported name %r" % (name,))
    g.close()
