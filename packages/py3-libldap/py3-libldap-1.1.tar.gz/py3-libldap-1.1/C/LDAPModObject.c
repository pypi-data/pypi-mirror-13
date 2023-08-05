/*****************************************************************************
 * INCLUDED FILES & MACRO DEFINITIONS
 *****************************************************************************/

#include <libldap.h>
#include <locale.h>
#include <wchar.h>
#include <LDAPModObject.h>

#ifdef __LIBLDAP_DARWIN__
extern PyObject *LibLDAPErr;
#endif

/*****************************************************************************
 * libldap.LDAPMod OBJECT
 *****************************************************************************/

/* DOC */

PyDoc_STRVAR(LDAPModObjectDoc, "");

/* METHODS */

/* MEMBERS */

/* GET/SET */

static PyObject *
LDAPModObject_getmode(LDAPModObject *self, void *closure)
{
    return PyLong_FromLong((long) self->mod->mod_op);
}

static PyObject *
LDAPModObject_getattr(LDAPModObject *self, void *closure)
{
    return PyUnicode_FromString(self->mod->mod_type);
}

static PyObject *
LDAPModObject_getvalues(LDAPModObject *self, void *closure)
{
    char **ptr;
    PyObject *ret;
    
    if (!self->mod->mod_values)
	Py_RETURN_NONE;
    ret = PyList_New(0);
    if (!ret)
	return NULL;
    for (ptr = self->mod->mod_values; *ptr; ptr++) {
	PyObject *val = PyUnicode_FromString(*ptr);

	if (!val)
	    return NULL;
	if (PyList_Append(ret, val) == -1)
	    return NULL;
    }
    return ret;
}

static PyGetSetDef LDAPModObjectGetSet[] = {
    {"mode", (getter) LDAPModObject_getmode, NULL,
     "LDAP mode (LDAP_MOD_[ADD|DELETE|REPLACE])",  NULL},
    {"attr", (getter) LDAPModObject_getattr, NULL,
     "attribute name",  NULL},
    {"values", (getter) LDAPModObject_getvalues, NULL,
     "list of attribute values",  NULL},
    {NULL, NULL, NULL, NULL, NULL}
};

/* SPECIAL METHODS */

static void
LDAPModObject_dealloc(LDAPModObject *self)
{
    PyMem_Free((void *) self->mod->mod_type);
    LibLDAP_value_free((void **) self->mod->mod_values);
    PyMem_Free((void *) self->mod);
    Py_TYPE(self)->tp_free((PyObject *) self);
}

static int
LDAPModObject_init(LDAPModObject *self, PyObject *args, PyObject *kwds)
{
    int mod_op;
    char *mod_type;
    PyObject *values = Py_None;
    static char *kwlist[] = {"mode", "attr", "values", NULL};

    if (!PyArg_ParseTupleAndKeywords(
	    args, kwds, "is|O", kwlist, &mod_op, &mod_type, &values))
	return -1;
    switch (mod_op) {
    case LDAP_MOD_ADD:
    case LDAP_MOD_DELETE:
    case LDAP_MOD_REPLACE:
	self->mod->mod_op = mod_op;
	break;
    default:
	(void) PyErr_Format(
	    PyExc_ValueError, "%s.__init__(): argument `mode' must be "
	    "LDAP_MOD_[ADD|DELETE|REPLACE]", LDAPObjName(self)
	    );
	return -1;
    }
    if (!PyList_Check(values) && values != Py_None) {
	(void) PyErr_Format(
	    PyExc_TypeError, "%s.__init__(): argument `values' must be "
	    "a list or None", LDAPObjName(self)
	    );
	return -1;
    }
    self->mod->mod_type = PyMem_New(char, strlen(mod_type) + 1);
    if (!self->mod->mod_type) {
	PyErr_SetNone(PyExc_MemoryError);
	return -1;
    }
    (void) strcpy(self->mod->mod_type, mod_type);
    if (PyList_Check(values)) {
	char **ptr;
        wchar_t *tmp;
	Py_ssize_t i, len = PyList_GET_SIZE(values);

	if (!len) {
	    (void) PyErr_Format(
		PyExc_TypeError, "%s.__init__(): argument `values' must be "
		"a non empty list", LDAPObjName(self)
		);
	    return -1;
	}
	self->mod->mod_values = PyMem_New(char *, len + 1);
	if (!self->mod->mod_values) {
	    PyErr_SetNone(PyExc_MemoryError);
	    return -1;
	}
	self->mod->mod_values[len] = NULL;
        setlocale(LC_ALL, "");
	for (i = 0, ptr=self->mod->mod_values; i < len; i++, ptr++) {
	    PyObject *py_value = PyList_GET_ITEM(values, i);
	    Py_ssize_t l;
	    
	    if (!PyUnicode_Check(py_value)) {
		PyMem_Free((void *) self->mod->mod_values);
		self->mod->mod_values = NULL;
		PyErr_Format(
		    PyExc_TypeError,
		    "%s.__init__(): argument `values' must be a list of "
		    "strings", LDAPObjName(self)
		    );
		return -1;
	    }
            tmp=PyUnicode_AsWideCharString(py_value,&l);
	    *ptr = PyMem_New(char, 2*l);
	    if (!*ptr || !tmp) {
		LibLDAP_value_free((void **) self->mod->mod_values);
		PyErr_SetNone(PyExc_MemoryError);
		return -1;
	    }

            wcstombs(*ptr,tmp,2*l);
            PyMem_Free((void*)tmp);
	}
    }
    return 0;
}

static PyObject *
LDAPModObject_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    LDAPModObject *self;

    self = (LDAPModObject *) type->tp_alloc(type, 0);
    if (self) {
	self->mod = PyMem_New(LDAPMod, 1);
	if (!self->mod)
	    return PyErr_NoMemory();
	(void) memset((void *) self->mod, 0, sizeof(LDAPMod));
    }
    return (PyObject *) self;
}

/* TYPE */

PyTypeObject LDAPModTypeObject = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "_libldap.LDAPMod",				/* tp_name */
    sizeof(LDAPModObject),			/* tp_basicsize */
    0,						/* tp_itemsize */
    (destructor) LDAPModObject_dealloc,		/* tp_dealloc */
    0,						/* tp_print */
    0,						/* tp_getattr */
    0,						/* tp_setattr */
    0,						/* tp_compare */
    0,						/* tp_repr */
    0,						/* tp_as_number */
    0,						/* tp_as_sequence */
    0,						/* tp_as_mapping */
    0,						/* tp_hash  */
    0,						/* tp_call */
    0,						/* tp_str */
    0,						/* tp_getattro */
    0,						/* tp_setattro */
    0,						/* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,	/* tp_flags */
    LDAPModObjectDoc,				/* tp_doc */
    0,						/* tp_traverse */
    0,						/* tp_clear */
    0,						/* tp_richcompare */
    0,						/* tp_weaklistoffset */
    0,						/* tp_iter */
    0,						/* tp_iternext */
    0,						/* tp_methods */
    0,						/* tp_members */
    LDAPModObjectGetSet,			/* tp_getset */
    0,						/* tp_base */
    0,						/* tp_dict */
    0,						/* tp_descr_get */
    0,						/* tp_descr_set */
    0,						/* tp_dictoffset */
    (initproc) LDAPModObject_init,		/* tp_init */
    0,						/* tp_alloc */
    (newfunc) LDAPModObject_new,		/* tp_new */
};
