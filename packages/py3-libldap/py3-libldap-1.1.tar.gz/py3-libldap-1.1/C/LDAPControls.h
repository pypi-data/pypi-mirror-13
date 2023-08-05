#ifndef LDAPCONTROLS_H
#define LDAPCONTROLS_H

/*****************************************************************************
 * GLOBAL FUNCTION DECLARATIONS
 *****************************************************************************/

int LDAPControls_Check(LDAP *, LDAPMessage *, const char *, const char *);

/*****************************************************************************
 * libldap.LDAPControl OBJECT
 *****************************************************************************/

/* OBJECT */

typedef struct {
    PyObject_HEAD
    LDAPControl *ctrl;
} LDAPControlObject;

extern PyTypeObject LDAPControlTypeObject;

#define LDAPControlObject_Check(o) ((o)->ob_type == &LDAPControlTypeObject)

/*****************************************************************************
 * libldap.LDAPControls OBJECT
 *****************************************************************************/

/* OBJECT */

typedef struct {
    PyObject_HEAD
    LDAPControl **ctrls;
} LDAPControlsObject;

extern PyTypeObject LDAPControlsTypeObject;

#define LDAPControlsObject_Check(o) ((o)->ob_type == &LDAPControlsTypeObject)

#endif /* LDAPCONTROLS_H */
