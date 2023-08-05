#ifndef LIBLDAP_H
#define LIBLDAP_H

/*****************************************************************************
 * INCLUDED FILES & MACRO DEFINITIONS
 *****************************************************************************/

#include <Python.h>
#include <structmember.h>
#include <ldap.h>

#define LibLDAPSchemaBase "cn=Subschema"
#define LDAPObjName(o) (((PyObject *) (o))->ob_type->tp_name)

/*****************************************************************************
 * GLOBAL VARIABLES
 *****************************************************************************/

#ifndef __LIBLDAP_DARWIN__
PyObject *LibLDAPErr;
#endif

/*****************************************************************************
 * GLOBAL FUNCTION DECLARATIONS
 *****************************************************************************/

void LibLDAP_value_free(void **);

#endif /* LIBLDAP_H */
