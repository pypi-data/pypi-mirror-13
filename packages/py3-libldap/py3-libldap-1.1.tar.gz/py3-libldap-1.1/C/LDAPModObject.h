#ifndef LDAPMODOBJECT_H
#define LDAPMODOBJECT_H

/*****************************************************************************
 * libldap.LDAPMod OBJECT
 *****************************************************************************/

/* OBJECT */

typedef struct {
    PyObject_HEAD
    LDAPMod *mod;
} LDAPModObject;

extern PyTypeObject LDAPModTypeObject;

#define LDAPModObject_Check(o) ((o)->ob_type == &LDAPModTypeObject)

#endif /* LDAPMODOBJECT_H */
