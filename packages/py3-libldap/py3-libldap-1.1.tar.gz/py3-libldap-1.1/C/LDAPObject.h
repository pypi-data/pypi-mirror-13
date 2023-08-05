#ifndef LDAPOBJECT_H
#define LDAPOBJECT_H

/*****************************************************************************
 * INCLUDED FILES & MACRO DEFINITIONS
 *****************************************************************************/

#include <sys/types.h>
#include <sys/socket.h>

/*****************************************************************************
 * libldap.LDAP OBJECT
 *****************************************************************************/

/* OBJECT */

typedef struct {
    PyObject_HEAD
    PyObject        *uri;
    PyObject        *dn;
    LDAP            *ldp;
    LDAPURLDesc     *lud;
    struct sockaddr *addr;
    socklen_t        addrlen;
} LDAPObject;

extern PyTypeObject LDAPTypeObject;

#define LDAPObject_Check(o) ((o)->ob_type == &LDAPTypeObject)

#endif /* LDAPOBJECT_H */
