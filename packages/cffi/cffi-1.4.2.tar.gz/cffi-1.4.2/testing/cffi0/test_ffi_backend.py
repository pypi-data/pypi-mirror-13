import py, sys, platform
import pytest
from testing.cffi0 import backend_tests, test_function, test_ownlib
from cffi import FFI
import _cffi_backend


class TestFFI(backend_tests.BackendTests,
              test_function.TestFunction,
              test_ownlib.TestOwnLib):
    TypeRepr = "<ctype '%s'>"

    @staticmethod
    def Backend():
        return _cffi_backend

    def test_not_supported_bitfield_in_result(self):
        ffi = FFI(backend=self.Backend())
        ffi.cdef("struct foo_s { int a,b,c,d,e; int x:1; };")
        e = py.test.raises(NotImplementedError, ffi.callback,
                           "struct foo_s foo(void)", lambda: 42)
        assert str(e.value) == ("struct foo_s(*)(): "
            "callback with unsupported argument or return type or with '...'")

    def test_inspecttype(self):
        ffi = FFI(backend=self.Backend())
        assert ffi.typeof("long").kind == "primitive"
        assert ffi.typeof("long(*)(long, long**, ...)").cname == (
            "long(*)(long, long * *, ...)")
        assert ffi.typeof("long(*)(long, long**, ...)").ellipsis is True

    def test_new_handle(self):
        ffi = FFI(backend=self.Backend())
        o = [2, 3, 4]
        p = ffi.new_handle(o)
        assert ffi.typeof(p) == ffi.typeof("void *")
        assert ffi.from_handle(p) is o
        assert ffi.from_handle(ffi.cast("char *", p)) is o
        py.test.raises(RuntimeError, ffi.from_handle, ffi.NULL)

    def test_callback_onerror(self):
        ffi = FFI(backend=self.Backend())
        seen = []
        def oops(*args):
            seen.append(args)
        def otherfunc():
            raise LookupError
        def cb(n):
            otherfunc()
        a = ffi.callback("int(*)(int)", cb, error=42, onerror=oops)
        res = a(234)
        assert res == 42
        assert len(seen) == 1
        exc, val, tb = seen[0]
        assert exc is LookupError
        assert isinstance(val, LookupError)
        assert tb.tb_frame.f_code.co_name == 'cb'
        assert tb.tb_frame.f_locals['n'] == 234

    def test_ffi_new_allocator_2(self):
        ffi = FFI(backend=self.Backend())
        seen = []
        def myalloc(size):
            seen.append(size)
            return ffi.new("char[]", b"X" * size)
        def myfree(raw):
            seen.append(raw)
        alloc1 = ffi.new_allocator(myalloc, myfree)
        alloc2 = ffi.new_allocator(alloc=myalloc, free=myfree,
                                   should_clear_after_alloc=False)
        p1 = alloc1("int[10]")
        p2 = alloc2("int[]", 10)
        assert seen == [40, 40]
        assert ffi.typeof(p1) == ffi.typeof("int[10]")
        assert ffi.sizeof(p1) == 40
        assert ffi.typeof(p2) == ffi.typeof("int[]")
        assert ffi.sizeof(p2) == 40
        assert p1[5] == 0
        assert p2[6] == ord('X') * 0x01010101
        raw1 = ffi.cast("char *", p1)
        raw2 = ffi.cast("char *", p2)
        del p1, p2
        retries = 0
        while len(seen) != 4:
            retries += 1
            assert retries <= 5
            import gc; gc.collect()
        assert seen == [40, 40, raw1, raw2]
        assert repr(seen[2]) == "<cdata 'char[]' owning 41 bytes>"
        assert repr(seen[3]) == "<cdata 'char[]' owning 41 bytes>"

    def test_ffi_new_allocator_3(self):
        ffi = FFI(backend=self.Backend())
        seen = []
        def myalloc(size):
            seen.append(size)
            return ffi.new("char[]", b"X" * size)
        alloc1 = ffi.new_allocator(myalloc)    # no 'free'
        p1 = alloc1("int[10]")
        assert seen == [40]
        assert ffi.typeof(p1) == ffi.typeof("int[10]")
        assert ffi.sizeof(p1) == 40
        assert p1[5] == 0

    def test_ffi_new_allocator_4(self):
        ffi = FFI(backend=self.Backend())
        py.test.raises(TypeError, ffi.new_allocator, free=lambda x: None)
        #
        def myalloc2(size):
            raise LookupError
        alloc2 = ffi.new_allocator(myalloc2)
        py.test.raises(LookupError, alloc2, "int[5]")
        #
        def myalloc3(size):
            return 42
        alloc3 = ffi.new_allocator(myalloc3)
        e = py.test.raises(TypeError, alloc3, "int[5]")
        assert str(e.value) == "alloc() must return a cdata object (got int)"
        #
        def myalloc4(size):
            return ffi.cast("int", 42)
        alloc4 = ffi.new_allocator(myalloc4)
        e = py.test.raises(TypeError, alloc4, "int[5]")
        assert str(e.value) == "alloc() must return a cdata pointer, not 'int'"
        #
        def myalloc5(size):
            return ffi.NULL
        alloc5 = ffi.new_allocator(myalloc5)
        py.test.raises(MemoryError, alloc5, "int[5]")


class TestBitfield:
    def check(self, source, expected_ofs_y, expected_align, expected_size):
        # NOTE: 'expected_*' is the numbers expected from GCC.
        # The numbers expected from MSVC are not explicitly written
        # in this file, and will just be taken from the compiler.
        ffi = FFI()
        ffi.cdef("struct s1 { %s };" % source)
        ctype = ffi.typeof("struct s1")
        # verify the information with gcc
        ffi1 = FFI()
        ffi1.cdef("""
            static const int Gofs_y, Galign, Gsize;
            struct s1 *try_with_value(int fieldnum, long long value);
        """)
        fnames = [name for name, cfield in ctype.fields
                       if name and cfield.bitsize > 0]
        setters = ['case %d: s.%s = value; break;' % iname
                   for iname in enumerate(fnames)]
        lib = ffi1.verify("""
            struct s1 { %s };
            struct sa { char a; struct s1 b; };
            #define Gofs_y  offsetof(struct s1, y)
            #define Galign  offsetof(struct sa, b)
            #define Gsize   sizeof(struct s1)
            struct s1 *try_with_value(int fieldnum, long long value)
            {
                static struct s1 s;
                memset(&s, 0, sizeof(s));
                switch (fieldnum) { %s }
                return &s;
            }
        """ % (source, ' '.join(setters)))
        if sys.platform == 'win32':
            expected_ofs_y = lib.Gofs_y
            expected_align = lib.Galign
            expected_size  = lib.Gsize
        else:
            assert (lib.Gofs_y, lib.Galign, lib.Gsize) == (
                expected_ofs_y, expected_align, expected_size)
        # the real test follows
        assert ffi.offsetof("struct s1", "y") == expected_ofs_y
        assert ffi.alignof("struct s1") == expected_align
        assert ffi.sizeof("struct s1") == expected_size
        # compare the actual storage of the two
        for name, cfield in ctype.fields:
            if cfield.bitsize < 0 or not name:
                continue
            if int(ffi.cast(cfield.type, -1)) == -1:   # signed
                min_value = -(1 << (cfield.bitsize-1))
                max_value = (1 << (cfield.bitsize-1)) - 1
            else:
                min_value = 0
                max_value = (1 << cfield.bitsize) - 1
            for t in [1, 2, 4, 8, 16, 128, 2813, 89728, 981729,
                     -1,-2,-4,-8,-16,-128,-2813,-89728,-981729]:
                if min_value <= t <= max_value:
                    self._fieldcheck(ffi, lib, fnames, name, t)

    def _fieldcheck(self, ffi, lib, fnames, name, value):
        s = ffi.new("struct s1 *")
        setattr(s, name, value)
        assert getattr(s, name) == value
        raw1 = ffi.buffer(s)[:]
        t = lib.try_with_value(fnames.index(name), value)
        raw2 = ffi.buffer(t, len(raw1))[:]
        assert raw1 == raw2

    def test_bitfield_basic(self):
        self.check("int a; int b:9; int c:20; int y;", 8, 4, 12)
        self.check("int a; short b:9; short c:7; int y;", 8, 4, 12)
        self.check("int a; short b:9; short c:9; int y;", 8, 4, 12)

    def test_bitfield_reuse_if_enough_space(self):
        self.check("int a:2; char y;", 1, 4, 4)
        self.check("int a:1; char b  ; int c:1; char y;", 3, 4, 4)
        self.check("int a:1; char b:8; int c:1; char y;", 3, 4, 4)
        self.check("char a; int b:9; char y;", 3, 4, 4)
        self.check("char a; short b:9; char y;", 4, 2, 6)
        self.check("int a:2; char b:6; char y;", 1, 4, 4)
        self.check("int a:2; char b:7; char y;", 2, 4, 4)
        self.check("int a:2; short b:15; char c:2; char y;", 5, 4, 8)
        self.check("int a:2; char b:1; char c:1; char y;", 1, 4, 4)

    @pytest.mark.skipif("platform.machine().startswith(('arm', 'aarch64'))")
    def test_bitfield_anonymous_no_align(self):
        L = FFI().alignof("long long")
        self.check("char y; int :1;", 0, 1, 2)
        self.check("char x; int z:1; char y;", 2, 4, 4)
        self.check("char x; int  :1; char y;", 2, 1, 3)
        self.check("char x; long long z:48; char y;", 7, L, 8)
        self.check("char x; long long  :48; char y;", 7, 1, 8)
        self.check("char x; long long z:56; char y;", 8, L, 8 + L)
        self.check("char x; long long  :56; char y;", 8, 1, 9)
        self.check("char x; long long z:57; char y;", L + 8, L, L + 8 + L)
        self.check("char x; long long  :57; char y;", L + 8, 1, L + 9)

    @pytest.mark.skipif(
        "not platform.machine().startswith(('arm', 'aarch64'))")
    def test_bitfield_anonymous_align_arm(self):
        L = FFI().alignof("long long")
        self.check("char y; int :1;", 0, 4, 4)
        self.check("char x; int z:1; char y;", 2, 4, 4)
        self.check("char x; int  :1; char y;", 2, 4, 4)
        self.check("char x; long long z:48; char y;", 7, L, 8)
        self.check("char x; long long  :48; char y;", 7, 8, 8)
        self.check("char x; long long z:56; char y;", 8, L, 8 + L)
        self.check("char x; long long  :56; char y;", 8, L, 8 + L)
        self.check("char x; long long z:57; char y;", L + 8, L, L + 8 + L)
        self.check("char x; long long  :57; char y;", L + 8, L, L + 8 + L)

    @pytest.mark.skipif("platform.machine().startswith(('arm', 'aarch64'))")
    def test_bitfield_zero(self):
        L = FFI().alignof("long long")
        self.check("char y; int :0;", 0, 1, 4)
        self.check("char x; int :0; char y;", 4, 1, 5)
        self.check("char x; int :0; int :0; char y;", 4, 1, 5)
        self.check("char x; long long :0; char y;", L, 1, L + 1)
        self.check("short x, y; int :0; int :0;", 2, 2, 4)
        self.check("char x; int :0; short b:1; char y;", 5, 2, 6)
        self.check("int a:1; int :0; int b:1; char y;", 5, 4, 8)

    @pytest.mark.skipif(
        "not platform.machine().startswith(('arm', 'aarch64'))")
    def test_bitfield_zero_arm(self):
        L = FFI().alignof("long long")
        self.check("char y; int :0;", 0, 4, 4)
        self.check("char x; int :0; char y;", 4, 4, 8)
        self.check("char x; int :0; int :0; char y;", 4, 4, 8)
        self.check("char x; long long :0; char y;", L, 8, L + 8)
        self.check("short x, y; int :0; int :0;", 2, 4, 4)
        self.check("char x; int :0; short b:1; char y;", 5, 4, 8)
        self.check("int a:1; int :0; int b:1; char y;", 5, 4, 8)

    def test_error_cases(self):
        ffi = FFI()
        py.test.raises(TypeError,
            'ffi.cdef("struct s1 { float x:1; };"); ffi.new("struct s1 *")')
        py.test.raises(TypeError,
            'ffi.cdef("struct s2 { char x:0; };"); ffi.new("struct s2 *")')
        py.test.raises(TypeError,
            'ffi.cdef("struct s3 { char x:9; };"); ffi.new("struct s3 *")')

    def test_struct_with_typedef(self):
        ffi = FFI()
        ffi.cdef("typedef struct { float x; } foo_t;")
        p = ffi.new("foo_t *", [5.2])
        assert repr(p).startswith("<cdata 'foo_t *' ")

    def test_struct_array_no_length(self):
        ffi = FFI()
        ffi.cdef("struct foo_s { int x; int a[]; };")
        p = ffi.new("struct foo_s *", [100, [200, 300, 400]])
        assert p.x == 100
        assert ffi.typeof(p.a) is ffi.typeof("int *")   # no length available
        assert p.a[0] == 200
        assert p.a[1] == 300
        assert p.a[2] == 400

    @pytest.mark.skipif("sys.platform != 'win32'")
    def test_getwinerror(self):
        ffi = FFI()
        code, message = ffi.getwinerror(1155)
        assert code == 1155
        assert message == ("No application is associated with the "
                           "specified file for this operation")
        ffi.cdef("void SetLastError(int);")
        lib = ffi.dlopen("Kernel32.dll")
        lib.SetLastError(2)
        code, message = ffi.getwinerror()
        assert code == 2
        assert message == "The system cannot find the file specified"
        code, message = ffi.getwinerror(-1)
        assert code == 2
        assert message == "The system cannot find the file specified"

    def test_from_buffer(self):
        import array
        ffi = FFI()
        a = array.array('H', [10000, 20000, 30000])
        c = ffi.from_buffer(a)
        assert ffi.typeof(c) is ffi.typeof("char[]")
        ffi.cast("unsigned short *", c)[1] += 500
        assert list(a) == [10000, 20500, 30000]

    def test_memmove(self):
        ffi = FFI()
        p = ffi.new("short[]", [-1234, -2345, -3456, -4567, -5678])
        ffi.memmove(p, p + 1, 4)
        assert list(p) == [-2345, -3456, -3456, -4567, -5678]
        p[2] = 999
        ffi.memmove(p + 2, p, 6)
        assert list(p) == [-2345, -3456, -2345, -3456, 999]
        ffi.memmove(p + 4, ffi.new("char[]", b"\x71\x72"), 2)
        if sys.byteorder == 'little':
            assert list(p) == [-2345, -3456, -2345, -3456, 0x7271]
        else:
            assert list(p) == [-2345, -3456, -2345, -3456, 0x7172]

    def test_memmove_buffer(self):
        import array
        ffi = FFI()
        a = array.array('H', [10000, 20000, 30000])
        p = ffi.new("short[]", 5)
        ffi.memmove(p, a, 6)
        assert list(p) == [10000, 20000, 30000, 0, 0]
        ffi.memmove(p + 1, a, 6)
        assert list(p) == [10000, 10000, 20000, 30000, 0]
        b = array.array('h', [-1000, -2000, -3000])
        ffi.memmove(b, a, 4)
        assert b.tolist() == [10000, 20000, -3000]
        assert a.tolist() == [10000, 20000, 30000]
        p[0] = 999
        p[1] = 998
        p[2] = 997
        p[3] = 996
        p[4] = 995
        ffi.memmove(b, p, 2)
        assert b.tolist() == [999, 20000, -3000]
        ffi.memmove(b, p + 2, 4)
        assert b.tolist() == [997, 996, -3000]
        p[2] = -p[2]
        p[3] = -p[3]
        ffi.memmove(b, p + 2, 6)
        assert b.tolist() == [-997, -996, 995]

    def test_memmove_readonly_readwrite(self):
        ffi = FFI()
        p = ffi.new("signed char[]", 5)
        ffi.memmove(p, b"abcde", 3)
        assert list(p) == [ord("a"), ord("b"), ord("c"), 0, 0]
        ffi.memmove(p, bytearray(b"ABCDE"), 2)
        assert list(p) == [ord("A"), ord("B"), ord("c"), 0, 0]
        py.test.raises((TypeError, BufferError), ffi.memmove, b"abcde", p, 3)
        ba = bytearray(b"xxxxx")
        ffi.memmove(dest=ba, src=p, n=3)
        assert ba == bytearray(b"ABcxx")

    def test_all_primitives(self):
        ffi = FFI()
        for name in [
            "char",
            "short",
            "int",
            "long",
            "long long",
            "signed char",
            "unsigned char",
            "unsigned short",
            "unsigned int",
            "unsigned long",
            "unsigned long long",
            "float",
            "double",
            "long double",
            "wchar_t",
            "_Bool",
            "int8_t",
            "uint8_t",
            "int16_t",
            "uint16_t",
            "int32_t",
            "uint32_t",
            "int64_t",
            "uint64_t",
            "int_least8_t",
            "uint_least8_t",
            "int_least16_t",
            "uint_least16_t",
            "int_least32_t",
            "uint_least32_t",
            "int_least64_t",
            "uint_least64_t",
            "int_fast8_t",
            "uint_fast8_t",
            "int_fast16_t",
            "uint_fast16_t",
            "int_fast32_t",
            "uint_fast32_t",
            "int_fast64_t",
            "uint_fast64_t",
            "intptr_t",
            "uintptr_t",
            "intmax_t",
            "uintmax_t",
            "ptrdiff_t",
            "size_t",
            "ssize_t",
            ]:
            x = ffi.sizeof(name)
            assert 1 <= x <= 16
