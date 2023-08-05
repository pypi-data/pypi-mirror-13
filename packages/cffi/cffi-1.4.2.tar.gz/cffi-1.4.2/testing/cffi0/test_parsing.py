import py, sys, re
from cffi import FFI, FFIError, CDefError, VerificationError

class FakeBackend(object):

    def nonstandard_integer_types(self):
        return {}

    def sizeof(self, name):
        return 1

    def load_library(self, name, flags):
        if sys.platform == 'win32':
            assert name is None or "msvcr" in name
        else:
            assert name is None or "libc" in name or "libm" in name
        return FakeLibrary()

    def new_function_type(self, args, result, has_varargs):
        args = [arg.cdecl for arg in args]
        result = result.cdecl
        return FakeType(
            '<func (%s), %s, %s>' % (', '.join(args), result, has_varargs))

    def new_primitive_type(self, name):
        assert name == name.lower()
        return FakeType('<%s>' % name)

    def new_pointer_type(self, itemtype):
        return FakeType('<pointer to %s>' % (itemtype,))

    def new_struct_type(self, name):
        return FakeStruct(name)

    def complete_struct_or_union(self, s, fields, tp=None,
                                 totalsize=-1, totalalignment=-1, sflags=0):
        assert isinstance(s, FakeStruct)
        s.fields = fields

    def new_array_type(self, ptrtype, length):
        return FakeType('<array %s x %s>' % (ptrtype, length))

    def new_void_type(self):
        return FakeType("<void>")
    def cast(self, x, y):
        return 'casted!'
    def _get_types(self):
        return "CData", "CType"

class FakeType(object):
    def __init__(self, cdecl):
        self.cdecl = cdecl
    def __str__(self):
        return self.cdecl

class FakeStruct(object):
    def __init__(self, name):
        self.name = name
    def __str__(self):
        return ', '.join([str(y) + str(x) for x, y, z in self.fields])

class FakeLibrary(object):

    def load_function(self, BType, name):
        return FakeFunction(BType, name)

class FakeFunction(object):

    def __init__(self, BType, name):
        self.BType = str(BType)
        self.name = name

lib_m = "m"
if sys.platform == 'win32':
    #there is a small chance this fails on Mingw via environ $CC
    import distutils.ccompiler
    if distutils.ccompiler.get_default_compiler() == 'msvc':
        lib_m = 'msvcrt'

def test_simple():
    ffi = FFI(backend=FakeBackend())
    ffi.cdef("double sin(double x);")
    m = ffi.dlopen(lib_m)
    func = m.sin    # should be a callable on real backends
    assert func.name == 'sin'
    assert func.BType == '<func (<double>), <double>, False>'

def test_pipe():
    ffi = FFI(backend=FakeBackend())
    ffi.cdef("int pipe(int pipefd[2]);")
    C = ffi.dlopen(None)
    func = C.pipe
    assert func.name == 'pipe'
    assert func.BType == '<func (<pointer to <int>>), <int>, False>'

def test_vararg():
    ffi = FFI(backend=FakeBackend())
    ffi.cdef("short foo(int, ...);")
    C = ffi.dlopen(None)
    func = C.foo
    assert func.name == 'foo'
    assert func.BType == '<func (<int>), <short>, True>'

def test_no_args():
    ffi = FFI(backend=FakeBackend())
    ffi.cdef("""
        int foo(void);
        """)
    C = ffi.dlopen(None)
    assert C.foo.BType == '<func (), <int>, False>'

def test_typedef():
    ffi = FFI(backend=FakeBackend())
    ffi.cdef("""
        typedef unsigned int UInt;
        typedef UInt UIntReally;
        UInt foo(void);
        """)
    C = ffi.dlopen(None)
    assert str(ffi.typeof("UIntReally")) == '<unsigned int>'
    assert C.foo.BType == '<func (), <unsigned int>, False>'

def test_typedef_more_complex():
    ffi = FFI(backend=FakeBackend())
    ffi.cdef("""
        typedef struct { int a, b; } foo_t, *foo_p;
        int foo(foo_p[]);
        """)
    C = ffi.dlopen(None)
    assert str(ffi.typeof("foo_t")) == '<int>a, <int>b'
    assert str(ffi.typeof("foo_p")) == '<pointer to <int>a, <int>b>'
    assert C.foo.BType == ('<func (<pointer to <pointer to '
                           '<int>a, <int>b>>), <int>, False>')

def test_typedef_array_convert_array_to_pointer():
    ffi = FFI(backend=FakeBackend())
    ffi.cdef("""
        typedef int (*fn_t)(int[5]);
        """)
    with ffi._lock:
        type = ffi._parser.parse_type("fn_t")
        BType = ffi._get_cached_btype(type)
    assert str(BType) == '<func (<pointer to <int>>), <int>, False>'

def test_remove_comments():
    ffi = FFI(backend=FakeBackend())
    ffi.cdef("""
        double /*comment here*/ sin   // blah blah
        /* multi-
           line-
           //comment */  (
        // foo
        double // bar      /* <- ignored, because it's in a comment itself
        x, double/*several*//*comment*/y) /*on the same line*/
        ;
    """)
    m = ffi.dlopen(lib_m)
    func = m.sin
    assert func.name == 'sin'
    assert func.BType == '<func (<double>, <double>), <double>, False>'

def test_remove_line_continuation_comments():
    ffi = FFI(backend=FakeBackend())
    ffi.cdef("""
        double // blah \\
                  more comments
        x(void);
        double // blah\\\\
        y(void);
        double // blah\\ \
                  etc
        z(void);
    """)
    m = ffi.dlopen(lib_m)
    m.x
    m.y
    m.z

def test_line_continuation_in_defines():
    ffi = FFI(backend=FakeBackend())
    ffi.cdef("""
        #define ABC\\
            42
        #define BCD   \\
            43
    """)
    m = ffi.dlopen(lib_m)
    assert m.ABC == 42
    assert m.BCD == 43

def test_define_not_supported_for_now():
    ffi = FFI(backend=FakeBackend())
    e = py.test.raises(CDefError, ffi.cdef, '#define FOO "blah"')
    assert str(e.value) == (
        'only supports one of the following syntax:\n'
        '  #define FOO ...     (literally dot-dot-dot)\n'
        '  #define FOO NUMBER  (with NUMBER an integer'
                                    ' constant, decimal/hex/octal)\n'
        'got:\n'
        '  #define FOO "blah"')

def test_unnamed_struct():
    ffi = FFI(backend=FakeBackend())
    ffi.cdef("typedef struct { int x; } foo_t;\n"
             "typedef struct { int y; } *bar_p;\n")
    assert 'typedef foo_t' in ffi._parser._declarations
    assert 'typedef bar_p' in ffi._parser._declarations
    assert 'anonymous foo_t' in ffi._parser._declarations
    type_foo = ffi._parser.parse_type("foo_t")
    type_bar = ffi._parser.parse_type("bar_p").totype
    assert repr(type_foo) == "<foo_t>"
    assert repr(type_bar) == "<struct $1>"
    py.test.raises(VerificationError, type_bar.get_c_name)
    assert type_foo.get_c_name() == "foo_t"

def test_override():
    ffi = FFI(backend=FakeBackend())
    C = ffi.dlopen(None)
    ffi.cdef("int foo(void);")
    py.test.raises(FFIError, ffi.cdef, "long foo(void);")
    assert C.foo.BType == '<func (), <int>, False>'
    ffi.cdef("long foo(void);", override=True)
    assert C.foo.BType == '<func (), <long>, False>'

def test_cannot_have_only_variadic_part():
    # this checks that we get a sensible error if we try "int foo(...);"
    ffi = FFI()
    e = py.test.raises(CDefError, ffi.cdef, "int foo(...);")
    assert str(e.value) == \
           "foo: a function with only '(...)' as argument is not correct C"

def test_parse_error():
    ffi = FFI()
    e = py.test.raises(CDefError, ffi.cdef, " x y z ")
    assert re.match(r'cannot parse "x y z"\n:\d+:', str(e.value))

def test_cannot_declare_enum_later():
    ffi = FFI()
    e = py.test.raises(NotImplementedError, ffi.cdef,
                       "typedef enum foo_e foo_t; enum foo_e { AA, BB };")
    assert str(e.value) == (
           "enum foo_e: the '{}' declaration should appear on the "
           "first time the enum is mentioned, not later")

def test_unknown_name():
    ffi = FFI()
    e = py.test.raises(CDefError, ffi.cast, "foobarbazunknown", 0)
    assert str(e.value) == "unknown identifier 'foobarbazunknown'"
    e = py.test.raises(CDefError, ffi.cast, "foobarbazunknown*", 0)
    assert str(e.value).startswith('cannot parse "foobarbazunknown*"')
    e = py.test.raises(CDefError, ffi.cast, "int(*)(foobarbazunknown)", 0)
    assert str(e.value).startswith('cannot parse "int(*)(foobarbazunknown)"')

def test_redefine_common_type():
    prefix = "" if sys.version_info < (3,) else "b"
    ffi = FFI()
    ffi.cdef("typedef char FILE;")
    assert repr(ffi.cast("FILE", 123)) == "<cdata 'char' %s'{'>" % prefix
    ffi.cdef("typedef char int32_t;")
    assert repr(ffi.cast("int32_t", 123)) == "<cdata 'char' %s'{'>" % prefix
    ffi = FFI()
    ffi.cdef("typedef int bool, *FILE;")
    assert repr(ffi.cast("bool", 123)) == "<cdata 'int' 123>"
    assert re.match(r"<cdata 'int [*]' 0[xX]?0*7[bB]>",
                    repr(ffi.cast("FILE", 123)))
    ffi = FFI()
    ffi.cdef("typedef bool (*fn_t)(bool, bool);")   # "bool," but within "( )"

def test_bool():
    ffi = FFI()
    ffi.cdef("void f(bool);")
    #
    ffi = FFI()
    ffi.cdef("typedef _Bool bool; void f(bool);")

def test_unknown_argument_type():
    ffi = FFI()
    e = py.test.raises(CDefError, ffi.cdef, "void f(foobarbazzz);")
    assert str(e.value) == ("f arg 1: unknown type 'foobarbazzz' (if you meant"
                            " to use the old C syntax of giving untyped"
                            " arguments, it is not supported)")

def test_void_renamed_as_only_arg():
    ffi = FFI()
    ffi.cdef("typedef void void_t1;"
             "typedef void_t1 void_t;"
             "typedef int (*func_t)(void_t);")
    assert ffi.typeof("func_t").args == ()

def test_WPARAM_on_windows():
    if sys.platform != 'win32':
        py.test.skip("Only for Windows")
    ffi = FFI()
    ffi.cdef("void f(WPARAM);")
    #
    # WPARAM -> UINT_PTR -> unsigned 32/64-bit integer
    ffi = FFI()
    value = int(ffi.cast("WPARAM", -42))
    assert value == sys.maxsize * 2 - 40

def test__is_constant_globalvar():
    for input, expected_output in [
        ("int a;",          False),
        ("const int a;",    True),
        ("int *a;",         False),
        ("const int *a;",   False),
        ("int const *a;",   False),
        ("int *const a;",   True),
        ("int a[5];",       False),
        ("const int a[5];", False),
        ("int *a[5];",      False),
        ("const int *a[5];", False),
        ("int const *a[5];", False),
        ("int *const a[5];", False),
        ("int a[5][6];",       False),
        ("const int a[5][6];", False),
        ]:
        ffi = FFI()
        ffi.cdef(input)
        declarations = ffi._parser._declarations
        assert ('constant a' in declarations) == expected_output
        assert ('variable a' in declarations) == (not expected_output)

def test_restrict():
    from cffi import model
    for input, expected_output in [
        ("int a;",             False),
        ("restrict int a;",    True),
        ("int *a;",            False),
        ]:
        ffi = FFI()
        ffi.cdef(input)
        tp, quals = ffi._parser._declarations['variable a']
        assert bool(quals & model.Q_RESTRICT) == expected_output

def test_different_const_funcptr_types():
    lst = []
    for input in [
        "int(*)(int *a)",
        "int(*)(int const *a)",
        "int(*)(int * const a)",
        "int(*)(int const a[])"]:
        ffi = FFI(backend=FakeBackend())
        lst.append(ffi._parser.parse_type(input))
    assert lst[0] != lst[1]
    assert lst[0] == lst[2]
    assert lst[1] == lst[3]

def test_const_pointer_to_pointer():
    from cffi import model
    ffi = FFI(backend=FakeBackend())
    #
    tp, qual = ffi._parser.parse_type_and_quals("char * * (* const)")
    assert (str(tp), qual) == ("<char * * *>", model.Q_CONST)
    tp, qual = ffi._parser.parse_type_and_quals("char * (* const (*))")
    assert (str(tp), qual) == ("<char * * const *>", 0)
    tp, qual = ffi._parser.parse_type_and_quals("char (* const (* (*)))")
    assert (str(tp), qual) == ("<char * const * *>", 0)
    tp, qual = ffi._parser.parse_type_and_quals("char const * * *")
    assert (str(tp), qual) == ("<char const * * *>", 0)
    tp, qual = ffi._parser.parse_type_and_quals("const char * * *")
    assert (str(tp), qual) == ("<char const * * *>", 0)
    #
    tp, qual = ffi._parser.parse_type_and_quals("char * * * const const")
    assert (str(tp), qual) == ("<char * * *>", model.Q_CONST)
    tp, qual = ffi._parser.parse_type_and_quals("char * * volatile *")
    assert (str(tp), qual) == ("<char * * volatile *>", 0)
    tp, qual = ffi._parser.parse_type_and_quals("char * volatile restrict * *")
    assert (str(tp), qual) == ("<char * __restrict volatile * *>", 0)
    tp, qual = ffi._parser.parse_type_and_quals("char const volatile * * *")
    assert (str(tp), qual) == ("<char volatile const * * *>", 0)
    tp, qual = ffi._parser.parse_type_and_quals("const char * * *")
    assert (str(tp), qual) == ("<char const * * *>", 0)
    #
    tp, qual = ffi._parser.parse_type_and_quals(
        "int(char*const*, short****const*)")
    assert (str(tp), qual) == (
        "<int()(char * const *, short * * * * const *)>", 0)
    tp, qual = ffi._parser.parse_type_and_quals(
        "char*const*(short*const****)")
    assert (str(tp), qual) == (
        "<char * const *()(short * const * * * *)>", 0)

def test_enum():
    ffi = FFI()
    ffi.cdef("""
        enum Enum { POS = +1, TWO = 2, NIL = 0, NEG = -1};
        """)
    C = ffi.dlopen(None)
    assert C.POS == 1
    assert C.TWO == 2
    assert C.NIL == 0
    assert C.NEG == -1

def test_stdcall():
    ffi = FFI()
    tp = ffi.typeof("int(*)(int __stdcall x(int),"
                    "       long (__cdecl*y)(void),"
                    "       short(WINAPI *z)(short))")
    if sys.platform == 'win32' and sys.maxsize < 2**32:
        stdcall = '__stdcall '
    else:
        stdcall = ''
    assert str(tp) == (
        "<ctype 'int(*)(int(%s*)(int), "
                        "long(*)(), "
                        "short(%s*)(short))'>" % (stdcall, stdcall))

def test_extern_python():
    ffi = FFI()
    ffi.cdef("""
        int bok(int, int);
        extern "Python" int foobar(int, int);
        int baz(int, int);
    """)
    assert sorted(ffi._parser._declarations) == [
        'extern_python foobar', 'function baz', 'function bok']
    assert (ffi._parser._declarations['function bok'] ==
            ffi._parser._declarations['extern_python foobar'] ==
            ffi._parser._declarations['function baz'])

def test_extern_python_group():
    ffi = FFI()
    ffi.cdef("""
        int bok(int);
        extern "Python" {int foobar(int, int);int bzrrr(int);}
        int baz(int, int);
    """)
    assert sorted(ffi._parser._declarations) == [
        'extern_python bzrrr', 'extern_python foobar',
        'function baz', 'function bok']
    assert (ffi._parser._declarations['function baz'] ==
            ffi._parser._declarations['extern_python foobar'] !=
            ffi._parser._declarations['function bok'] ==
            ffi._parser._declarations['extern_python bzrrr'])
