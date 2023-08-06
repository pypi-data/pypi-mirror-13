from cffi import FFI
ffi = FFI()

ffi.set_source("orte_cffi", """

#include "orte/orted/orted_submit.h"

""",
    libraries=[
        "open-rte"
    ],
    library_dirs=[
        "/Users/mark/proj/openmpi/installed/DEBUG/lib",
    ],
    include_dirs=[
        #"/Users/mark/proj/openmpi/installed/DEBUG/include",
        #"/Users/mark/proj/openmpi/installed/DEBUG/include/openmpi",
        #"/Users/mark/proj/openmpi/installed/DEBUG/include/openmpi/opal/mca/hwloc/hwloc1112/hwloc/include",
        #"/Users/mark/proj/openmpi/installed/DEBUG/include/openmpi/opal/mca/event/libevent2022/libevent",
        #"/Users/mark/proj/openmpi/installed/DEBUG/include/openmpi/opal/mca/event/libevent2022/libevent/include"
    ])

ffi.cdef("""

/* Types */
typedef ... orte_job_t;
typedef void (*orte_submit_cbfunc_t)(int index, orte_job_t *jdata, int ret, void *cbdata);

/* Functions */
int orte_submit_init(int argc, char *argv[]);
int orte_submit_job(char *cmd[],
                    orte_submit_cbfunc_t launch_cb, void *launch_cbdata,
                    orte_submit_cbfunc_t complete_cb, void *complete_cbdata);
void orte_submit_finalize(void);

/* Callbacks */
extern "Python" void launch_cb(int, orte_job_t *, int, void *);
extern "Python" void finish_cb(int, orte_job_t *, int, void *);

""")

if __name__ == "__main__":
    ffi.compile()
