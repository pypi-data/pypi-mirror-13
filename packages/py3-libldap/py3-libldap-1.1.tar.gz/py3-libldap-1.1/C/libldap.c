/*****************************************************************************
 * INCLUDED FILES & MACRO DEFINITIONS
 *****************************************************************************/

#include <libldap.h>
#include <ldap_schema.h>
#include <LDAPObject.h>
#include <LDAPModObject.h>
#include <LDAPControls.h>
#include <LDAPSchema.h>

#ifdef __LIBLDAP_DARWIN__
PyObject *LibLDAPErr;
#endif

/*****************************************************************************
 * LOCAL FUNCTION DECLARATIONS
 *****************************************************************************/

static int LibLDAP_add_constants(PyObject *);

/*****************************************************************************
 * MODULE METHODS
 *****************************************************************************/

PyDoc_STRVAR(LibLDAP_ldap_get_optionDoc, "");

static PyObject *
LibLDAP_ldap_get_option(PyObject *self, PyObject *args)
{
    PyMethodDef *ml;

    for (ml = LDAPTypeObject.tp_methods; ml->ml_name; ml++)
	if (!strcmp(ml->ml_name, "get_option"))
	    return ml->ml_meth(NULL, args);
    return PyErr_Format(
	LibLDAPErr,
	"ldap_get_option(): LDAPObject has no method `get_option()'"
	);
}

PyDoc_STRVAR(LibLDAP_ldap_set_optionDoc, "");

static PyObject *
LibLDAP_ldap_set_option(PyObject *self, PyObject *args)
{
    PyMethodDef *ml;

    for (ml = LDAPTypeObject.tp_methods; ml->ml_name; ml++)
	if (!strcmp(ml->ml_name, "set_option"))
	    return ml->ml_meth(NULL, args);
    return PyErr_Format(
	LibLDAPErr,
	"ldap_set_option(): LDAPObject has no method `set_option()'"
	);
}

PyDoc_STRVAR(LibLDAP_initializeDoc, "");

static PyObject *
LibLDAP_ldap_initialize(PyObject *self, PyObject *args, PyObject *kwds)
{
    PyObject *ldp = LDAPTypeObject.tp_new(&LDAPTypeObject, args, kwds);

    if (!ldp)
	return NULL;
    if (LDAPTypeObject.tp_init(ldp, args, kwds) == -1)
	return NULL;
    return ldp;
}

PyDoc_STRVAR(LibLDAP_is_valid_dnDoc, "");

static PyObject *
LibLDAP_ldap_is_valid_dn(PyObject *self, PyObject *args)
{
    char *dn;
    int ecode, flags = LDAP_DN_FORMAT_LDAPV3;
    LDAPDN ldn;

    if (!PyArg_ParseTuple(args, "s|i", &dn, &flags))
	return NULL;
    ecode = ldap_str2dn(dn, &ldn, flags);
    if (ecode != LDAP_SUCCESS) {
	Py_INCREF(Py_False);
	return Py_False;
    }
    ldap_dnfree(ldn);
    Py_INCREF(Py_True);
    return Py_True;
}

static PyMethodDef LibLDAPMethods[] = {
    {"ldap_get_option", (PyCFunction) LibLDAP_ldap_get_option,
     METH_VARARGS, LibLDAP_ldap_get_optionDoc
    },
    {"ldap_set_option", (PyCFunction) LibLDAP_ldap_set_option,
     METH_VARARGS, LibLDAP_ldap_set_optionDoc
    },
    {"ldap_initialize", (PyCFunction) LibLDAP_ldap_initialize,
     METH_VARARGS | METH_KEYWORDS, LibLDAP_initializeDoc
    },
    {"ldap_is_valid_dn", (PyCFunction) LibLDAP_ldap_is_valid_dn,
     METH_VARARGS | METH_KEYWORDS, LibLDAP_is_valid_dnDoc
    },
    {NULL, NULL, 0, NULL}
};

/*****************************************************************************
 * MODULE INITIALIZATION
 *****************************************************************************/

PyDoc_STRVAR(LibLDAPDoc, "OpenLDAP library wrapper");

static struct PyModuleDef LibLDAPModule = {
   PyModuleDef_HEAD_INIT,
   "_libldap",
   LibLDAPDoc,
   -1,
   LibLDAPMethods
};

PyMODINIT_FUNC
PyInit__libldap(void)
{
    PyObject *m;

    if (PyType_Ready(&LDAPModTypeObject) < 0)
        return NULL;
    if (PyType_Ready(&LDAPControlTypeObject) < 0)
        return NULL;
    if (PyType_Ready(&LDAPControlsTypeObject) < 0)
        return NULL;    
    if (PyType_Ready(&LDAPTypeObject) < 0)
        return NULL;
    m = PyModule_Create(&LibLDAPModule);
    if (!m)
	return NULL;
    if (LibLDAP_add_schema_methods(m) < 0)
	return NULL;
    Py_INCREF(&LDAPModTypeObject);
    PyModule_AddObject(m, "LDAPMod", (PyObject *) &LDAPModTypeObject);
    Py_INCREF(&LDAPControlTypeObject);
    PyModule_AddObject(m, "LDAPControl", (PyObject *) &LDAPControlTypeObject);
    Py_INCREF(&LDAPControlsTypeObject);
    PyModule_AddObject(m, "LDAPControls", (PyObject *) &LDAPControlsTypeObject);
    Py_INCREF(&LDAPTypeObject);
    PyModule_AddObject(m, "LDAP_", (PyObject *) &LDAPTypeObject);
    LibLDAPErr = PyErr_NewException("_libldap.LDAPError", NULL, NULL);
    Py_INCREF(LibLDAPErr);
    PyModule_AddObject(m, "LDAPError", LibLDAPErr);
    if (LibLDAP_add_constants(m) < 0)
	return NULL;
    return m;
}

/*****************************************************************************
 * GLOBAL FUNCTION DEFINITIONS
 *****************************************************************************/

void
LibLDAP_value_free(void **vals)
{
    void **ptr;

    for (ptr = vals; ptr && *ptr; ptr++)
	PyMem_Free(*ptr);
    PyMem_Free((void *) vals);
}

/*****************************************************************************
 * LOCAL FUNCTION DEFINITIONS
 *****************************************************************************/

static int
LibLDAP_add_constants(PyObject *m)
{
    if (PyModule_AddIntMacro(m, LDAP_VERSION2) < 0)
	return -1;
    if (PyModule_AddIntMacro(m, LDAP_VERSION3) < 0)
	return -1;
    if (PyModule_AddIntMacro(m, LDAP_SCOPE_BASE) < 0)
	return -1;
    if (PyModule_AddIntMacro(m, LDAP_SCOPE_ONELEVEL) < 0)
	return -1;
    if (PyModule_AddIntMacro(m, LDAP_SCOPE_SUBTREE) < 0)
	return -1;
    if (PyModule_AddIntMacro(m, LDAP_SCOPE_CHILDREN) < 0)
	return -1;
    if (PyModule_AddIntMacro(m, LDAP_NO_LIMIT) < 0)
	return -1;
    if (PyModule_AddIntMacro(m, LDAP_OPT_X_TLS_REQUIRE_CERT) < 0)
	return -1;
    if (PyModule_AddIntMacro(m, LDAP_OPT_X_TLS_NEVER) < 0)
	return -1;
    if (PyModule_AddIntMacro(m, LDAP_OPT_X_TLS_HARD) < 0)
	return -1;
    if (PyModule_AddIntMacro(m, LDAP_OPT_X_TLS_DEMAND) < 0)
	return -1;
    if (PyModule_AddIntMacro(m, LDAP_OPT_X_TLS_ALLOW) < 0)
	return -1;
    if (PyModule_AddIntMacro(m, LDAP_OPT_X_TLS_TRY) < 0)
	return -1;
    if (PyModule_AddIntMacro(m, LDAP_OPT_PROTOCOL_VERSION) < 0)
	return -1;
    if (PyModule_AddIntMacro(m, LDAP_MOD_ADD) < 0)
	return -1;
    if (PyModule_AddIntMacro(m, LDAP_MOD_DELETE) < 0)
	return -1;
    if (PyModule_AddIntMacro(m, LDAP_MOD_REPLACE) < 0)
	return -1;
    if (PyModule_AddIntMacro(m, LDAP_AUTH_SIMPLE) < 0)
	return -1;
    if (PyModule_AddStringConstant(
	    m, "LDAP_SCHEMA_BASE", LibLDAPSchemaBase) < 0)
	return -1;
    if (PyModule_AddIntMacro(m, LDAP_SCHEMA_ALLOW_NONE) < 0)
	return -1;
    if (PyModule_AddIntMacro(m, LDAP_SCHEMA_ALLOW_NO_OID) < 0)
	return -1;
    if (PyModule_AddIntMacro(m, LDAP_SCHEMA_ALLOW_QUOTED) < 0)
	return -1;
    if (PyModule_AddIntMacro(m, LDAP_SCHEMA_ALLOW_DESCR) < 0)
	return -1;
    if (PyModule_AddIntMacro(m, LDAP_SCHEMA_ALLOW_DESCR_PREFIX) < 0)
	return -1;
    if (PyModule_AddIntMacro(m, LDAP_SCHEMA_ALLOW_ALL) < 0)
	return -1;
    if (PyModule_AddIntMacro(m, LDAP_SCHEMA_USER_APPLICATIONS) < 0)
	return -1;
    if (PyModule_AddIntMacro(m, LDAP_SCHEMA_DIRECTORY_OPERATION) < 0)
	return -1;
    if (PyModule_AddIntMacro(m, LDAP_SCHEMA_DISTRIBUTED_OPERATION) < 0)
	return -1;
    if (PyModule_AddIntMacro(m, LDAP_SCHEMA_DSA_OPERATION) < 0)
	return -1;
    if (PyModule_AddIntMacro(m, LDAP_SCHEMA_ABSTRACT) < 0)
	return -1;
    if (PyModule_AddIntMacro(m, LDAP_SCHEMA_STRUCTURAL) < 0)
	return -1;
    if (PyModule_AddIntMacro(m, LDAP_SCHEMA_AUXILIARY) < 0)
	return -1;
    if (PyModule_AddIntMacro(m, LDAP_DN_FORMAT_LDAPV3) < 0)
	return -1;
    if (PyModule_AddIntMacro(m, LDAP_DN_FORMAT_LDAPV2) < 0)
	return -1;
    if (PyModule_AddIntMacro(m, LDAP_DN_FORMAT_DCE) < 0)
	return -1;
    if (PyModule_AddIntMacro(m, LDAP_DN_PEDANTIC) < 0)
	return -1;    
    return 0;
}
