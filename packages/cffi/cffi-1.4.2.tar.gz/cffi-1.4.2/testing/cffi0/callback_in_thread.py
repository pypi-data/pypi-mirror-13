import sys, time
sys.path.insert(0, sys.argv[1])
from cffi import FFI

def _run_callback_in_thread():
    ffi = FFI()
    ffi.cdef("""
        typedef int (*mycallback_func_t)(int, int);
        int threaded_ballback_test(mycallback_func_t mycb);
    """)
    lib = ffi.verify("""
        #include <pthread.h>
        typedef int (*mycallback_func_t)(int, int);
        void *my_wait_function(void *ptr) {
            mycallback_func_t cbfunc = (mycallback_func_t)ptr;
            cbfunc(10, 10);
            cbfunc(12, 15);
            return NULL;
        }
        int threaded_ballback_test(mycallback_func_t mycb) {
            pthread_t thread;
            pthread_create(&thread, NULL, my_wait_function, (void*)mycb);
            return 0;
        }
    """, extra_compile_args=['-pthread'])
    seen = []
    @ffi.callback('int(*)(int,int)')
    def mycallback(x, y):
        time.sleep(0.022)
        seen.append((x, y))
        return 0
    lib.threaded_ballback_test(mycallback)
    count = 300
    while len(seen) != 2:
        time.sleep(0.01)
        count -= 1
        assert count > 0, "timeout"
    assert seen == [(10, 10), (12, 15)]

print('STARTING')
_run_callback_in_thread()
print('DONE')
