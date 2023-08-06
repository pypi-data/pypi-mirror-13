#include "Python.h"
#include "double_array.hpp"
using namespace std;

typedef struct {
    PyObject_HEAD
    DoubleArray *da;
} python_da_TrieObject;

static int python_da_Trie_init(python_da_TrieObject *self, PyObject *args, PyObject *kwds){
    try{
        void* p = PyMem_Malloc(sizeof(DoubleArray));
        new (p) DoubleArray();
        self->da = (DoubleArray *)p;
    }catch(bad_alloc e){
        PyErr_NoMemory();
        return -1;
    }
    return 0; 
}

static void python_da_Trie_dealloc(python_da_TrieObject *self){
    self->da->~DoubleArray();
    PyMem_Free(self->da);
    Py_TYPE(self)->tp_free((PyObject*)self);
}

static PyObject* cnv_result(bool is_true){
    if(is_true){
        Py_RETURN_TRUE;
    }else{
        Py_RETURN_FALSE;
    }  
}

static PyObject* python_da_Trie_insert(python_da_TrieObject *self, PyObject *args){
    try{
        char *word = NULL;
        int id = -1;
        if(!PyArg_ParseTuple(args, "s|i", &word, &id)){
            return NULL;
        }
        return cnv_result(self->da->insert(word, id));
    }catch(bad_alloc){
        return PyErr_NoMemory();
    }
}


static PyObject* python_da_Trie_erase(python_da_TrieObject *self, PyObject *args){
    try{
        char *word = NULL;
        if(!PyArg_ParseTuple(args, "s", &word)){
            return NULL;
        }
        return cnv_result(self->da->erase(word));
    }catch(bad_alloc){
        return PyErr_NoMemory();
    }
}


static PyObject* vector_to_array(vector<string> vec){
    PyObject* res = PyList_New(vec.size());
    if(res == NULL){
        PyErr_SetString(PyExc_RuntimeError, "failed build list");
        return NULL;
    }
    for(size_t i = 0; i < vec.size(); i++){
        PyObject* elem = Py_BuildValue("s", vec[i].c_str());
        if(elem == NULL){
           Py_DECREF(res);
           return NULL;
        }
        PyList_SET_ITEM(res, i, elem);
    }
    return res;
}

static PyObject* python_da_Trie_enumerate(python_da_TrieObject *self, PyObject *args){
    try{
        char *str = NULL;
        if(!PyArg_ParseTuple(args, "s", &str)){
            return NULL;
        }
        vector<pair<string, int> > result;
        self->da->enumerate(str, result);
        PyObject* res = PyList_New(result.size());
        if(res == NULL){
            PyErr_SetString(PyExc_RuntimeError, "failed build list");
            return NULL;
        }
        for(size_t i = 0; i < result.size(); i++){
            PyObject* elem = Py_BuildValue("si", result[i].first.c_str(), result[i].second);
            if(elem == NULL){
                Py_DECREF(res);
                return NULL;
            }
            PyList_SET_ITEM(res, i, elem);
        }
        return res; 
    }catch(bad_alloc){
        return PyErr_NoMemory();
    }
}

static PyObject* python_da_Trie_exact_match(python_da_TrieObject *self, PyObject *args){
    try{
        char *word = NULL;
        if(!PyArg_ParseTuple(args, "s", &word)){
            return NULL;
        }
        int id = self->da->exact_match(word);
        PyObject* result = Py_BuildValue("i", id);
        if(result == NULL) return NULL;
        return result;
    }catch(bad_alloc){
        return PyErr_NoMemory();
    }
}

static PyObject* python_da_Trie_common_prefix_search(python_da_TrieObject *self, PyObject *args){
    try{
        char *word = NULL;
        if(!PyArg_ParseTuple(args, "s", &word)){
            return NULL;
        }
        vector<string> result;
        self->da->common_prefix_search(word, result);
        return vector_to_array(result);
    }catch(bad_alloc){
        return PyErr_NoMemory();
    }
}

static PyObject* python_da_Trie_contains(python_da_TrieObject *self, PyObject *args){
    try{
        char *word = NULL;
        if(!PyArg_ParseTuple(args, "s", &word)){
            return NULL;
        }
        return cnv_result(self->da->contains(word));
    }catch(bad_alloc){
        return PyErr_NoMemory();
    }
}

static PyObject* python_da_Trie_extract_all_matched(python_da_TrieObject *self, PyObject *args){
    try{
        char *str = NULL;
        if(!PyArg_ParseTuple(args, "s", &str)){
            return NULL;
        }
        vector<string> result;
        self->da->extract_all_matched(str, result);
        return vector_to_array(result);
    }catch(bad_alloc){
        return PyErr_NoMemory();
    }
}

static PyObject* python_da_Trie_save(python_da_TrieObject *self, PyObject *args){
    try{
        char *str = NULL;
        if(!PyArg_ParseTuple(args, "s", &str)){
            return NULL;
        }
        return cnv_result(self->da->save(str));
    }catch(bad_alloc){
        return PyErr_NoMemory();
    }
}


static PyObject* python_da_Trie_load(python_da_TrieObject *self, PyObject *args){
    try{
        char *str = NULL;
        if(!PyArg_ParseTuple(args, "s", &str)){
            return NULL; 
        }
        return cnv_result(self->da->load(str));
    }catch(bad_alloc){
        return PyErr_NoMemory();
    }   
}       



static PyObject* python_da_Trie_build(python_da_TrieObject *self, PyObject *args){
    try{
        PyObject* list = NULL;
        if(!PyArg_ParseTuple(args, "O", &list)){
            return NULL;
        }
        if(!PyList_Check(list)){
            PyErr_BadArgument();
            return NULL;
        }
        size_t size = PyList_Size(list); 
        vector<string> words;
        for(int i = 0; i < static_cast<int>(size); i++){
            PyObject* elem = PyList_GetItem(list, i);
            if(!PyString_Check(elem)){
                PyErr_BadArgument();
                return NULL;
            }
            words.push_back(PyString_AsString(elem));
        }
        return cnv_result(self->da->build(words));
    }catch(bad_alloc){
        return PyErr_NoMemory();
    }
}


static PyMethodDef python_da_Trie_methods[] = {
    {"exact_match", (PyCFunction)python_da_Trie_exact_match, METH_VARARGS, "exact match search" },
    {"enumerate", (PyCFunction)python_da_Trie_enumerate, METH_VARARGS, "enumerate all words" },
    {"common_prefix_search", (PyCFunction)python_da_Trie_common_prefix_search, METH_VARARGS, "common prefix search" },
    {"contains", (PyCFunction)python_da_Trie_contains, METH_VARARGS, "contains word" },
    {"extract_all_matched", (PyCFunction)python_da_Trie_extract_all_matched, METH_VARARGS, "extract all matched words" },
    {"insert", (PyCFunction)python_da_Trie_insert, METH_VARARGS, "insert new word" },
    {"build", (PyCFunction)python_da_Trie_build, METH_VARARGS, "build with many words" },
    {"erase", (PyCFunction)python_da_Trie_erase, METH_VARARGS, "erase word" },
    {"save", (PyCFunction)python_da_Trie_save, METH_VARARGS, "save file" },
    {"load", (PyCFunction)python_da_Trie_load, METH_VARARGS, "load file" },
    {NULL}  /* Sentinel */
};

static PyTypeObject python_da_TrieType = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "python_da.Trie",             /*tp_name*/
    sizeof(python_da_TrieObject), /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    (destructor)python_da_Trie_dealloc,    /*tp_dealloc*/
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,                         /*tp_compare*/
    0,                         /*tp_repr*/
    0,                         /*tp_as_number*/
    0,                         /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    0,                         /*tp_hash */
    0,                         /*tp_call*/
    0,                         /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT,        /*tp_flags*/
    "Python Double Array objects",           /* tp_doc */
    0,                         /* tp_traverse */
    0,                         /* tp_clear */
    0,                         /* tp_richcompare */
    0,                         /* tp_weaklistoffset */
    0,                         /* tp_iter */
    0,                         /* tp_iternext */
    python_da_Trie_methods,               /* tp_methods */
    0,                         /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    (initproc)python_da_Trie_init,      /* tp_init */
    0,                         /* tp_alloc */
    0,                 /* tp_new */
};


static PyMethodDef python_da_methods[] = {
    {NULL}  /* Sentinel */
};

#ifndef PyMODINIT_FUNC	/* declarations for DLL import/export */
#define PyMODINIT_FUNC void
#endif
PyMODINIT_FUNC
initpython_da(void) 
{
    PyObject* module;

    python_da_TrieType.tp_new = PyType_GenericNew;
    if (PyType_Ready(&python_da_TrieType) < 0)
        return;

    module = Py_InitModule3("python_da", python_da_methods, "Python Double Array Module.");

    Py_INCREF(&python_da_TrieType);
    PyModule_AddObject(module, "Trie", (PyObject *)&python_da_TrieType);
}
