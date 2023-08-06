#include <Python.h>

#include "diff-match-patch-cpp-stl/diff_match_patch.h"

#if PY_MAJOR_VERSION == 3
    // Upgrade these types.
    #define PyString_FromString PyUnicode_FromString
    #define PyString_FromStringAndSize PyUnicode_FromStringAndSize
    #define PyInt_FromLong PyLong_FromLong
#endif

template <class STORAGE_TYPE, char FMTSPEC, class CPPTYPE, class PYTYPE>
static PyObject *
diff_match_patch_diff(PyObject *self, PyObject *args, PyObject *kwargs)
{
    STORAGE_TYPE *a, *b;
    float timelimit = 0.0;
    int checklines = 1;
    int cleanupSemantic = 1;
    int counts_only = 1;
    int as_patch = 0;
    char format_spec[64];

    static char *kwlist[] = {
        strdup("left_document"),
        strdup("right_document"),
        strdup("timelimit"),
        strdup("checklines"),
        strdup("cleanup_semantic"),
        strdup("counts_only"),
        strdup("as_patch"),
        NULL };

    sprintf(format_spec, "%c%c|fbbbb", FMTSPEC, FMTSPEC);
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, format_spec, kwlist,
                                     &a, &b,
                                     &timelimit, &checklines, &cleanupSemantic,
                                     &counts_only, &as_patch))
        return NULL;

    PyObject *ret = PyList_New(0);

    typedef diff_match_patch<CPPTYPE> DMP;
    DMP dmp;

    PyObject *opcodes[3];
    opcodes[dmp.DELETE] = PyString_FromString("-");
    opcodes[dmp.INSERT] = PyString_FromString("+");
    opcodes[dmp.EQUAL] = PyString_FromString("=");

    dmp.Diff_Timeout = timelimit;
    typename DMP::Diffs diff = dmp.diff_main(a, b, checklines);

    if (cleanupSemantic)
        dmp.diff_cleanupSemantic(diff);

    if (as_patch) {
        typename DMP::Patches patch = dmp.patch_make(a, diff);
        CPPTYPE patch_str = dmp.patch_toText(patch);

        if (FMTSPEC == 'u')
            return PyUnicode_FromUnicode((Py_UNICODE*)patch_str.data(), patch_str.size());
        else
            return PyString_FromStringAndSize((const char*)patch_str.data(), patch_str.size());
    }

    typename std::list<typename DMP::Diff>::const_iterator entryiter;
    for (entryiter = diff.begin(); entryiter != diff.end(); entryiter++) {
        typename DMP::Diff entry = *entryiter;

        PyObject* tuple = PyTuple_New(2);

        Py_INCREF(opcodes[entry.operation]); // we're going to reuse the object, so don't let SetItem steal the reference
        PyTuple_SetItem(tuple, 0, opcodes[entry.operation]);

        if (counts_only)
            PyTuple_SetItem(tuple, 1, PyInt_FromLong(entry.text.length()));
        else if (FMTSPEC == 'u')
            PyTuple_SetItem(tuple, 1, PyUnicode_FromUnicode((Py_UNICODE*)entry.text.data(), entry.text.size()));
        else
            PyTuple_SetItem(tuple, 1, PyString_FromStringAndSize((const char*)entry.text.data(), entry.text.size()));

        PyList_Append(ret, tuple);
        Py_DECREF(tuple); // the list owns a reference now
    }

    // We're left with one extra reference.
    Py_DECREF(opcodes[dmp.DELETE]);
    Py_DECREF(opcodes[dmp.INSERT]);
    Py_DECREF(opcodes[dmp.EQUAL]);

    return ret;
}

#if PY_MAJOR_VERSION == 2
static PyObject *
diff_match_patch_diff_str(PyObject *self, PyObject *args, PyObject *kwargs)
{
    return diff_match_patch_diff<const char, 's', std::string, char*>(self, args, kwargs);
}

// return the length of a null terminated character sequence
template <class char_t> static int len(const char_t* p)
{
  for (int i = 0; ; i++) {
    if (p[i] == 0) {
      return i;
    }
  }
}

// convert Py_UNICODE* to std::wstring object
std::wstring to_wstring(Py_UNICODE* p)
{
    int n = len(p);
    wchar_t buf[n + 1];
    PyUnicodeObject* obj = reinterpret_cast<PyUnicodeObject*>(PyUnicode_FromUnicode(p, n));
    PyUnicode_AsWideChar(obj, buf, n + 1);
    Py_DECREF(obj);
    return std::wstring(buf);
}

std::string wtos(const std::wstring& wstr)
{
  return std::string(wstr.begin(), wstr.end());
}

static PyObject *
diff_match_patch_diff_unicode_python2(PyObject *self, PyObject *args, PyObject *kwargs)
{
    Py_UNICODE *a, *b;
    float timelimit = 0.0;
    int checklines = 1;
    int cleanupSemantic = 1;
    int counts_only = 1;
    int as_patch = 0;

    static char *kwlist[] = {
        strdup("left_document"),
        strdup("right_document"),
        strdup("timelimit"),
        strdup("checklines"),
        strdup("cleanup_semantic"),
        strdup("counts_only"),
        strdup("as_patch"),
        NULL };

    const char* format_spec = "uu|fbbbb";
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, format_spec, kwlist,
                                     &a, &b,
                                     &timelimit, &checklines, &cleanupSemantic,
                                     &counts_only, &as_patch))
        return NULL;

    PyObject *ret = PyList_New(0);

    typedef diff_match_patch<std::wstring> DMP;
    DMP dmp;

    PyObject *opcodes[3];
    opcodes[dmp.DELETE] = PyString_FromString("-");
    opcodes[dmp.INSERT] = PyString_FromString("+");
    opcodes[dmp.EQUAL] = PyString_FromString("=");

    dmp.Diff_Timeout = timelimit;

    std::wstring a_str = to_wstring(a);
    std::wstring b_str = to_wstring(b);

    DMP::Diffs diff;
    try {
        diff = dmp.diff_main(a_str, b_str, checklines);
    } catch (std::exception& e) {
        PyErr_SetString(PyExc_RuntimeError, e.what());
        return NULL;
    } catch (std::wstring& s) {
        PyErr_SetString(PyExc_RuntimeError, wtos(s).c_str());
        return NULL;
    }

    if (cleanupSemantic)
        dmp.diff_cleanupSemantic(diff);

    if (as_patch) {
        DMP::Patches patch = dmp.patch_make(a_str, diff);
        std::wstring patch_str = dmp.patch_toText(patch);

        return PyUnicode_FromUnicode((Py_UNICODE*)patch_str.data(), patch_str.size());
    }

    std::list<DMP::Diff>::const_iterator entryiter;
    for (entryiter = diff.begin(); entryiter != diff.end(); entryiter++) {
        DMP::Diff entry = *entryiter;
        PyObject* tuple = PyTuple_New(2);

        Py_INCREF(opcodes[entry.operation]); // we're going to reuse the object, so don't let SetItem steal the reference
        PyTuple_SetItem(tuple, 0, opcodes[entry.operation]);

        if (counts_only) {
            PyTuple_SetItem(tuple, 1, PyInt_FromLong(entry.text.length()));
        }
        else {
            PyObject* obj = PyUnicode_FromWideChar(entry.text.data(), entry.text.size());
            PyTuple_SetItem(tuple, 1, obj);
        }

        PyList_Append(ret, tuple);
        Py_DECREF(tuple); // the list owns a reference now
    }


    // We're left with one extra reference.
    Py_DECREF(opcodes[dmp.DELETE]);
    Py_DECREF(opcodes[dmp.INSERT]);
    Py_DECREF(opcodes[dmp.EQUAL]);

    return ret;
}

static PyObject *
match_main_unicode(PyObject *self, PyObject *args, PyObject *kwargs)
{
    Py_UNICODE *pattern, *text;
    int loc;
    int match_distance = 1000;
    int match_maxbits = 32;
    float match_threshold = 0.5;

    static char *kwlist[] = {
        strdup("pattern"),
        strdup("text"),
        strdup("loc"),
        strdup("match_distance"),
        strdup("match_maxbits"),
        strdup("match_threshold"),
        NULL };

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "uui|iif", kwlist,
                                     &pattern, &text, &loc,
                                     &match_distance, &match_maxbits, &match_threshold)) {
        return NULL;
    }

    std::wstring pattern_str = to_wstring(pattern);
    std::wstring text_str = to_wstring(text);

    typedef diff_match_patch<std::wstring> DMP;
    DMP dmp;

    dmp.Match_Distance = match_distance;
    dmp.Match_MaxBits = match_maxbits;
    dmp.Match_Threshold = match_threshold;

    try {
        int index = dmp.match_main(pattern_str, text_str, loc);
        return Py_BuildValue("i", index);
    } catch (std::exception& e) {
        PyErr_SetString(PyExc_RuntimeError, e.what());
        return NULL;
    } catch (std::wstring& s) {
        PyErr_SetString(PyExc_RuntimeError, wtos(s).c_str());
        return NULL;
    }
}

static PyMethodDef MyMethods[] = {
    {"diff_unicode", (PyCFunction)diff_match_patch_diff_unicode_python2, METH_VARARGS|METH_KEYWORDS,
    "Compute the difference between two Unicode strings. Returns a list of tuples (OP, LEN)."},
    {"diff_str", (PyCFunction)diff_match_patch_diff_str, METH_VARARGS|METH_KEYWORDS,
    "Compute the difference between two (regular) strings. Returns a list of tuples (OP, LEN)."},
    {"match_main_unicode", (PyCFunction)match_main_unicode, METH_VARARGS|METH_KEYWORDS,
    "Locate the best instance of 'pattern' in 'text' near 'loc'. Returns -1 if no match found."},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

PyMODINIT_FUNC
initdiff_match_patch(void)
{
    (void) Py_InitModule("diff_match_patch", MyMethods);
}
#endif

#if PY_MAJOR_VERSION == 3
static PyObject *
diff_match_patch_diff_bytes(PyObject *self, PyObject *args, PyObject *kwargs)
{
    return diff_match_patch_diff<const char, 'y', std::string, char*>(self, args, kwargs);
}

static PyMethodDef MyMethods[] = {
    {"diff", (PyCFunction)diff_match_patch_diff_unicode, METH_VARARGS|METH_KEYWORDS,
    "Compute the difference between two strings. Returns a list of tuples (OP, LEN)."},
    {"diff_bytes", (PyCFunction)diff_match_patch_diff_bytes, METH_VARARGS|METH_KEYWORDS,
    "Compute the difference between two byte strings. Returns a list of tuples (OP, LEN)."},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

static struct PyModuleDef mymodule = {
   PyModuleDef_HEAD_INIT,
   "diff_match_patch",   /* name of module */
   NULL, /* module documentation, may be NULL */
   -1,       /* size of per-interpreter state of the module,
                or -1 if the module keeps state in global variables. */
   MyMethods
};

PyMODINIT_FUNC
PyInit_diff_match_patch(void)
{
    return PyModule_Create(&mymodule);
}
#endif
