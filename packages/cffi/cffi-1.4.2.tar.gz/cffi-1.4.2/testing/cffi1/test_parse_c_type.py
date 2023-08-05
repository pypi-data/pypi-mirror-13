import sys, re, os, py
import cffi
from cffi import cffi_opcode

if '__pypy__' in sys.builtin_module_names:
    py.test.skip("not available on pypy")

cffi_dir = os.path.dirname(cffi_opcode.__file__)

r_macro = re.compile(r"#define \w+[(][^\n]*|#include [^\n]*")
r_define = re.compile(r"(#define \w+) [^\n]*")
r_ifdefs = re.compile(r"(#ifdef |#endif)[^\n]*")
header = open(os.path.join(cffi_dir, 'parse_c_type.h')).read()
header = r_macro.sub(r"", header)
header = r_define.sub(r"\1 ...", header)
header = r_ifdefs.sub(r"", header)

ffi = cffi.FFI()
ffi.cdef(header)

lib = ffi.verify(
        open(os.path.join(cffi_dir, '..', 'c', 'parse_c_type.c')).read() + """
static const char *get_common_type(const char *search, size_t search_len) {
    return NULL;
}
""",    include_dirs=[cffi_dir])

class ParseError(Exception):
    pass

struct_names = ["bar_s", "foo", "foo_", "foo_s", "foo_s1", "foo_s12"]
assert struct_names == sorted(struct_names)

enum_names = ["ebar_s", "efoo", "efoo_", "efoo_s", "efoo_s1", "efoo_s12"]
assert enum_names == sorted(enum_names)

identifier_names = ["id", "id0", "id05", "id05b", "tail"]
assert identifier_names == sorted(identifier_names)

global_names = ["FIVE", "NEG", "ZERO"]
assert global_names == sorted(global_names)

ctx = ffi.new("struct _cffi_type_context_s *")
c_struct_names = [ffi.new("char[]", _n.encode('ascii')) for _n in struct_names]
ctx_structs = ffi.new("struct _cffi_struct_union_s[]", len(struct_names))
for _i in range(len(struct_names)):
    ctx_structs[_i].name = c_struct_names[_i]
ctx_structs[3].flags = lib._CFFI_F_UNION
ctx.struct_unions = ctx_structs
ctx.num_struct_unions = len(struct_names)

c_enum_names = [ffi.new("char[]", _n.encode('ascii')) for _n in enum_names]
ctx_enums = ffi.new("struct _cffi_enum_s[]", len(enum_names))
for _i in range(len(enum_names)):
    ctx_enums[_i].name = c_enum_names[_i]
ctx.enums = ctx_enums
ctx.num_enums = len(enum_names)

c_identifier_names = [ffi.new("char[]", _n.encode('ascii'))
                      for _n in identifier_names]
ctx_identifiers = ffi.new("struct _cffi_typename_s[]", len(identifier_names))
for _i in range(len(identifier_names)):
    ctx_identifiers[_i].name = c_identifier_names[_i]
    ctx_identifiers[_i].type_index = 100 + _i
ctx.typenames = ctx_identifiers
ctx.num_typenames = len(identifier_names)

@ffi.callback("int(unsigned long long *)")
def fetch_constant_five(p):
    p[0] = 5
    return 0
@ffi.callback("int(unsigned long long *)")
def fetch_constant_zero(p):
    p[0] = 0
    return 1
@ffi.callback("int(unsigned long long *)")
def fetch_constant_neg(p):
    p[0] = 123321
    return 1

ctx_globals = ffi.new("struct _cffi_global_s[]", len(global_names))
c_glob_names = [ffi.new("char[]", _n.encode('ascii')) for _n in global_names]
for _i, _fn in enumerate([fetch_constant_five,
                          fetch_constant_neg,
                          fetch_constant_zero]):
    ctx_globals[_i].name = c_glob_names[_i]
    ctx_globals[_i].address = _fn
    ctx_globals[_i].type_op = ffi.cast("_cffi_opcode_t",
                                       cffi_opcode.OP_CONSTANT_INT if _i != 1
                                       else cffi_opcode.OP_ENUM)
ctx.globals = ctx_globals
ctx.num_globals = len(global_names)


def parse(input):
    out = ffi.new("_cffi_opcode_t[]", 100)
    info = ffi.new("struct _cffi_parse_info_s *")
    info.ctx = ctx
    info.output = out
    info.output_size = len(out)
    for j in range(len(out)):
        out[j] = ffi.cast("void *", -424242)
    res = lib.parse_c_type(info, input.encode('ascii'))
    if res < 0:
        raise ParseError(ffi.string(info.error_message).decode('ascii'),
                         info.error_location)
    assert 0 <= res < len(out)
    result = []
    for j in range(len(out)):
        if out[j] == ffi.cast("void *", -424242):
            assert res < j
            break
        i = int(ffi.cast("intptr_t", out[j]))
        if j == res:
            result.append('->')
        result.append(i)
    return result

def parsex(input):
    result = parse(input)
    def str_if_int(x):
        if isinstance(x, str):
            return x
        return '%d,%d' % (x & 255, x >> 8)
    return '  '.join(map(str_if_int, result))

def parse_error(input, expected_msg, expected_location):
    e = py.test.raises(ParseError, parse, input)
    assert e.value.args[0] == expected_msg
    assert e.value.args[1] == expected_location

def make_getter(name):
    opcode = getattr(lib, '_CFFI_OP_' + name)
    def getter(value):
        return opcode | (value << 8)
    return getter

Prim = make_getter('PRIMITIVE')
Pointer = make_getter('POINTER')
Array = make_getter('ARRAY')
OpenArray = make_getter('OPEN_ARRAY')
NoOp = make_getter('NOOP')
Func = make_getter('FUNCTION')
FuncEnd = make_getter('FUNCTION_END')
Struct = make_getter('STRUCT_UNION')
Enum = make_getter('ENUM')
Typename = make_getter('TYPENAME')


def test_simple():
    for simple_type, expected in [
            ("int", lib._CFFI_PRIM_INT),
            ("signed int", lib._CFFI_PRIM_INT),
            ("  long  ", lib._CFFI_PRIM_LONG),
            ("long int", lib._CFFI_PRIM_LONG),
            ("unsigned short", lib._CFFI_PRIM_USHORT),
            ("long double", lib._CFFI_PRIM_LONGDOUBLE),
            ]:
        assert parse(simple_type) == ['->', Prim(expected)]

def test_array():
    assert parse("int[5]") == [Prim(lib._CFFI_PRIM_INT), '->', Array(0), 5]
    assert parse("int[]") == [Prim(lib._CFFI_PRIM_INT), '->', OpenArray(0)]
    assert parse("int[5][8]") == [Prim(lib._CFFI_PRIM_INT),
                                  '->', Array(3),
                                  5,
                                  Array(0),
                                  8]
    assert parse("int[][8]") == [Prim(lib._CFFI_PRIM_INT),
                                 '->', OpenArray(2),
                                 Array(0),
                                 8]

def test_pointer():
    assert parse("int*") == [Prim(lib._CFFI_PRIM_INT), '->', Pointer(0)]
    assert parse("int***") == [Prim(lib._CFFI_PRIM_INT),
                               Pointer(0), Pointer(1), '->', Pointer(2)]

def test_grouping():
    assert parse("int*[]") == [Prim(lib._CFFI_PRIM_INT),
                               Pointer(0), '->', OpenArray(1)]
    assert parse("int**[][8]") == [Prim(lib._CFFI_PRIM_INT),
                                   Pointer(0), Pointer(1),
                                   '->', OpenArray(4), Array(2), 8]
    assert parse("int(*)[]") == [Prim(lib._CFFI_PRIM_INT),
                                 NoOp(3), '->', Pointer(1), OpenArray(0)]
    assert parse("int(*)[][8]") == [Prim(lib._CFFI_PRIM_INT),
                                    NoOp(3), '->', Pointer(1),
                                    OpenArray(4), Array(0), 8]
    assert parse("int**(**)") == [Prim(lib._CFFI_PRIM_INT),
                                  Pointer(0), Pointer(1),
                                  NoOp(2), Pointer(3), '->', Pointer(4)]
    assert parse("int**(**)[]") == [Prim(lib._CFFI_PRIM_INT),
                                    Pointer(0), Pointer(1),
                                    NoOp(6), Pointer(3), '->', Pointer(4),
                                    OpenArray(2)]

def test_simple_function():
    assert parse("int()") == [Prim(lib._CFFI_PRIM_INT),
                              '->', Func(0), FuncEnd(0), 0]
    assert parse("int(int)") == [Prim(lib._CFFI_PRIM_INT),
                                 '->', Func(0), NoOp(4), FuncEnd(0),
                                 Prim(lib._CFFI_PRIM_INT)]
    assert parse("int(long, char)") == [
                                 Prim(lib._CFFI_PRIM_INT),
                                 '->', Func(0), NoOp(5), NoOp(6), FuncEnd(0),
                                 Prim(lib._CFFI_PRIM_LONG),
                                 Prim(lib._CFFI_PRIM_CHAR)]
    assert parse("int(int*)") == [Prim(lib._CFFI_PRIM_INT),
                                  '->', Func(0), NoOp(5), FuncEnd(0),
                                  Prim(lib._CFFI_PRIM_INT),
                                  Pointer(4)]
    assert parse("int*(void)") == [Prim(lib._CFFI_PRIM_INT),
                                   Pointer(0),
                                   '->', Func(1), FuncEnd(0), 0]
    assert parse("int(int, ...)") == [Prim(lib._CFFI_PRIM_INT),
                                      '->', Func(0), NoOp(5), FuncEnd(1), 0,
                                      Prim(lib._CFFI_PRIM_INT)]

def test_internal_function():
    assert parse("int(*)()") == [Prim(lib._CFFI_PRIM_INT),
                                 NoOp(3), '->', Pointer(1),
                                 Func(0), FuncEnd(0), 0]
    assert parse("int(*())[]") == [Prim(lib._CFFI_PRIM_INT),
                                   NoOp(6), Pointer(1),
                                   '->', Func(2), FuncEnd(0), 0,
                                   OpenArray(0)]
    assert parse("int(char(*)(long, short))") == [
        Prim(lib._CFFI_PRIM_INT),
        '->', Func(0), NoOp(6), FuncEnd(0),
        Prim(lib._CFFI_PRIM_CHAR),
        NoOp(7), Pointer(5),
        Func(4), NoOp(11), NoOp(12), FuncEnd(0),
        Prim(lib._CFFI_PRIM_LONG),
        Prim(lib._CFFI_PRIM_SHORT)]

def test_fix_arg_types():
    assert parse("int(char(long, short))") == [
        Prim(lib._CFFI_PRIM_INT),
        '->', Func(0), Pointer(5), FuncEnd(0),
        Prim(lib._CFFI_PRIM_CHAR),
        Func(4), NoOp(9), NoOp(10), FuncEnd(0),
        Prim(lib._CFFI_PRIM_LONG),
        Prim(lib._CFFI_PRIM_SHORT)]
    assert parse("int(char[])") == [
        Prim(lib._CFFI_PRIM_INT),
        '->', Func(0), Pointer(4), FuncEnd(0),
        Prim(lib._CFFI_PRIM_CHAR),
        OpenArray(4)]

def test_enum():
    for i in range(len(enum_names)):
        assert parse("enum %s" % (enum_names[i],)) == ['->', Enum(i)]
        assert parse("enum %s*" % (enum_names[i],)) == [Enum(i),
                                                        '->', Pointer(0)]

def test_error():
    parse_error("short short int", "'short' after another 'short' or 'long'", 6)
    parse_error("long long long", "'long long long' is too long", 10)
    parse_error("short long", "'long' after 'short'", 6)
    parse_error("signed unsigned int", "multiple 'signed' or 'unsigned'", 7)
    parse_error("unsigned signed int", "multiple 'signed' or 'unsigned'", 9)
    parse_error("long char", "invalid combination of types", 5)
    parse_error("short char", "invalid combination of types", 6)
    parse_error("signed void", "invalid combination of types", 7)
    parse_error("unsigned struct", "invalid combination of types", 9)
    #
    parse_error("", "identifier expected", 0)
    parse_error("]", "identifier expected", 0)
    parse_error("*", "identifier expected", 0)
    parse_error("int ]**", "unexpected symbol", 4)
    parse_error("char char", "unexpected symbol", 5)
    parse_error("int(int]", "expected ')'", 7)
    parse_error("int(*]", "expected ')'", 5)
    parse_error("int(]", "identifier expected", 4)
    parse_error("int[?]", "expected a positive integer constant", 4)
    parse_error("int[24)", "expected ']'", 6)
    parse_error("struct", "struct or union name expected", 6)
    parse_error("struct 24", "struct or union name expected", 7)
    parse_error("int[5](*)", "unexpected symbol", 6)
    parse_error("int a(*)", "identifier expected", 6)
    parse_error("int[123456789012345678901234567890]", "number too large", 4)

def test_number_too_large():
    num_max = sys.maxsize
    assert parse("char[%d]" % num_max) == [Prim(lib._CFFI_PRIM_CHAR),
                                          '->', Array(0), num_max]
    parse_error("char[%d]" % (num_max + 1), "number too large", 5)

def test_complexity_limit():
    parse_error("int" + "[]" * 2500, "internal type complexity limit reached",
                202)

def test_struct():
    for i in range(len(struct_names)):
        if i == 3:
            tag = "union"
        else:
            tag = "struct"
        assert parse("%s %s" % (tag, struct_names[i])) == ['->', Struct(i)]
        assert parse("%s %s*" % (tag, struct_names[i])) == [Struct(i),
                                                            '->', Pointer(0)]

def test_exchanging_struct_union():
    parse_error("union %s" % (struct_names[0],),
                "wrong kind of tag: struct vs union", 6)
    parse_error("struct %s" % (struct_names[3],),
                "wrong kind of tag: struct vs union", 7)

def test_identifier():
    for i in range(len(identifier_names)):
        assert parse("%s" % (identifier_names[i])) == ['->', Typename(i)]
        assert parse("%s*" % (identifier_names[i])) == [Typename(i),
                                                        '->', Pointer(0)]

def test_cffi_opcode_sync():
    import cffi.model
    for name in dir(lib):
        if name.startswith('_CFFI_'):
            assert getattr(cffi_opcode, name[6:]) == getattr(lib, name)
    assert sorted(cffi_opcode.PRIMITIVE_TO_INDEX.keys()) == (
        sorted(cffi.model.PrimitiveType.ALL_PRIMITIVE_TYPES.keys()))

def test_array_length_from_constant():
    parse_error("int[UNKNOWN]", "expected a positive integer constant", 4)
    assert parse("int[FIVE]") == [Prim(lib._CFFI_PRIM_INT), '->', Array(0), 5]
    assert parse("int[ZERO]") == [Prim(lib._CFFI_PRIM_INT), '->', Array(0), 0]
    parse_error("int[NEG]", "expected a positive integer constant", 4)

def test_various_constant_exprs():
    def array(n):
        return [Prim(lib._CFFI_PRIM_CHAR), '->', Array(0), n]
    assert parse("char[21]") == array(21)
    assert parse("char[0x10]") == array(16)
    assert parse("char[0X21]") == array(33)
    assert parse("char[0Xb]") == array(11)
    assert parse("char[0x1C]") == array(0x1C)
    assert parse("char[0xc6]") == array(0xC6)
    assert parse("char[010]") == array(8)
    assert parse("char[021]") == array(17)
    parse_error("char[08]", "invalid number", 5)
    parse_error("char[1C]", "invalid number", 5)
    parse_error("char[0C]", "invalid number", 5)
    # not supported (really obscure):
    #    "char[+5]"
    #    "char['A']"

def test_stdcall_cdecl():
    assert parse("int __stdcall(int)") == [Prim(lib._CFFI_PRIM_INT),
                                           '->', Func(0), NoOp(4), FuncEnd(2),
                                           Prim(lib._CFFI_PRIM_INT)]
    assert parse("int __stdcall func(int)") == parse("int __stdcall(int)")
    assert parse("int (__stdcall *)()") == [Prim(lib._CFFI_PRIM_INT),
                                            NoOp(3), '->', Pointer(1),
                                            Func(0), FuncEnd(2), 0]
    assert parse("int (__stdcall *p)()") == parse("int (__stdcall*)()")
    parse_error("__stdcall int", "identifier expected", 0)
    parse_error("__cdecl int", "identifier expected", 0)
    parse_error("int __stdcall", "expected '('", 13)
    parse_error("int __cdecl", "expected '('", 11)
