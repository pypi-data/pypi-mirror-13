/*****************************************************************************
 * INCLUDED FILES & MACRO DEFINITIONS
 *****************************************************************************/

#include <libldap.h>
#include <LDAPControls.h>

#ifdef __LIBLDAP_DARWIN__
extern PyObject *LibLDAPErr;
#endif

/*****************************************************************************
 * libldap.LDAPControl OBJECT
 *****************************************************************************/

/* DOC */

PyDoc_STRVAR(LDAPControlObjectDoc, "");

/* SPECIAL METHODS */

static void
LDAPControlObject_dealloc(LDAPControlObject *self)
{
    if (self->ctrl)
	ldap_control_free(self->ctrl);
    Py_TYPE(self)->tp_free((PyObject *) self);
}

static int
LDAPControlObject_init(LDAPControlObject *self, PyObject *args, PyObject *kwds)
{
    PyErr_SetString(
        LibLDAPErr, "`LDAPControl' object cannot be created directly, "
        "use instead `create_*_control()' methods of a `LDAP' object instance"
        );
    return -1;
}

static PyObject *
LDAPControlObject_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    LDAPControlObject *self;

    self = (LDAPControlObject *) type->tp_alloc(type, 0);
    if (self)
	self->ctrl = NULL;
    return (PyObject *) self;
}

/* TYPE */

PyTypeObject LDAPControlTypeObject = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "_libldap.LDAPControl",			/* tp_name */
    sizeof(LDAPControlObject),			/* tp_basicsize */
    0,						/* tp_itemsize */
    (destructor) LDAPControlObject_dealloc,	/* tp_dealloc */
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
    Py_TPFLAGS_DEFAULT,				/* tp_flags */
    LDAPControlObjectDoc,			/* tp_doc */
    0,						/* tp_traverse */
    0,						/* tp_clear */
    0,						/* tp_richcompare */
    0,						/* tp_weaklistoffset */
    0,						/* tp_iter */
    0,						/* tp_iternext */
    0,						/* tp_methods */
    0,						/* tp_members */
    0,						/* tp_getset */
    0,						/* tp_base */
    0,						/* tp_dict */
    0,						/* tp_descr_get */
    0,						/* tp_descr_set */
    0,						/* tp_dictoffset */
    (initproc) LDAPControlObject_init,		/* tp_init */
    0,						/* tp_alloc */
    (newfunc) LDAPControlObject_new,		/* tp_new */
};

/*****************************************************************************
 * libldap.LDAPControls OBJECT
 *****************************************************************************/

/* DOC */

PyDoc_STRVAR(LDAPControlsObjectDoc, "");

/* SPECIAL METHODS */

static void
LDAPControlsObject_dealloc(LDAPControlsObject *self)
{
    if (self->ctrls)
	ldap_controls_free(self->ctrls);
    Py_TYPE(self)->tp_free((PyObject *) self);
}

static int
LDAPControlsObject_init(LDAPControlsObject *self, PyObject *args,
			PyObject *kwds)
{
    Py_ssize_t i, len = PyTuple_GET_SIZE(args);
    LDAPControl **ctrls;

    if (!len) {
	(void) PyErr_Format(
	    PyExc_TypeError, "%s.__init__() takes at least one argument",
	    LDAPObjName(self)
	    );
	return -1;
    }
    for (i = 0; i < len; i++) {
	PyObject *ctrl = PyTuple_GET_ITEM(args, i);

	if (!LDAPControlObject_Check(ctrl)) {
	    (void) PyErr_Format(
		PyExc_TypeError, "%s.__init__(): arg%d is not an instance "
		"of LDAPControl object", LDAPObjName(self), i + 1
		);
	    return -1;
	}
    }
    self->ctrls = PyMem_New(LDAPControl *, len + 1);
    if (!self->ctrls) {
	PyErr_SetNone(PyExc_MemoryError);
	return -1;
    }
    (void) memset((void *) self->ctrls, 0, (len + 1) * sizeof(LDAPControl *));
    for (i = 0, ctrls = self->ctrls; i < len; i++, ctrls++) {
	LDAPControlObject *ctrl =
	    (LDAPControlObject *) PyTuple_GET_ITEM(args, i);

	*ctrls = ldap_control_dup(ctrl->ctrl);
	if (!*ctrls) {
	    ldap_controls_free(self->ctrls);
	    (void) PyErr_Format(
		LibLDAPErr, "%s.__init__(): ldap_control_dup() failed",
		LDAPObjName(self)
		);
	    return -1;
	}
    }
    return 0;
}

static PyObject *
LDAPControlsObject_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    LDAPControlsObject *self;

    self = (LDAPControlsObject *) type->tp_alloc(type, 0);
    if (self)
	self->ctrls = NULL;
    return (PyObject *) self;
}

/* TYPE */

PyTypeObject LDAPControlsTypeObject = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "_libldap.LDAPControls",			/* tp_name */
    sizeof(LDAPControlsObject),			/* tp_basicsize */
    0,						/* tp_itemsize */
    (destructor) LDAPControlsObject_dealloc,	/* tp_dealloc */
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
    Py_TPFLAGS_DEFAULT,				/* tp_flags */
    LDAPControlsObjectDoc,			/* tp_doc */
    0,						/* tp_traverse */
    0,						/* tp_clear */
    0,						/* tp_richcompare */
    0,						/* tp_weaklistoffset */
    0,						/* tp_iter */
    0,						/* tp_iternext */
    0,						/* tp_methods */
    0,						/* tp_members */
    0,						/* tp_getset */
    0,						/* tp_base */
    0,						/* tp_dict */
    0,						/* tp_descr_get */
    0,						/* tp_descr_set */
    0,						/* tp_dictoffset */
    (initproc) LDAPControlsObject_init,		/* tp_init */
    0,						/* tp_alloc */
    (newfunc) LDAPControlsObject_new,		/* tp_new */
};

/*****************************************************************************
 * GLOBAL FUNCTION DEFINITIONS
 *****************************************************************************/

int
LDAPControls_Check(
    LDAP *ldp, LDAPMessage *res, const char *cls, const char *meth
    )
{
    int ecode, errcode;
    char *errmsg = NULL;
    LDAPControl **ctrls, **ptr;

    ecode = ldap_parse_result(
	ldp, res, &errcode, NULL, &errmsg, NULL, &ctrls, 0);
    if (ecode != LDAP_SUCCESS || errcode != LDAP_SUCCESS) {
	(void) PyErr_Format(
	    LibLDAPErr,
	    "%s.%s(): ldap_parse_result(): %s: error code %d: error msg: %s",
	    cls, meth, ldap_err2string(ecode), errcode,
	    errmsg ? errmsg : "<none>"
	    );
	ldap_memfree(errmsg);
	return -1;
    }
    ldap_memfree(errmsg);
    if (!ctrls)
	return 0;
    for (ptr = ctrls; *ptr; ptr++) {
	if (!strcmp((*ptr)->ldctl_oid, LDAP_CONTROL_SORTRESPONSE)) {
	    char *attr = NULL;
	    
	    ecode = ldap_parse_sortresponse_control(ldp, *ptr, &errcode, &attr);
	    if (ecode != LDAP_SUCCESS || errcode != LDAP_SUCCESS) {
		(void) PyErr_Format(
		    LibLDAPErr, "%s.%s(): ldap_parse_sortresponse_control: "
		    "%s: error code %d: attribute in error: %s",
		    cls, meth, ldap_err2string(ecode), errcode,
		    attr ? attr : "<none>"
		    );
		ldap_memfree((void *) attr);
		ldap_controls_free(ctrls);
		return -1;
	    }
	    ldap_memfree((void *) attr);
	}
    }
    ldap_controls_free(ctrls);
    return 0;
}
