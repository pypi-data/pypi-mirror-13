#include "Python.h"
#include <structmember.h>

struct module_state {
    PyObject *error;
};

#if PY_MAJOR_VERSION >= 3
#define GETSTATE(m) ((struct module_state*)PyModule_GetState(m))
#endif

static PyMethodDef cachesim_methods[] = {
    {NULL, NULL}
};

typedef struct Cache {
    PyObject_HEAD
    unsigned int sets;
    unsigned int set_bits;
    unsigned int ways;
    unsigned int way_bits;
    unsigned int cl_size;
    unsigned int cl_bits;
    unsigned int strategy; // 0 = FIFO, 1 = LRU, 2 = MRU, 3 = RR (state is kept in the ordering)
    // for LFU an additional field would be required to capture state
    unsigned int *placement;
    PyObject *parent;
    unsigned int LOAD;
    unsigned int STORE;
    unsigned int HIT;
    unsigned int MISS;
} Cache;

static void Cache_dealloc(Cache* self) {
    Py_XDECREF(self->parent); // Causes a segfault, but why?
    PyMem_Del(self->placement);
    Py_TYPE(self)->tp_free((PyObject*)self);
}

unsigned int log2_uint(unsigned int x) {
  unsigned int ans = 0;
  while(x >>= 1) {
      ans++;
  }
  return ans;
}

static PyMemberDef Cache_members[] = {
    {"sets", T_UINT, offsetof(Cache, sets), 0,
     "number of sets available"},
    {"ways", T_UINT, offsetof(Cache, ways), 0,
     "number of ways available"},
    {"way_bits", T_UINT, offsetof(Cache, way_bits), 0,
     "number of bits used to identiy ways"},
    {"cl_size", T_UINT, offsetof(Cache, cl_size), 0,
     "number of bytes in a cacheline"},
    {"cl_bits", T_UINT, offsetof(Cache, cl_bits), 0,
     "number of bits used to identiy individual bytes in a cacheline"},
    {"cl_size", T_UINT, offsetof(Cache, cl_size), 0,
     "number of bytes in a cacheline"},
    {"strategy", T_UINT, offsetof(Cache, strategy), 0,
     "replacement strategy of cachlevel"},
    {"parent", T_OBJECT_EX, offsetof(Cache, parent), 0,
     "parent Cache object (cache level which is closer to main memory)"},
    {"LOAD", T_UINT, offsetof(Cache, LOAD), 0,
     "number of loads performed since last counter reset"},
    {"STORE", T_UINT, offsetof(Cache, STORE), 0,
     "number of stores performed since last counter reset"},
    {"HIT", T_UINT, offsetof(Cache, HIT), 0,
     "number of cache hits since last counter reset"},
    {"MISS", T_UINT, offsetof(Cache, MISS), 0,
     "number of misses since last counter reset"},
    {NULL}  /* Sentinel */
};

inline static unsigned int Cache__get_cacheline_id(Cache* self, unsigned int addr) {
    return addr >> self->cl_bits;
}

inline static unsigned int Cache__get_set_id(Cache* self, unsigned int cl_id) {
    return (cl_id >> self->way_bits) % self->sets;
}

static void Cache__load(Cache* self, unsigned int addr) {
    self->LOAD++;
    unsigned int cl_id = Cache__get_cacheline_id(self, addr);
    unsigned int set_id = Cache__get_set_id(self, cl_id);
    if(self->ways == 8) { //&& self->LOAD < 200) {
        // PySys_WriteStdout("LOAD=%i addr=%i cl_id=%i set_id=%i\n", self->LOAD, addr, cl_id, set_id);
    }

    // Check if cl_id is already cached
    // TODO use sorted data structure for faster searches?
    for(int i=0; i<self->ways; i++) {
        if(self->placement[set_id*self->ways+i] == cl_id) {
            // HIT: Found it!
            self->HIT++;
            // if(self->ways == 16 && set_id == 0 && self->MISS == 0) {
            //     PySys_WriteStdout("HIT(L3) self->LOAD=%i addr=%i cl_id=%i set_id=%i\n", self->LOAD, addr, cl_id, set_id);
            //     PySys_WriteStdout("CACHED_B(L3) [%i %i %i %i %i %i %i %i %i %i %i %i %i %i %i %i]\n", self->placement[set_id*self->ways+0], self->placement[set_id*self->ways+1], self->placement[set_id*self->ways+2], self->placement[set_id*self->ways+3], self->placement[set_id*self->ways+4], self->placement[set_id*self->ways+5], self->placement[set_id*self->ways+6], self->placement[set_id*self->ways+7], self->placement[set_id*self->ways+8], self->placement[set_id*self->ways+9], self->placement[set_id*self->ways+10], self->placement[set_id*self->ways+11], self->placement[set_id*self->ways+12], self->placement[set_id*self->ways+13], self->placement[set_id*self->ways+14], self->placement[set_id*self->ways+15]);
            // }

            if(self->strategy == 0 || self->strategy == 3) {
                // FIFO: nothing to do
                // RR: nothing to do
            } else if(self->strategy == 1 || self->strategy == 2) {
                // LRU: Reorder elements to account for access to element
                // MRU: Reorder elements to account for access to element
                if(i != 0) {
                    for(int j=i; j>0; j--) {
                        self->placement[set_id*self->ways+j] =
                            self->placement[set_id*self->ways+j-1];
                    }
                    self->placement[set_id*self->ways] = cl_id;
                }
            }
            return;
        }
    }

    // MISS!
    self->MISS++;
    if(self->ways == 8) {//self->LOAD < 200) {
        // PySys_WriteStdout("CACHED [%i %i %i %i %i %i %i %i]\n", self->placement[set_id*self->ways+0], self->placement[set_id*self->ways+1], self->placement[set_id*self->ways+2], self->placement[set_id*self->ways+3], self->placement[set_id*self->ways+4], self->placement[set_id*self->ways+5], self->placement[set_id*self->ways+6], self->placement[set_id*self->ways+7]);
        // PySys_WriteStdout("MISS self->LOAD=%i addr=%i cl_id=%i set_id=%i\n", self->LOAD, addr, cl_id, set_id);
    }

    // Load from lower cachelevel
    if(self->parent != NULL) {
        Py_INCREF(self->parent);
        Cache__load((Cache*)(self->parent), addr);
        Py_DECREF(self->parent);
    }

    // Replace other cacheline according to strategy (using placement order as state)
    if(self->strategy == 0 || self->strategy == 1) {
        // FIFO: add to front of queue
        // LRU: add to front of queue
        if(self->ways == 8) { // && self->LOAD < 200) {
            // PySys_WriteStdout("REPLACED %i with %i\n", self->placement[set_id*self->ways+self->ways-1], cl_id);
        }
        for(int i=self->ways-1; i>0; i--) {
            self->placement[set_id*self->ways+i] = self->placement[set_id*self->ways+i-1];
        }
        self->placement[set_id*self->ways] = cl_id;
    } else if(self->strategy == 2) {
        // MRU: add to end of queue
        for(int i=0; i>self->ways-1; i++) {
            self->placement[set_id*self->ways+i] = self->placement[set_id*self->ways+i+1];
        }
        self->placement[set_id*self->ways+self->ways-1] = cl_id;
    } else if(self->strategy == 3) {
        // RR: replace random element
        int i = rand() & (self->ways - 1);
        self->placement[set_id*self->ways+i] = cl_id;
    }
}

static void Cache__store(Cache* self, unsigned int addr) {
    self->STORE++;
    // unsigned int cl_id = Cache__get_cacheline_id(self, addr);
    // unsigned int set_id = Cache__get_set_id(self, cl_id);
    //PySys_WriteStdout("STORE=%i addr=%i cl_id=%i set_id=%i\n", self->LOAD, addr, cl_id, set_id);

    // Load from lower cachelevel
    if(self->parent != NULL) {
        Py_INCREF(self->parent);
        Cache__store((Cache*)(self->parent), addr);
        Py_DECREF(self->parent);
    }
}

static PyObject* Cache_load(Cache* self, PyObject *args, PyObject *kwds)
{
    unsigned int addr;
    unsigned int length = 1;
    
    static char *kwlist[] = {"addr", "length", NULL};
    PyArg_ParseTupleAndKeywords(args, kwds, "I|I", kwlist, &addr, &length);
    
    // Doing this in c, tremendously increases the speed for multiple elements
    for(int i=0; i<length; i++) {
        Cache__load(self, addr+i);
    }
    Py_RETURN_NONE;
}

static PyObject* Cache_iterload(Cache* self, PyObject *args, PyObject *kwds)
{
    PyObject *addrs;
    unsigned int length = 1;
    
    static char *kwlist[] = {"addrs", "length", NULL};
    PyArg_ParseTupleAndKeywords(args, kwds, "O|I", kwlist, &addrs, &length);
    
    // Get and check iterator
    PyObject *addrs_iter = PyObject_GetIter(addrs);
    if(addrs_iter == NULL) {
        PyErr_SetString(PyExc_ValueError, "addrs is not iteratable");
        return NULL;
    }
    
    // Iterate of elements in addrs
    PyObject *addr;
    while((addr = PyIter_Next(addrs_iter))) {
        // Each address is expanded to a certain length (default is 1)
        for(int i=0; i<length; i++) {
#if PY_MAJOR_VERSION >= 3
            Cache__load(self, PyLong_AsUnsignedLong(addr)+i);
#else
            Cache__load(self, PyInt_AsUnsignedLongLongMask(addr)+i);
#endif
        }
        Py_DECREF(addr);
    }
    Py_DECREF(addrs_iter);
    Py_RETURN_NONE;
}

static PyObject* Cache_store(Cache* self, PyObject *args, PyObject *kwds)
{
    unsigned int addr;
    unsigned int length = 1;
    
    static char *kwlist[] = {"addr", "length", NULL};
    PyArg_ParseTupleAndKeywords(args, kwds, "I|I", kwlist, &addr, &length);
    
    // Doing this in c, tremendously increases the speed for multiple elements
    for(int i=0; i<length; i++) {
        Cache__store(self, addr+i);
    }
    Py_RETURN_NONE;
}

static PyObject* Cache_iterstore(Cache* self, PyObject *args, PyObject *kwds)
{
    PyObject *addrs;
    unsigned int length = 1;
    
    static char *kwlist[] = {"addrs", "length", NULL};
    PyArg_ParseTupleAndKeywords(args, kwds, "O|I", kwlist, &addrs, &length);
    
    // Get and check iterator
    PyObject *addrs_iter = PyObject_GetIter(addrs);
    if(addrs_iter == NULL) {
        PyErr_SetString(PyExc_ValueError, "addrs is not iteratable");
        return NULL;
    }
    
    // Iterate of elements in addrs
    PyObject *addr;
    while((addr = PyIter_Next(addrs_iter))) {
        // Each address is expanded to a certain length (default is 1)
        for(int i=0; i<length; i++) {
#if PY_MAJOR_VERSION >= 3
            Cache__store(self, PyLong_AsUnsignedLong(addr)+i);
#else
            Cache__store(self, PyInt_AsUnsignedLongLongMask(addr)+i);
#endif
        }
        Py_DECREF(addr);
    }
    Py_DECREF(addrs_iter);
    Py_RETURN_NONE;
}

static PyObject* Cache_contains(Cache* self, PyObject *args, PyObject *kwds) {
    unsigned int addr;

    static char *kwlist[] = {"addr", NULL};
    PyArg_ParseTupleAndKeywords(args, kwds, "I", kwlist, &addr);

    unsigned int cl_id = Cache__get_cacheline_id(self, addr);
    unsigned int set_id = Cache__get_set_id(self, cl_id);

    for(int i=0; i<self->ways; i++) {
        if(self->placement[set_id*self->ways+i] == cl_id) {
            Py_RETURN_TRUE;
        }
    }
    Py_RETURN_FALSE;
}

static PyMethodDef Cache_methods[] = {
    {"load", (PyCFunction)Cache_load, METH_VARARGS|METH_KEYWORDS, NULL},
    {"iterload", (PyCFunction)Cache_iterload, METH_VARARGS|METH_KEYWORDS, NULL},
    {"store", (PyCFunction)Cache_store, METH_VARARGS|METH_KEYWORDS, NULL},
    {"iterstore", (PyCFunction)Cache_iterstore, METH_VARARGS|METH_KEYWORDS, NULL},
    {"contains", (PyCFunction)Cache_contains, METH_VARARGS, NULL},
    
    /* Sentinel */
    {NULL, NULL}
};

static PyObject* Cache_cached_get(Cache* self) {
    PyObject* cached_set = PySet_New(NULL);
    for(int i=0; i<self->sets*self->ways; i++) {
        // For each cached cacheline expand to all cached addresses:
        for(int j=0; j<self->cl_size; j++) {
            // PySys_WriteStdout("%i %i %i %i\n", self->sets, self->ways, i, self->placement[i]);
            PyObject* addr = PyLong_FromUnsignedLong(self->placement[i]*self->cl_size+j);
            PySet_Add(cached_set, addr);
            Py_DECREF(addr);
        }
    }
    return cached_set;
}

static PyGetSetDef Cache_getset[] = {
    {"cached", (getter)Cache_cached_get, NULL, "cache", NULL},
    
    /* Sentinel */
    {NULL},
};

static int Cache_init(Cache *self, PyObject *args, PyObject *kwds);

static PyTypeObject CacheType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "cachesim.backend.Cache",  /* tp_name */
    sizeof(Cache),             /* tp_basicsize */
    0,                         /* tp_itemsize */
    (destructor)Cache_dealloc, /* tp_dealloc */
    0,                         /* tp_print */
    0,                         /* tp_getattr */
    0,                         /* tp_setattr */
    0,                         /* tp_reserved */
    0,                         /* tp_repr */
    0,                         /* tp_as_number */
    0,                         /* tp_as_sequence */
    0,                         /* tp_as_mapping */
    0,                         /* tp_hash  */
    0,                         /* tp_call */
    0,                         /* tp_str */
    0,                         /* tp_getattro */
    0,                         /* tp_setattro */
    0,                         /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT,        /* tp_flags */
    "Cache objects",           /* tp_doc */
    0,                         /* tp_traverse */
    0,                         /* tp_clear */
    0,                         /* tp_richcompare */
    0,                         /* tp_weaklistoffset */
    0,                         /* tp_iter */
    0,                         /* tp_iternext */
    Cache_methods,             /* tp_methods */
    Cache_members,             /* tp_members */
    Cache_getset,              /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    (initproc)Cache_init,      /* tp_init */
    0,                         /* tp_alloc */
    0,                         /* tp_new */
};

static int Cache_init(Cache *self, PyObject *args, PyObject *kwds) {
    PyObject *parent, *tmp;
    parent = NULL;
    static char *kwlist[] = {"sets", "ways", "cl_size", "strategy", "parent", NULL};
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "IIII|O!", kwlist,
                                     &self->sets, &self->ways, &self->cl_size, &self->strategy,
                                     &CacheType, &parent)) {
        return -1;
    }
    
    // Set parent (if given)
    if(parent != NULL) {
        tmp = self->parent;
        Py_INCREF(parent);
        self->parent = parent;
        Py_XDECREF(tmp);
    } else {
        self->parent = NULL;
    }

    self->placement = PyMem_New(unsigned int, self->sets*self->ways);
    for(unsigned int i=0; i<self->sets*self->ways; i++) {
        self->placement[i] = 0;
    }

    // TODO check if ways and cl_size are of power^2
    self->way_bits = log2_uint(self->ways);
    self->cl_bits = log2_uint(self->cl_size);

    self->LOAD = 0;
    self->STORE = 0;
    self->HIT = 0;
    self->MISS = 0;
    
    //PySys_WriteStdout("CACHE sets=%i ways=%i way_bits=%i cl_size=%i cl_bits=%i\n", self->sets, self->ways, self->way_bits, self->cl_size, self->cl_bits);
    
    return 0;
}


#if PY_MAJOR_VERSION >= 3
static int cachesim_traverse(PyObject *m, visitproc visit, void *arg) {
    Py_VISIT(GETSTATE(m)->error);
    return 0;
}

static int cachesim_clear(PyObject *m) {
    Py_CLEAR(GETSTATE(m)->error);
    return 0;
}

static struct PyModuleDef moduledef = {
        PyModuleDef_HEAD_INIT,
        "cachesim.backend",
        "Backend of cachesim",
        -1,
        NULL, NULL, NULL, NULL, NULL
};

#define INITERROR return NULL

PyObject *
PyInit_backend(void)
#else
#define INITERROR return

void
initbackend(void)
#endif
{
#if PY_MAJOR_VERSION >= 3
    PyObject *module = PyModule_Create(&moduledef);
#else
    PyObject *module = Py_InitModule("cachesim.backend", cachesim_methods);
#endif

    if (module == NULL)
        INITERROR;
    
    CacheType.tp_new = PyType_GenericNew;
    if (PyType_Ready(&CacheType) < 0)
        INITERROR;

    Py_INCREF(&CacheType);
    PyModule_AddObject(module, "Cache", (PyObject *)&CacheType);

#if PY_MAJOR_VERSION >= 3
    return module;
#endif
}