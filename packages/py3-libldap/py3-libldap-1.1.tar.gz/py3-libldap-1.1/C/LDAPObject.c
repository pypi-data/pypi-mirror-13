/*****************************************************************************
 * INCLUDED FILES & MACRO DEFINITIONS
 *****************************************************************************/

#include <libldap.h>
#include <LDAPObject.h>
#include <LDAPModObject.h>
#include <LDAPControls.h>
#include <netinet/in.h>
#include <netdb.h>

#ifdef __LIBLDAP_DARWIN__
extern PyObject *LibLDAPErr;
#endif

/*****************************************************************************
 * LOCAL VARIABLES
 *****************************************************************************/

static char LDAPObject_complete_dn_buf[1024];

/*****************************************************************************
 * LOCAL FUNCTION DECLARATIONS
 *****************************************************************************/

static const char *ldap_url_err2string(int);
static const char *LDAPObject_complete_dn(const char *, PyObject *);
static LDAPMod **LDAPObject_mods_parse(LDAPObject *, PyObject *, const char *);
static int LDAPObject_conn_valid(PyObject *, const char *);

/*****************************************************************************
 * libldap.LDAP OBJECT
 *****************************************************************************/

/* DOC */

PyDoc_STRVAR(LDAPObjectDoc, "");

/* METHODS */

PyDoc_STRVAR(LDAPObjectDoc_simple_bind_s, "");

static PyObject *
LDAPObject_simple_bind_s(LDAPObject *self, PyObject *args, PyObject *kwds)
{
    int ecode;
    const char *user = NULL, *password = NULL;
    static char *kwlist[] = {"user", "password", NULL};

    if (!LDAPObject_conn_valid((PyObject *) self, "simple_bind_s"))
	return NULL;
    if (!PyArg_ParseTupleAndKeywords(
	    args, kwds, "|ss", kwlist, &user, &password))
	return NULL;
    if (user)
	user = LDAPObject_complete_dn(user, self->dn);
    ecode = ldap_simple_bind_s(self->ldp, user, password);
    if (ecode != LDAP_SUCCESS)
	return PyErr_Format(
	    LibLDAPErr, "%s.simple_bind_s(): ldap_simple_bind_s(): %s",
	    LDAPObjName(self), ldap_err2string(ecode)
	    );
    Py_RETURN_NONE;
}

PyDoc_STRVAR(LDAPObjectDoc_bind_s, "");

static PyObject *
LDAPObject_bind_s(LDAPObject *self, PyObject *args, PyObject *kwds)
{
    int ecode, method = LDAP_AUTH_SIMPLE;
    const char *user = NULL, *password = NULL;
    static char *kwlist[] = {"user", "password", "method", NULL};

    if (!LDAPObject_conn_valid((PyObject *) self, "bind_s"))
	return NULL;
    if (!PyArg_ParseTupleAndKeywords(
	    args, kwds, "|ssi", kwlist, &user, &password, &method))
	return NULL;
    if (method != LDAP_AUTH_SIMPLE)
	return PyErr_Format(
	    LibLDAPErr,
	    "%s.bind_s(): only simple authentication [LDAP_AUTH_SIMPLE] "
	    "is supported", LDAPObjName(self)
	    );
    if (user)
	user = LDAPObject_complete_dn(user, self->dn);
    ecode = ldap_bind_s(self->ldp, user, password, method);
    if (ecode != LDAP_SUCCESS)
	return PyErr_Format(
	    LibLDAPErr, "%s.bind_s(): ldap_bind_s(): %s",
	    LDAPObjName(self), ldap_err2string(ecode)
	    );
    Py_RETURN_NONE;
}

PyDoc_STRVAR(LDAPObjectDoc_unbind_s, "");

static PyObject *
LDAPObject_unbind_s(LDAPObject *self)
{
    int ecode;

    if (!LDAPObject_conn_valid((PyObject *) self, "unbind_s"))
	return NULL;
    ecode = ldap_unbind_s(self->ldp);
    if (ecode != LDAP_SUCCESS)
	return PyErr_Format(
	    LibLDAPErr, "%s.unbind_s(): ldap_simple_bind_s(): %s",
	    LDAPObjName(self), ldap_err2string(ecode)
	    );
    self->ldp = NULL;
    Py_RETURN_NONE;
}

PyDoc_STRVAR(LDAPObjectDoc_start_tls, "");

static PyObject *
LDAPObject_start_tls(LDAPObject *self)
{
    int ecode, msgid;

    if (!LDAPObject_conn_valid((PyObject *) self, "start_tls"))
	return NULL;
    ecode = ldap_start_tls(self->ldp, NULL, NULL, &msgid);
    if (ecode != LDAP_SUCCESS)
	return PyErr_Format(
	    LibLDAPErr, "%s.start_tls(): ldap_start_tls(): %s",
	    LDAPObjName(self), ldap_err2string(ecode)
	    );
    return PyLong_FromLong((long) msgid);
}

PyDoc_STRVAR(LDAPObjectDoc_start_tls_s, "");

static PyObject *
LDAPObject_start_tls_s(LDAPObject *self)
{
    int ecode;

    if (!LDAPObject_conn_valid((PyObject *) self, "start_tls_s"))
	return NULL;
    ecode = ldap_start_tls_s(self->ldp, NULL, NULL);
    if (ecode != LDAP_SUCCESS)
	return PyErr_Format(
	    LibLDAPErr, "%s.start_tls_s(): ldap_start_tls_s(): %s",
	    LDAPObjName(self), ldap_err2string(ecode)
	    );
    Py_RETURN_NONE;
}

PyDoc_STRVAR(LDAPObjectDoc_get_option, "");

static PyObject *
LDAPObject_get_option(LDAPObject *self, PyObject *args)
{
    int ecode, opt, optval;
    LDAP *ldp = self ? self->ldp : NULL;
    
    if (!PyArg_ParseTuple(args, "i", &opt))
	return NULL;
    switch (opt) {
    case LDAP_OPT_PROTOCOL_VERSION:
    case LDAP_OPT_X_TLS_REQUIRE_CERT:
	ecode = ldap_get_option(ldp, opt, (void *) &optval);
	if (ecode != LDAP_OPT_SUCCESS)
	    return PyErr_Format(
		LibLDAPErr,"%s.get_option(): ldap_get_option() failed",
		LDAPObjName(self)
		);
	break;
    default:
	return PyErr_Format(
	    LibLDAPErr, "%s.get_option(): `%d': option not supported",
	    LDAPObjName(self)
	    );
    }
    return Py_BuildValue("i", optval);
}

PyDoc_STRVAR(LDAPObjectDoc_set_option, "");

static PyObject *
LDAPObject_set_option(LDAPObject *self, PyObject *args)
{
    int ecode, opt, optval;
    LDAP *ldp = self ? self->ldp : NULL;
    
    if (!PyArg_ParseTuple(args, "ii", &opt, &optval))
	return NULL;
    switch (opt) {
    case LDAP_OPT_PROTOCOL_VERSION:
    case LDAP_OPT_X_TLS_REQUIRE_CERT:
	ecode = ldap_set_option(ldp, opt, (const void *) &optval);
	if (ecode != LDAP_OPT_SUCCESS)
	    return PyErr_Format(
		LibLDAPErr,"%s.set_option(): ldap_set_option() failed",
		LDAPObjName(self)
		);
	break;
    default:
	return PyErr_Format(
	    LibLDAPErr, "%s.set_option(): `%d': option not supported",
	    LDAPObjName(self)
	    );
    }
    Py_RETURN_NONE;
}

PyDoc_STRVAR(LDAPObjectDoc_search_ext_s, "");

static PyObject *
LDAPObject_search_ext_s(LDAPObject *self, PyObject *args, PyObject *kwds)
{
    char *base = NULL, *filter = NULL, **attrs = NULL, **attr;
    int ecode, limit = LDAP_NO_LIMIT, scope = LDAP_SCOPE_SUBTREE, attrsonly;
    struct timeval tv = {0L, 0L}, *to = NULL;
    PyObject *py_attrs = NULL, *py_attrsonly = Py_False, *ret;
    LDAPControlsObject *serverctrls = NULL, *clientctrls = NULL;
    LDAPMessage *res, *ptr;
    LDAPControl **sctrls, **cctrls;
    static char *kwlist[] = {
	"base", "scope", "filter", "attrs", "attrsonly", "serverctrls",
	"clientctrls", "limit", "timeout", NULL
    };

    if (!LDAPObject_conn_valid((PyObject *) self, "search_ext_s"))
	return NULL;
    if (!PyArg_ParseTupleAndKeywords(
	    args, kwds, "|sisO!O!O!O!il", kwlist, &base, &scope, &filter,
	    &PyList_Type, &py_attrs, &PyBool_Type, &py_attrsonly,
	    &LDAPControlsTypeObject, &serverctrls, &LDAPControlsTypeObject,
	    &clientctrls, &limit, &tv.tv_sec))
	return NULL;
    if (py_attrs) {
	Py_ssize_t i, len = PyList_Size(py_attrs);

	if (!len)
	    return PyErr_Format(
		PyExc_TypeError,
		"%s.search_ext_s(): argument `attrs' must be a non empty list",
		LDAPObjName(self)
		);
	attrs = PyMem_New(char *, len + 1);
	if (!attrs)
	    return PyErr_NoMemory();
	(void) memset((void *) attrs, 0, (len + 1) * sizeof(char *));
	for (i = 0, attr = attrs; i < len; i++, attr++) {
	    PyObject *py_attr = PyList_GET_ITEM(py_attrs, i);
	    Py_ssize_t l;

	    if (!PyUnicode_Check(py_attr)) {
		LibLDAP_value_free((void **) attrs);
		return PyErr_Format(
		    PyExc_TypeError,
		    "%s.search_ext_s(): argument `attrs' must be a list "
		    "of strings", LDAPObjName(self)
		    );
	    }
	    l = PyUnicode_GET_LENGTH(py_attr);
	    *attr = PyMem_New(char, l + 1);
	    if (!*attr) {
		LibLDAP_value_free((void **) attrs);
		return PyErr_NoMemory();
	    }
	    (void) memcpy((void *) *attr, PyUnicode_DATA(py_attr), l);
	    (*attr)[l] = 0;
	}
    }
    base = (char *) LDAPObject_complete_dn(base, self->dn);
    if (!base)
	return PyErr_Format(
	    PyExc_TypeError,
	    "%s.search_ext_s(): argument `base' is not setted",
	    LDAPObjName(self)
	    );
    attrsonly = py_attrsonly == Py_True ? 1 : 0;
    sctrls = serverctrls ? serverctrls->ctrls : NULL;
    cctrls = clientctrls ? clientctrls->ctrls : NULL;
    if (tv.tv_sec > 0)
	to = &tv;
    ecode = ldap_search_ext_s(
	self->ldp, base, scope, filter, attrs, attrsonly, sctrls, cctrls, to,
	limit, &res);
    LibLDAP_value_free((void **) attrs);
    if (ecode != LDAP_SUCCESS) {
	(void) ldap_msgfree(res);
	return PyErr_Format(
	    LibLDAPErr, "%s.search_ext_s(): ldap_search_ext_s(): %s",
	    LDAPObjName(self), ldap_err2string(ecode)
	    );
    }
    if (LDAPControls_Check(
	    self->ldp, res, LDAPObjName(self), "search_ext_s") < 0) {
	(void) ldap_msgfree(res);
	return NULL;
    }
    ret = PyList_New(0);
    if (!ret)
	return NULL;
    for (ptr = ldap_first_entry(self->ldp, res); ptr;
	 ptr = ldap_next_entry(self->ldp, ptr)) {
	char *attr, *dn;
	BerElement *ber;
	PyObject *py_attr = PyDict_New(), *py_entry;

	if (!py_attr)
	    goto failed;
	for (attr = ldap_first_attribute(self->ldp, ptr, &ber ); 
	     attr; attr = ldap_next_attribute(self->ldp, ptr, ber)) {
	    char **vals = NULL;
	    int i;
	    PyObject *py_vals = PyList_New(0);

	    if (!py_vals)
		goto clean;
	    vals = ldap_get_values(self->ldp, ptr, attr);
	    if (!vals) {
		(void) PyErr_Format(
		    LibLDAPErr, "%s.search_ext_s(): ldap_get_values(): %s",
		    LDAPObjName(self), ldap_err2string(ecode)
		    );
		goto clean;
	    }
	    for (i = 0; vals[i]; i++) {
		PyObject *py_val = PyUnicode_FromString(vals[i]);
		
		if (!py_val) {
		    ldap_value_free(vals);
		    goto clean;
		}
		if (PyList_Append(py_vals, py_val) == -1) {
		    Py_DECREF(py_val);
		    ldap_value_free(vals);
		    goto clean;
		}
		Py_DECREF(py_val);
	    }
	    ldap_value_free(vals);
	    if (PyDict_SetItemString(py_attr, attr, py_vals) == -1)
		goto clean;
	    Py_DECREF(py_vals);
	    ldap_memfree(attr);
	    continue;
	  clean:
	    Py_XDECREF(py_vals);
	    Py_DECREF(py_attr);
	    ldap_memfree(attr);
	    ber_free(ber, 0);
	    goto failed;
	}
	ber_free(ber, 0);
	dn = ldap_get_dn(self->ldp, ptr);
	if (!dn) {
	    (void) PyErr_Format(
		LibLDAPErr, "%s.search_ext_s(): ldap_get_dn(): %s",
		LDAPObjName(self), ldap_err2string(ecode)
		);
	    Py_DECREF(py_attr);
	    goto failed;
	}
	py_entry = Py_BuildValue("(sO)", dn, py_attr);
	Py_DECREF(py_attr);
	ldap_memfree(dn);
	if (!py_entry)
	    goto failed;
	if (PyList_Append(ret, py_entry) == -1) {
	    Py_DECREF(py_entry);
	    goto failed;
	}
	Py_DECREF(py_entry);
    }
    (void) ldap_msgfree(res);
    return ret;
  failed:
    Py_DECREF(ret);
    (void) ldap_msgfree(res);
    return NULL;
}

PyDoc_STRVAR(LDAPObjectDoc_add_ext_s, "");

static PyObject *
LDAPObject_add_ext_s(LDAPObject *self, PyObject *args, PyObject *kwds)
{
    char *dn;
    int ecode;
    PyObject *py_mods;
    LDAPMod **mods;
    LDAPControlsObject *serverctrls = NULL, *clientctrls = NULL;
    LDAPControl **sctrls, **cctrls;
    static char *kwlist[] = {"dn", "mods", "serverctrls", "clientctrls", NULL};

    if (!LDAPObject_conn_valid((PyObject *) self, "add_ext_s"))
	return NULL;
    if (!PyArg_ParseTupleAndKeywords(
	    args, kwds, "sO!|O!O!", kwlist, &dn, &PyList_Type, &py_mods,
	    &LDAPControlsTypeObject, &serverctrls, &LDAPControlsTypeObject,
	    &clientctrls))
	return NULL;
    dn = (char *) LDAPObject_complete_dn(dn, self->dn);
    mods = LDAPObject_mods_parse(self, py_mods, "add_ext_s");
    if (!mods)
    	return NULL;
    sctrls = serverctrls ? serverctrls->ctrls : NULL;
    cctrls = clientctrls ? clientctrls->ctrls : NULL;
    ecode = ldap_add_ext_s(self->ldp, dn, mods, sctrls, cctrls);
    LibLDAP_value_free((void **) mods);
    if (ecode != LDAP_SUCCESS)
	return PyErr_Format(
	    LibLDAPErr, "%s.add_ext_s(): ldap_add_ext_s(): %s",
	    LDAPObjName(self), ldap_err2string(ecode)
	    );
    Py_RETURN_NONE;
}

PyDoc_STRVAR(LDAPObjectDoc_delete_ext_s, "");

static PyObject *
LDAPObject_delete_ext_s(LDAPObject *self, PyObject *args, PyObject *kwds)
{
    char *dn;
    int ecode;
    LDAPControlsObject *serverctrls = NULL, *clientctrls = NULL;
    LDAPControl **sctrls, **cctrls;
    static char *kwlist[] = {"dn", "serverctrls", "clientctrls", NULL};

    if (!LDAPObject_conn_valid((PyObject *) self, "delete_ext_s"))
	return NULL;
    if (!PyArg_ParseTupleAndKeywords(
	    args, kwds, "s|O!O!", kwlist, &dn, &LDAPControlsTypeObject,
	    &serverctrls, &LDAPControlsTypeObject, &clientctrls))
	return NULL;
    dn = (char *) LDAPObject_complete_dn(dn, self->dn);
    sctrls = serverctrls ? serverctrls->ctrls : NULL;
    cctrls = clientctrls ? clientctrls->ctrls : NULL;
    ecode = ldap_delete_ext_s(self->ldp, dn , sctrls, cctrls);
    if (ecode != LDAP_SUCCESS) {
	return PyErr_Format(
	    LibLDAPErr, "%s.delete_ext_s(): ldap_delete_ext_s(): %s",
	    LDAPObjName(self), ldap_err2string(ecode)
	    );
    }
    Py_RETURN_NONE;
}

PyDoc_STRVAR(LDAPObjectDoc_modify_ext_s, "");

static PyObject *
LDAPObject_modify_ext_s(LDAPObject *self, PyObject *args, PyObject *kwds)
{
    char *dn;
    int ecode;
    PyObject *py_mods;
    LDAPMod **mods;
    LDAPControlsObject *serverctrls = NULL, *clientctrls = NULL;
    LDAPControl **sctrls, **cctrls;
    static char *kwlist[] = {"dn", "mods", "serverctrls", "clientctrls", NULL};

    if (!LDAPObject_conn_valid((PyObject *) self, "modify_ext_s"))
	return NULL;
    if (!PyArg_ParseTupleAndKeywords(
	    args, kwds, "sO!|O!O!", kwlist, &dn, &PyList_Type, &py_mods,
	    &LDAPControlsTypeObject, &serverctrls, &LDAPControlsTypeObject,
	    &clientctrls))
	return NULL;
    dn = (char *) LDAPObject_complete_dn(dn, self->dn);
    mods = LDAPObject_mods_parse(self, py_mods, "modify_ext_s");
    if (!mods)
    	return NULL;
    sctrls = serverctrls ? serverctrls->ctrls : NULL;
    cctrls = clientctrls ? clientctrls->ctrls : NULL;
    ecode = ldap_modify_ext_s(self->ldp, dn, mods, sctrls, cctrls);
    LibLDAP_value_free((void **) mods);
    if (ecode != LDAP_SUCCESS)
	return PyErr_Format(
	    LibLDAPErr, "%s.modify_ext_s(): ldap_modify_ext_s(): %s",
	    LDAPObjName(self), ldap_err2string(ecode)
	    );
    Py_RETURN_NONE;
}

PyDoc_STRVAR(LDAPObjectDoc_modrdn2_s, "");

static PyObject *
LDAPObject_modrdn2_s(LDAPObject *self, PyObject *args, PyObject *kwds)
{
    char *dn, *newrdn;
    int ecode, deleteoldrdn;
    PyObject *py_deleteoldrdn = Py_False;
    static char *kwlist[] = {"dn", "newrdn", "deleteoldrdn", NULL};

    if (!LDAPObject_conn_valid((PyObject *) self, "modrdn2_s"))
	return NULL;
    if (!PyArg_ParseTupleAndKeywords(
	    args, kwds, "ss|O!", kwlist, &dn, &newrdn, &PyBool_Type,
	    &py_deleteoldrdn))
	return NULL;
    dn = (char *) LDAPObject_complete_dn(dn, self->dn);
    deleteoldrdn = py_deleteoldrdn == Py_False ? 0 : 1;
    ecode = ldap_modrdn2_s(self->ldp, dn, newrdn, deleteoldrdn);
    if (ecode != LDAP_SUCCESS)
	return PyErr_Format(
	    LibLDAPErr, "%s.modrdn2_s(): "
	    "ldap_modrdn2_s(): %s", LDAPObjName(self),
	    ldap_err2string(ecode)
	    );
    Py_RETURN_NONE;
}

PyDoc_STRVAR(LDAPObjectDoc_create_sort_control, "");

static PyObject *
LDAPObject_create_sort_control(LDAPObject *self, PyObject *args, PyObject *kwds)
{
    char *keylist;
    int ecode, iscritical;
    LDAPSortKey **sk;
    LDAPControl *ctrl;
    LDAPControlObject *ret;
    PyObject *py_iscritical = Py_False;
    static char *kwlist[] = {"keylist", "iscritical", "serverctrls", NULL};

    if (!LDAPObject_conn_valid((PyObject *) self, "create_sort_control"))
	return NULL;
    if (!PyArg_ParseTupleAndKeywords(
	    args, kwds, "s|O!", kwlist, &keylist, &PyBool_Type, &py_iscritical))
	return NULL;
    ecode = ldap_create_sort_keylist(&sk, keylist);
    if (ecode != LDAP_SUCCESS)
	return PyErr_Format(
	    LibLDAPErr, "%s.create_sort_control(): "
	    "ldap_create_sort_keylist(): %s", LDAPObjName(self),
	    ldap_err2string(ecode)
	    );
    iscritical = py_iscritical == Py_False ? 0 : 1;
    ecode = ldap_create_sort_control(self->ldp, sk, iscritical, &ctrl);
    ldap_free_sort_keylist(sk);
    if (ecode != LDAP_SUCCESS)
	return PyErr_Format(
	    LibLDAPErr, "%s.create_sort_control(): "
	    "ldap_create_sort_control(): %s", LDAPObjName(self),
	    ldap_err2string(ecode)
	    );
    ret = (LDAPControlObject *)
	LDAPControlTypeObject.tp_new(&LDAPControlTypeObject, NULL, NULL);
    if (!ret) {
	ldap_control_free(ctrl);
	return NULL;
    }
    ret->ctrl = ctrl;
    return (PyObject *) ret;
}

PyDoc_STRVAR(LDAPObjectDoc_create_assertion_control, "");

static PyObject *
LDAPObject_create_assertion_control(
    LDAPObject *self, PyObject *args, PyObject *kwds
    )
{
    int ecode, iscritical;
    char *filter;
    LDAPControl *ctrl;
    LDAPControlObject *ret;
    PyObject *py_iscritical = Py_False;
    static char *kwlist[] = {"filter", "iscritical", NULL};

    if (!LDAPObject_conn_valid((PyObject *) self, "create_assertion_control"))
	return NULL;
    if (!PyArg_ParseTupleAndKeywords(
	    args, kwds, "s|O!", kwlist, &filter, &PyBool_Type, &py_iscritical))
	return NULL;
    iscritical = py_iscritical == Py_False ? 0 : 1;
    ecode = ldap_create_assertion_control(self->ldp, filter, iscritical, &ctrl);
    if (ecode != LDAP_SUCCESS)
	return PyErr_Format(
	    LibLDAPErr, "%s.create_assertion_control(): "
	    "ldap_create_assertion_control(): %s", LDAPObjName(self),
	    ldap_err2string(ecode)
	    );
    ret = (LDAPControlObject *)
	LDAPControlTypeObject.tp_new(&LDAPControlTypeObject, NULL, NULL);
    if (!ret) {
	ldap_control_free(ctrl);
	return NULL;
    }
    ret->ctrl = ctrl;
    return (PyObject *) ret;    
}

static PyMethodDef LDAPObjectMethods[] = {
    {"simple_bind_s", (PyCFunction) LDAPObject_simple_bind_s,
     METH_VARARGS | METH_KEYWORDS, LDAPObjectDoc_simple_bind_s
    },
    {"bind_s", (PyCFunction) LDAPObject_bind_s,
     METH_VARARGS | METH_KEYWORDS, LDAPObjectDoc_bind_s
    },
    {"unbind_s", (PyCFunction) LDAPObject_unbind_s, METH_NOARGS,
     LDAPObjectDoc_unbind_s
    },
    {"start_tls", (PyCFunction) LDAPObject_start_tls, METH_NOARGS,
     LDAPObjectDoc_start_tls
    },
    {"start_tls_s", (PyCFunction) LDAPObject_start_tls_s, METH_NOARGS,
     LDAPObjectDoc_start_tls_s
    },
    {"get_option", (PyCFunction) LDAPObject_get_option,
     METH_VARARGS, LDAPObjectDoc_get_option
    },
    {"set_option", (PyCFunction) LDAPObject_set_option,
     METH_VARARGS, LDAPObjectDoc_set_option
    },
    {"search_ext_s", (PyCFunction) LDAPObject_search_ext_s,
     METH_VARARGS | METH_KEYWORDS, LDAPObjectDoc_search_ext_s
    },
    {"add_ext_s", (PyCFunction) LDAPObject_add_ext_s,
     METH_VARARGS | METH_KEYWORDS, LDAPObjectDoc_add_ext_s
    },
    {"delete_ext_s", (PyCFunction) LDAPObject_delete_ext_s,
     METH_VARARGS | METH_KEYWORDS, LDAPObjectDoc_delete_ext_s
    },
    {"modify_ext_s", (PyCFunction) LDAPObject_modify_ext_s,
     METH_VARARGS | METH_KEYWORDS, LDAPObjectDoc_modify_ext_s
    },
    {"modrdn2_s", (PyCFunction) LDAPObject_modrdn2_s,
     METH_VARARGS | METH_KEYWORDS, LDAPObjectDoc_modrdn2_s
    },
    {"create_sort_control", (PyCFunction) LDAPObject_create_sort_control,
     METH_VARARGS | METH_KEYWORDS, LDAPObjectDoc_create_sort_control
    },
    {"create_assertion_control",
     (PyCFunction) LDAPObject_create_assertion_control,
     METH_VARARGS | METH_KEYWORDS, LDAPObjectDoc_create_assertion_control
    },
    {NULL, NULL, 0, NULL}
};

/* MEMBERS */

static PyMemberDef LDAPObjectMembers[] = {
    {"uri", T_OBJECT, offsetof(LDAPObject, uri), READONLY,
     "LDAP URI (Uniform Resource Identifier) - RFC 4516 compliant"},
    {NULL, 0, 0, 0, NULL}
};

/* GET/SET */

static PyObject *
LDAPObject_getscheme(LDAPObject *self, void *closure)
{
    if (!self->lud->lud_scheme)
	Py_RETURN_NONE;
    return PyUnicode_FromString(self->lud->lud_scheme);
}

static PyObject *
LDAPObject_gethost(LDAPObject *self, void *closure)
{
    if (!self->lud->lud_host)
	Py_RETURN_NONE;
    return PyUnicode_FromString(self->lud->lud_host);
}

static PyObject *
LDAPObject_getip(LDAPObject *self, void *closure)
{
    int ecode;
    char host[NI_MAXHOST];

    if (!self->addr)
	Py_RETURN_NONE;
    ecode = getnameinfo(
	self->addr, self->addrlen, host, sizeof(host), NULL, 0, NI_NUMERICHOST
	);
    if (ecode)
	return PyErr_Format(
	    LibLDAPErr, "`getip' attribute: getnameinfo(): %s",
	    gai_strerror(ecode)
	    );
    return PyUnicode_FromString(host);
}

static PyObject *
LDAPObject_getport(LDAPObject *self, void *closure)
{
    return PyLong_FromLong((long) self->lud->lud_port);
}

static PyObject *
LDAPObject_getdn(LDAPObject *self, void *closure)
{
    if (!self->dn)
	Py_RETURN_NONE;
    Py_INCREF(self->dn);
    return self->dn;
}

static int
LDAPObject_setdn(LDAPObject *self, PyObject *dn, void *closure)
{
    if (!dn) {
	PyErr_SetString(
	    PyExc_TypeError, "`dn' attribute cannot be deleted"
	    );
	return -1;
    }
    if (!PyUnicode_Check(dn) && dn != Py_None) {
	PyErr_SetString(
	    PyExc_TypeError, "`dn' attribute value must be a string or None"
	    );
	return -1;
    }
    Py_XDECREF(self->dn);
    if (dn == Py_None)
	self->dn = NULL;
    else {
	Py_INCREF(dn);
	self->dn = dn;
    }
    return 0;
}

static PyGetSetDef LDAPObjectGetSet[] = {
    {"scheme", (getter) LDAPObject_getscheme, NULL,
     "URI scheme",  NULL},
    {"host", (getter) LDAPObject_gethost, NULL,
     "LDAP host to contact",  NULL},
    {"ip", (getter) LDAPObject_getip, NULL,
     "IPv4/v6 address of LDAP host to contact",  NULL},
    {"port", (getter) LDAPObject_getport, NULL,
     "port on host",  NULL},
    {"dn", (getter) LDAPObject_getdn, (setter) LDAPObject_setdn,
     "base DN",  NULL},
    {NULL, NULL, NULL, NULL, NULL}
};

/* SPECIAL METHODS */

static void
LDAPObject_dealloc(LDAPObject *self)
{
    Py_XDECREF(self->uri);
    Py_XDECREF(self->dn);
    if (self->ldp)
	(void) ldap_unbind(self->ldp);
    ldap_free_urldesc(self->lud);
    PyMem_Free((void *) self->addr);
    Py_TYPE(self)->tp_free((PyObject *) self);
}

static int
LDAPObject_init(LDAPObject *self, PyObject *args, PyObject *kwds)
{
    const char *uri;
    int ecode, version = LDAP_VERSION3;
    struct addrinfo *res, hints = {
	.ai_flags = 0,
	.ai_family = AF_UNSPEC,
	.ai_socktype = SOCK_STREAM,
	.ai_protocol = IPPROTO_TCP
    };
    static char *kwlist[] = {"uri", "version", NULL};

    if (!PyArg_ParseTupleAndKeywords(
	    args, kwds, "s|i", kwlist, &uri, &version))
	return -1;
    if (version != LDAP_VERSION2 && version != LDAP_VERSION3) {
	(void) PyErr_Format(
	    PyExc_ValueError,
	    "%s.__init__(): argument `version' must be %d or %d",
	    LDAPObjName(self), LDAP_VERSION2, LDAP_VERSION3
	    );
	return -1;
    }    
    ecode = ldap_url_parse(uri, &self->lud);
    if (ecode != LDAP_URL_SUCCESS) {
	(void) PyErr_Format(
	    LibLDAPErr, "%s.__init__(): ldap_url_parse(): %s",
	    LDAPObjName(self), ldap_url_err2string(ecode)
	    );
	return -1;
    }
    ecode = getaddrinfo(self->lud->lud_host, NULL, &hints, &res);
    if (ecode) {
	(void) PyErr_Format(
	    LibLDAPErr,
	    "%s.__init__(): `%s': getaddrinfo(): %s", LDAPObjName(self),
	    self->lud->lud_host, gai_strerror(ecode)
	    );
	return -1;
    }
    self->addr = (struct sockaddr *) PyMem_Malloc(res->ai_addrlen);
    if (!self->addr) {
	PyErr_SetNone(PyExc_MemoryError);
	return -1;
    }
    (void) memcpy(
	(void *) self->addr, (const void *) res->ai_addr, res->ai_addrlen
	);
    self->addrlen = res->ai_addrlen;
    freeaddrinfo(res);
    if (self->lud->lud_port <=0 || self->lud->lud_port > 0xffff) {
	(void) PyErr_Format(
	    LibLDAPErr,
	    "%s.__init__(): %d: invalid  port, "
	    "must be an integer in range ]0, %d]", LDAPObjName(self),
	    self->lud->lud_port, 0xffff
	    );
	return -1;
    }
    if (self->lud->lud_dn) {
	char *s = strrchr(uri, '/');
	char u[s - uri + 1];

	self->dn = PyUnicode_FromString(self->lud->lud_dn);
	if (!self->dn)
	    return -1;
	(void) strncpy(u, uri, s - uri);
	u[s - uri] = 0;
	self->uri = PyUnicode_FromString(u);
    }
    else
	self->uri = PyUnicode_FromString(uri);
    if (!self->uri)
	return -1;
    ecode = ldap_initialize(
	&self->ldp, (char *) PyUnicode_1BYTE_DATA(self->uri));
    if (ecode != LDAP_SUCCESS) {
    	(void) PyErr_Format(
	    LibLDAPErr, "%s.__init__(): ldap_initialize() %s",
	    LDAPObjName(self), ldap_err2string(ecode)
	    );
    	return -1;
    }
    ecode = ldap_set_option(self->ldp, LDAP_OPT_PROTOCOL_VERSION, &version);
    if (ecode != LDAP_OPT_SUCCESS) {
	(void) PyErr_Format(
	    LibLDAPErr,
	    "%s.__init__(): ldap_set_option() [LDAP_OPT_PROTOCOL_VERSION] "
	    "failed", LDAPObjName(self)
	    );
	    return -1;
    }
    return 0;
}

static PyObject *
LDAPObject_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    LDAPObject *self;

    self = (LDAPObject *) type->tp_alloc(type, 0);
    if (self) {
	self->uri = NULL;
	self->dn = NULL;
	self->ldp = NULL;
	self->lud = NULL;
	self->addr = NULL;
	self->addrlen = 0;
    }
    return (PyObject *) self;
}

/* TYPE */

PyTypeObject LDAPTypeObject = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "_libldap.LDAP_",				/* tp_name */
    sizeof(LDAPObject),				/* tp_basicsize */
    0,						/* tp_itemsize */
    (destructor) LDAPObject_dealloc,		/* tp_dealloc */
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
    LDAPObjectDoc,				/* tp_doc */
    0,						/* tp_traverse */
    0,						/* tp_clear */
    0,						/* tp_richcompare */
    0,						/* tp_weaklistoffset */
    0,						/* tp_iter */
    0,						/* tp_iternext */
    LDAPObjectMethods,				/* tp_methods */
    LDAPObjectMembers,				/* tp_members */
    LDAPObjectGetSet,				/* tp_getset */
    0,						/* tp_base */
    0,						/* tp_dict */
    0,						/* tp_descr_get */
    0,						/* tp_descr_set */
    0,						/* tp_dictoffset */
    (initproc) LDAPObject_init,			/* tp_init */
    0,						/* tp_alloc */
    (newfunc) LDAPObject_new,			/* tp_new */
};

/*****************************************************************************
 * LOCAL FUNCTION DEFINITIONS
 *****************************************************************************/

static const char *__ldap_url_err2string[] = {
    "success",
    "can't allocate memory space",
    "parameter is bad",
    "URL doesn't begin with \"ldap[si]://\"",
    "URL is missing trailing \">\"",
    "URL is bad",
    "host port is bad",
    "bad (or missing) attributes",
    "scope string is invalid (or missing)",
    "bad or missing filter",
    "bad or missing extensions",
#define LDAP_URL_ERR_UNKNOWN 0x0b
    "unknown error"
};

static const char *
ldap_url_err2string(int ecode)
{
    if (ecode < LDAP_URL_SUCCESS || ecode > LDAP_URL_ERR_BADEXTS)
	return __ldap_url_err2string[LDAP_URL_ERR_UNKNOWN];
    return __ldap_url_err2string[ecode];
}

static const char *
LDAPObject_complete_dn(const char *dni, PyObject *dnc)
{
    const char *sep = dnc ? "," : "", *dncp = dnc ? PyUnicode_DATA(dnc) : "";
    size_t li = dni ? strlen(dni) : 0, lc = strlen(dncp);

    if (!dni) {
	if (!dnc)
	    return NULL;
	sep = dni = "";
    }
    if (strcasecmp(dni, LibLDAPSchemaBase)) {
	if (dnc && li >= lc) {
	    const char *s = dni + li - lc;
	    
	    if (!memcmp((const void *) s, (const void *) dncp, lc + 1))
		sep = dncp = "";
	}
    }
    else
	sep = dncp = "";	
    snprintf(
	LDAPObject_complete_dn_buf, sizeof(LDAPObject_complete_dn_buf),
	"%s%s%s", dni, sep, dncp
	);
    return LDAPObject_complete_dn_buf;
}

static LDAPMod **
LDAPObject_mods_parse(LDAPObject *self, PyObject *py_mods, const char *func)
{
    Py_ssize_t i, len = PyList_GET_SIZE(py_mods);
    LDAPMod **ptr, **ret;

    if (!len)
	return (LDAPMod **) PyErr_Format(
	    PyExc_TypeError, 
	    "%s.%s(): argument `mods' must be a non empty list",
	    LDAPObjName(self), func
	    );
    ret = PyMem_New(LDAPMod *, len + 1);
    if (!ret) {
	PyErr_SetNone(PyExc_MemoryError);
	return NULL;
    }
    (void) memset((void *) ret, 0, (len + 1) * sizeof(LDAPMod *));
    for (i = 0, ptr = ret; i < len; i++, ptr++) {
	PyObject *py_mod = PyList_GET_ITEM(py_mods, i);
	int isi = PyObject_IsInstance(py_mod, (PyObject *) &LDAPModTypeObject);

	if (isi == -1) {
	    LibLDAP_value_free((void **) ret);
	    return NULL;
	}
	if (!isi) {
	    LibLDAP_value_free((void **) ret);
	    return (LDAPMod **) PyErr_Format(
		PyExc_TypeError,
		"%s.%s(): argument `mods' must be a list of LDAPMod objects",
		LDAPObjName(self), func
		);
	}
	if (!strcmp(func, "add_ext_s") &&
	    ((LDAPModObject *) py_mod)->mod->mod_op != LDAP_MOD_ADD) {
	    LibLDAP_value_free((void **) ret);
	    return (LDAPMod **) PyErr_Format(
		PyExc_ValueError,
		"%s.%s(): attribute `mode' of each LDAPMod object must be "
		"%d (LDAP_MOD_ADD)", LDAPObjName(self), func, LDAP_MOD_ADD
		);
	}
	*ptr = PyMem_New(LDAPMod, 1);
	if (!*ptr) {
	    LibLDAP_value_free((void **) ret);
	    PyErr_SetNone(PyExc_MemoryError);
	    return NULL;
	}
	(void) memcpy(
	    (void *) *ptr, (const void *) ((LDAPModObject *) py_mod)->mod,
	    sizeof(**ptr)
	    );
    }
    return ret;
}

static int
LDAPObject_conn_valid(PyObject *pyo, const char *func)
{
    if (!((LDAPObject *) pyo)->ldp) {
	(void) PyErr_Format(
	    LibLDAPErr, "%s.%s(): invalid LDAP connection", LDAPObjName(pyo),
	    func
	    );
	return 0;
    }
    return 1;
}
