from cffi import FFI
ffi = FFI()

ffi.set_source("orte_cffi", """

//#include "opal/util/opal_environ.h"
//#include "orte/mca/plm/plm.h"

//#include "orted_submit.h"

""",
    libraries=[
#        "submit",
#        "open-pal",
#        "open-rte"
    ],
    library_dirs=[
#        "../../../../../installed/DEBUG/lib",
#        "/Users/mark/proj/openmpi/mysubmit"
    ],
    include_dirs=[
#        "../../include",
#        "../../../build/opal/include",
#        "../../../opal/include",
#        "../../..",
#        "../../../opal/mca/event/libevent2022/libevent",
#        "../../../build/opal/mca/hwloc/hwloc1112/hwloc/include",
#        "../../../build/opal/mca/event/libevent2022/libevent/include",
#        "../../../opal/mca/event/libevent2022/libevent/include",
#        "../../../opal/mca/hwloc/hwloc1112/hwloc/include",
#        "../../../orte/orted"
    ])

ffi.cdef("""

/* Constants */
//#define OPAL_EVLOOP_ONCE ...

/* Functions */
//int submit_job(char *argv[], void (*launch_cb)(int, void *), void (*finish_cb)(int, int, void *), void *cbdata);
//int orte_submit_job(char *argv[], void (*launch_cb)(int), void (*finish_cb)(int, int));
//int opal_event_loop(struct event_base *, int);

/* Callbacks */
extern "Python" void launch_cb(int, void *);
extern "Python" void finish_cb(int, int, void *);

/* Variables */
//typedef struct event_base opal_event_base_t;
//opal_event_base_t *orte_event_base = {0};

""")

if __name__ == "__main__":
    ffi.compile()
