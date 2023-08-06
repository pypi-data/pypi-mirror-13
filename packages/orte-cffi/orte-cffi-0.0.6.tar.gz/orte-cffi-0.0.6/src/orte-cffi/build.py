from cffi import FFI
ffi = FFI()

ffi.set_source("orte_cffi", """

int orte_submit_job(char *argv[], void (*launch_cb)(int, void *), void (*finish_cb)(int, int, void *), void *cbdata);

""",
    libraries=[
        "open-rte"
    ],
    library_dirs=[
#        "../../../../../installed/DEBUG/lib",
    ],
    include_dirs=[
    ])

ffi.cdef("""

/* Functions */
int orte_submit_job(char *argv[], void (*launch_cb)(int, void *), void (*finish_cb)(int, int, void *), void *cbdata);

/* Callbacks */
extern "Python" void launch_cb(int, void *);
extern "Python" void finish_cb(int, int, void *);

""")

if __name__ == "__main__":
    ffi.compile()
