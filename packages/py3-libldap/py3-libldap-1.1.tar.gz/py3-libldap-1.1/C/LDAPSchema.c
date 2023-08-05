/*****************************************************************************
 * INCLUDED FILES & MACRO DEFINITIONS
 *****************************************************************************/

#include <libldap.h>
#include <ldap_schema.h>
#include <LDAPSchema.h>

#ifdef __LIBLDAP_DARWIN__
extern PyObject *LibLDAPErr;
#endif

/*****************************************************************************
 * LOCAL FUNCTION DECLARATIONS
 *****************************************************************************/

static PyObject *LibLDAP_C2Py_strs(char **);
static PyObject *LibLDAP_C2Py_lseis(LDAPSchemaExtensionItem **);
static int LibLDAP_check_flags(int, const char *);

/*****************************************************************************
 * MODULE METHODS (SCHEMA)
 *****************************************************************************/

PyDoc_STRVAR(LibLDAP_ldap_str2syntaxDoc, "");

static PyObject *
LibLDAP_ldap_str2syntax(PyObject *self, PyObject *args)
{
    const char *str, *errp;
    int code, flags = LDAP_SCHEMA_ALLOW_NONE;
    LDAPSyntax *syn;
    PyObject *ret, *val;

    if (!PyArg_ParseTuple(args, "s|i", &str, &flags))
	return NULL;
    if (LibLDAP_check_flags(flags, "ldap_str2syntax") < 0)
	return NULL;
    syn = ldap_str2syntax(str, &code, &errp, flags);
    if (!syn)
	return PyErr_Format(
	    LibLDAPErr, "ldap_str2syntax(): `%s': %s", errp,
	    ldap_scherr2str(code));
    ret = PyDict_New();
    if (!ret) {
	ldap_syntax_free(syn);
	return NULL;
    }
    if (syn->syn_oid)
	val = PyUnicode_FromString(syn->syn_oid);
    else {
	Py_INCREF(Py_None);
	val = Py_None;
    }
    if (PyDict_SetItemString(ret, "oid", val) == -1)
	goto failed;
    Py_DECREF(val);
    val = LibLDAP_C2Py_strs(syn->syn_names);
    if (!val)
	goto failed;
    if (PyDict_SetItemString(ret, "names", val) == -1)
	goto failed;
    Py_DECREF(val);
    if (syn->syn_desc)
	val = PyUnicode_FromString(syn->syn_desc);
    else {
	Py_INCREF(Py_None);
	val = Py_None;
    }    
    if (PyDict_SetItemString(ret, "desc", val) == -1)
	goto failed;
    Py_DECREF(val);
    val = LibLDAP_C2Py_lseis(syn->syn_extensions);
    if (!val)
	goto failed;
    if (PyDict_SetItemString(ret, "extensions", val) == -1)
	goto failed;
    Py_DECREF(val);
    ldap_syntax_free(syn);
    return ret;
  failed:
    ldap_syntax_free(syn);
    Py_XDECREF(val);
    Py_DECREF(ret);
    return NULL;
}

PyDoc_STRVAR(LibLDAP_ldap_str2matchingruleDoc, "");

static PyObject *
LibLDAP_ldap_str2matchingrule(PyObject *self, PyObject *args)
{
    const char *str, *errp;
    int code, flags = LDAP_SCHEMA_ALLOW_NONE;
    LDAPMatchingRule *mr;
    PyObject *ret, *val;

    if (!PyArg_ParseTuple(args, "s|i", &str, &flags))
	return NULL;
    if (LibLDAP_check_flags(flags, "ldap_str2matchingrule") < 0)
	return NULL;
    mr = ldap_str2matchingrule(str, &code, &errp, flags);
    if (!mr)
	return PyErr_Format(
	    LibLDAPErr, "ldap_str2matchingrule(): `%s': %s", errp,
	    ldap_scherr2str(code));
    ret = PyDict_New();
    if (!ret) {
	ldap_matchingrule_free(mr);
	return NULL;
    }
    if (mr->mr_oid)
	val = PyUnicode_FromString(mr->mr_oid);
    else {
	Py_INCREF(Py_None);
	val = Py_None;
    }
    if (PyDict_SetItemString(ret, "oid", val) == -1)
	goto failed;
    Py_DECREF(val);
    val = LibLDAP_C2Py_strs(mr->mr_names);
    if (!val)
	goto failed;
    if (PyDict_SetItemString(ret, "names", val) == -1)
	goto failed;
    Py_DECREF(val);
    if (mr->mr_desc)
	val = PyUnicode_FromString(mr->mr_desc);
    else {
	Py_INCREF(Py_None);
	val = Py_None;
    }    
    if (PyDict_SetItemString(ret, "desc", val) == -1)
	goto failed;
    Py_DECREF(val);
    val = PyBool_FromLong((long) mr->mr_obsolete);
    if (PyDict_SetItemString(ret, "obsolete", val) == -1)
	goto failed;
    Py_DECREF(val);
    if (mr->mr_syntax_oid)
	val = PyUnicode_FromString(mr->mr_syntax_oid);
    else {
	Py_INCREF(Py_None);
	val = Py_None;
    }
    if (PyDict_SetItemString(ret, "syntax_oid", val) == -1)
	goto failed;
    Py_DECREF(val);
    val = LibLDAP_C2Py_lseis(mr->mr_extensions);
    if (!val)
	goto failed;
    if (PyDict_SetItemString(ret, "extensions", val) == -1)
	goto failed;
    Py_DECREF(val);
    ldap_matchingrule_free(mr);
    return ret;
  failed:
    ldap_matchingrule_free(mr);
    Py_XDECREF(val);
    Py_DECREF(ret);
    return NULL;
}

PyDoc_STRVAR(LibLDAP_ldap_str2matchingruleuseDoc, "");

static PyObject *
LibLDAP_ldap_str2matchingruleuse(PyObject *self, PyObject *args)
{
    const char *str, *errp;
    int code, flags = LDAP_SCHEMA_ALLOW_NONE;
    LDAPMatchingRuleUse *mru;
    PyObject *ret, *val;

    if (!PyArg_ParseTuple(args, "s|i", &str, &flags))
	return NULL;
    if (LibLDAP_check_flags(flags, "ldap_str2matchingruleuse") < 0)
	return NULL;
    mru = ldap_str2matchingruleuse(str, &code, &errp, flags);
    if (!mru)
	return PyErr_Format(
	    LibLDAPErr, "ldap_str2matchingruleuse(): `%s': %s", errp,
	    ldap_scherr2str(code));
    ret = PyDict_New();
    if (!ret) {
	ldap_matchingruleuse_free(mru);
	return NULL;
    }
    if (mru->mru_oid)
	val = PyUnicode_FromString(mru->mru_oid);
    else {
	Py_INCREF(Py_None);
	val = Py_None;
    }
    if (PyDict_SetItemString(ret, "oid", val) == -1)
	goto failed;
    Py_DECREF(val);
    val = LibLDAP_C2Py_strs(mru->mru_names);
    if (!val)
	goto failed;
    if (PyDict_SetItemString(ret, "names", val) == -1)
	goto failed;
    Py_DECREF(val);
    if (mru->mru_desc)
	val = PyUnicode_FromString(mru->mru_desc);
    else {
	Py_INCREF(Py_None);
	val = Py_None;
    }    
    if (PyDict_SetItemString(ret, "desc", val) == -1)
	goto failed;
    Py_DECREF(val);
    val = PyBool_FromLong((long) mru->mru_obsolete);
    if (PyDict_SetItemString(ret, "obsolete", val) == -1)
	goto failed;
    Py_DECREF(val);
    val = LibLDAP_C2Py_strs(mru->mru_applies_oids);
    if (!val)
	goto failed;
    if (PyDict_SetItemString(ret, "applies_oids", val) == -1)
	goto failed;
    Py_DECREF(val);
    val = LibLDAP_C2Py_lseis(mru->mru_extensions);
    if (!val)
	goto failed;
    if (PyDict_SetItemString(ret, "extensions", val) == -1)
	goto failed;
    Py_DECREF(val);
    ldap_matchingruleuse_free(mru);
    return ret;
  failed:
    ldap_matchingruleuse_free(mru);
    Py_XDECREF(val);
    Py_DECREF(ret);
    return NULL;
}

PyDoc_STRVAR(LibLDAP_ldap_str2attributetypeDoc, "");

static PyObject *
LibLDAP_ldap_str2attributetype(PyObject *self, PyObject *args)
{
    const char *str, *errp;
    int code, flags = LDAP_SCHEMA_ALLOW_NONE;
    LDAPAttributeType *at;
    PyObject *ret, *val;

    if (!PyArg_ParseTuple(args, "s|i", &str, &flags))
	return NULL;
    if (LibLDAP_check_flags(flags, "ldap_str2attributetype") < 0)
	return NULL;
    at = ldap_str2attributetype(str, &code, &errp, flags);
    if (!at)
	return PyErr_Format(
	    LibLDAPErr, "ldap_str2attributetype(): `%s': %s", errp,
	    ldap_scherr2str(code));
    ret = PyDict_New();
    if (!ret) {
	ldap_attributetype_free(at);
	return NULL;
    }
    if (at->at_oid)
	val = PyUnicode_FromString(at->at_oid);
    else {
	Py_INCREF(Py_None);
	val = Py_None;
    }
    if (PyDict_SetItemString(ret, "oid", val) == -1)
	goto failed;
    Py_DECREF(val);
    val = LibLDAP_C2Py_strs(at->at_names);
    if (!val)
	goto failed;
    if (PyDict_SetItemString(ret, "names", val) == -1)
	goto failed;
    Py_DECREF(val);
    if (at->at_desc)
	val = PyUnicode_FromString(at->at_desc);
    else {
	Py_INCREF(Py_None);
	val = Py_None;
    }    
    if (PyDict_SetItemString(ret, "desc", val) == -1)
	goto failed;
    Py_DECREF(val);
    val = PyBool_FromLong((long) at->at_obsolete);
    if (PyDict_SetItemString(ret, "obsolete", val) == -1)
	goto failed;
    Py_DECREF(val);
    if (at->at_sup_oid)
	val = PyUnicode_FromString(at->at_sup_oid);
    else {
	Py_INCREF(Py_None);
	val = Py_None;
    }
    if (PyDict_SetItemString(ret, "sup_oid", val) == -1)
	goto failed;
    Py_DECREF(val);
    if (at->at_equality_oid)
	val = PyUnicode_FromString(at->at_equality_oid);
    else {
	Py_INCREF(Py_None);
	val = Py_None;
    }
    if (PyDict_SetItemString(ret, "equality_oid", val) == -1)
	goto failed;
    Py_DECREF(val);
    if (at->at_ordering_oid)
	val = PyUnicode_FromString(at->at_ordering_oid);
    else {
	Py_INCREF(Py_None);
	val = Py_None;
    }
    if (PyDict_SetItemString(ret, "ordering_oid", val) == -1)
	goto failed;
    Py_DECREF(val);
    if (at->at_substr_oid)
	val = PyUnicode_FromString(at->at_substr_oid);
    else {
	Py_INCREF(Py_None);
	val = Py_None;
    }
    if (PyDict_SetItemString(ret, "substr_oid", val) == -1)
	goto failed;
    Py_DECREF(val);
    if (at->at_syntax_oid)
	val = PyUnicode_FromString(at->at_syntax_oid);
    else {
	Py_INCREF(Py_None);
	val = Py_None;
    }
    if (PyDict_SetItemString(ret, "syntax_oid", val) == -1)
	goto failed;
    Py_DECREF(val);
    val = PyLong_FromLong((long) at->at_syntax_len);
    if (PyDict_SetItemString(ret, "syntax_len", val) == -1)
	goto failed;
    Py_DECREF(val);
    val = PyBool_FromLong((long) at->at_single_value);
    if (PyDict_SetItemString(ret, "single_value", val) == -1)
	goto failed;
    Py_DECREF(val);
    val = PyBool_FromLong((long) at->at_collective);
    if (PyDict_SetItemString(ret, "collective", val) == -1)
	goto failed;
    Py_DECREF(val);
    val = PyBool_FromLong((long) at->at_no_user_mod);
    if (PyDict_SetItemString(ret, "no_user_mod", val) == -1)
	goto failed;
    Py_DECREF(val);
    val = PyLong_FromLong((long) at->at_usage);
    if (PyDict_SetItemString(ret, "usage", val) == -1)
	goto failed;
    Py_DECREF(val);
    val = LibLDAP_C2Py_lseis(at->at_extensions);
    if (!val)
	goto failed;
    if (PyDict_SetItemString(ret, "extensions", val) == -1)
	goto failed;
    Py_DECREF(val);
    ldap_attributetype_free(at);
    return ret;
  failed:
    ldap_attributetype_free(at);
    Py_XDECREF(val);
    Py_DECREF(ret);
    return NULL;
}

PyDoc_STRVAR(LibLDAP_ldap_str2objectclassDoc, "");

static PyObject *
LibLDAP_ldap_str2objectclass(PyObject *self, PyObject *args)
{
    const char *str, *errp;
    int code, flags = LDAP_SCHEMA_ALLOW_NONE;
    LDAPObjectClass *oc;
    PyObject *ret, *val;

    if (!PyArg_ParseTuple(args, "s|i", &str, &flags))
	return NULL;
    if (LibLDAP_check_flags(flags, "ldap_str2objectclass") < 0)
	return NULL;
    oc = ldap_str2objectclass(str, &code, &errp, flags);
    if (!oc)
	return PyErr_Format(
	    LibLDAPErr, "ldap_str2objectclass(): `%s': %s", errp,
	    ldap_scherr2str(code));
    ret = PyDict_New();
    if (!ret) {
	ldap_objectclass_free(oc);
	return NULL;
    }
    if (oc->oc_oid)
	val = PyUnicode_FromString(oc->oc_oid);
    else {
	Py_INCREF(Py_None);
	val = Py_None;
    }
    if (PyDict_SetItemString(ret, "oid", val) == -1)
	goto failed;
    Py_DECREF(val);
    val = LibLDAP_C2Py_strs(oc->oc_names);
    if (!val)
	goto failed;
    if (PyDict_SetItemString(ret, "names", val) == -1)
	goto failed;
    Py_DECREF(val);
    if (oc->oc_desc)
	val = PyUnicode_FromString(oc->oc_desc);
    else {
	Py_INCREF(Py_None);
	val = Py_None;
    }    
    if (PyDict_SetItemString(ret, "desc", val) == -1)
	goto failed;
    Py_DECREF(val);
    val = PyBool_FromLong((long) oc->oc_obsolete);
    if (PyDict_SetItemString(ret, "obsolete", val) == -1)
	goto failed;
    Py_DECREF(val);
    val = LibLDAP_C2Py_strs(oc->oc_sup_oids);
    if (!val)
	goto failed;
    if (PyDict_SetItemString(ret, "sup_oids", val) == -1)
	goto failed;
    Py_DECREF(val);
    val = PyLong_FromLong((long) oc->oc_kind);
    if (PyDict_SetItemString(ret, "kind", val) == -1)
	goto failed;
    Py_DECREF(val);
    val = LibLDAP_C2Py_strs(oc->oc_at_oids_must);
    if (!val)
	goto failed;
    if (PyDict_SetItemString(ret, "at_oids_must", val) == -1)
	goto failed;
    Py_DECREF(val);
    val = LibLDAP_C2Py_strs(oc->oc_at_oids_may);
    if (!val)
	goto failed;
    if (PyDict_SetItemString(ret, "at_oids_may", val) == -1)
	goto failed;
    Py_DECREF(val);
    val = LibLDAP_C2Py_lseis(oc->oc_extensions);
    if (!val)
	goto failed;
    if (PyDict_SetItemString(ret, "extensions", val) == -1)
	goto failed;
    Py_DECREF(val);
    ldap_objectclass_free(oc);
    return ret;
  failed:
    ldap_objectclass_free(oc);
    Py_XDECREF(val);
    Py_DECREF(ret);
    return NULL;
}

static PyMethodDef LibLDAPSchemaMethods[] = {
    {"ldap_str2syntax", (PyCFunction) LibLDAP_ldap_str2syntax,
     METH_VARARGS, LibLDAP_ldap_str2syntaxDoc
    },
    {"ldap_str2matchingrule", (PyCFunction) LibLDAP_ldap_str2matchingrule,
     METH_VARARGS, LibLDAP_ldap_str2matchingruleDoc
    },
    {"ldap_str2matchingruleuse", (PyCFunction) LibLDAP_ldap_str2matchingruleuse,
     METH_VARARGS, LibLDAP_ldap_str2matchingruleuseDoc
    },
    {"ldap_str2attributetype", (PyCFunction) LibLDAP_ldap_str2attributetype,
     METH_VARARGS, LibLDAP_ldap_str2attributetypeDoc
    },
    {"ldap_str2objectclass", (PyCFunction) LibLDAP_ldap_str2objectclass,
     METH_VARARGS, LibLDAP_ldap_str2objectclassDoc
    },
    {NULL, NULL, 0, NULL}
};

/*****************************************************************************
 * GLOBAL FUNCTION DEFINITIONS
 *****************************************************************************/

int
LibLDAP_add_schema_methods(PyObject *m)
{
    PyMethodDef *ml;

    for (ml = LibLDAPSchemaMethods; ml->ml_name; ml++) {
	PyObject *func = PyCFunction_New(ml, NULL);

	if (!func)
	    return -1;
	if (PyModule_AddObject(m, ml->ml_name, func) == -1) {
	    Py_DECREF(func);
	    return -1;
	}
    }	
    return 0;
}

/*****************************************************************************
 * LOCAL FUNCTION DEFINITIONS
 *****************************************************************************/

static PyObject *
LibLDAP_C2Py_strs(char **strs)
{
    char **str;
    PyObject *ret = PyList_New(0);

    if (!ret)
	return NULL;
    if (!strs)
	return ret;
    for (str = strs; *str; str++) {
	PyObject *py_str = PyUnicode_FromString(*str);

	if (!py_str) {
	    Py_DECREF(ret);
	    return NULL;
	}
	if (PyList_Append(ret, py_str) == -1) {
	    Py_DECREF(py_str);
	    Py_DECREF(ret);
	    return NULL;
	}
	Py_DECREF(py_str);
    }
    return ret;
}

static PyObject *
LibLDAP_C2Py_lseis(LDAPSchemaExtensionItem **lseis)
{
    LDAPSchemaExtensionItem **lsei;
    PyObject *ret;


    if (!lseis)
	Py_RETURN_NONE;
    ret = PyList_New(0);
    if (!ret)
	return NULL;
    for (lsei = lseis; *lsei; lsei++) {
	PyObject *item, *values = LibLDAP_C2Py_strs((*lsei)->lsei_values);

	if (!values) {
	    Py_DECREF(ret);
	    return NULL;
	}
	item = Py_BuildValue("(sO)", (*lsei)->lsei_name, values);
	if (!item) {
	    Py_DECREF(values);
	    Py_DECREF(ret);
	    return NULL;
	}
	Py_DECREF(values);
	if (PyList_Append(ret, item) == -1) {
	    Py_DECREF(item);
	    Py_DECREF(values);
	    Py_DECREF(ret);
	    return NULL;
	}
	Py_DECREF(item);
    }
    return ret;
}

static int
LibLDAP_check_flags(int flags, const char *func)
{
    if (flags >= LDAP_SCHEMA_ALLOW_NONE && flags <= LDAP_SCHEMA_ALLOW_ALL)
	return 0;
    (void) PyErr_Format(LibLDAPErr,"%s(): `%d': invalid flags", func, flags);
    return -1;
}
