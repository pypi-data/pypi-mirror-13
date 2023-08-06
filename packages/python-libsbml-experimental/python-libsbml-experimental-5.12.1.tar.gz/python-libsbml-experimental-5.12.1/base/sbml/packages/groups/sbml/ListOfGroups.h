/**
 * @file ListOfGroups.h
 * @brief Definition of the ListOfGroups class.
 * @author SBMLTeam
 *
 * <!--------------------------------------------------------------------------
 * This file is part of libSBML. Please visit http://sbml.org for more
 * information about SBML, and the latest version of libSBML.
 *
 * Copyright (C) 2013-2016 jointly by the following organizations:
 * 1. California Institute of Technology, Pasadena, CA, USA
 * 2. EMBL European Bioinformatics Institute (EMBL-EBI), Hinxton, UK
 * 3. University of Heidelberg, Heidelberg, Germany
 *
 * Copyright (C) 2009-2013 jointly by the following organizations:
 * 1. California Institute of Technology, Pasadena, CA, USA
 * 2. EMBL European Bioinformatics Institute (EMBL-EBI), Hinxton, UK
 *
 * Copyright (C) 2006-2008 by the California Institute of Technology,
 * Pasadena, CA, USA
 *
 * Copyright (C) 2002-2005 jointly by the following organizations:
 * 1. California Institute of Technology, Pasadena, CA, USA
 * 2. Japan Science and Technology Agency, Japan
 *
 * This library is free software; you can redistribute it and/or modify it
 * under the terms of the GNU Lesser General Public License as published by the
 * Free Software Foundation. A copy of the license agreement is provided in the
 * file named "LICENSE.txt" included with this software distribution and also
 * available online as http://sbml.org/software/libsbml/license.html
 * ------------------------------------------------------------------------ -->
 *
 * @class ListOfGroups
 * @sbmlbrief{groups} TODO:Definition of the ListOfGroups class.
 */


#ifndef ListOfGroups_H__
#define ListOfGroups_H__


#include <sbml/common/extern.h>
#include <sbml/common/sbmlfwd.h>
#include <sbml/packages/groups/common/groupsfwd.h>


#ifdef __cplusplus


#include <string>


#include <sbml/ListOf.h>
#include <sbml/packages/groups/extension/GroupsExtension.h>
#include <sbml/packages/groups/sbml/Group.h>


LIBSBML_CPP_NAMESPACE_BEGIN


class LIBSBML_EXTERN ListOfGroups : public ListOf
{

public:

  /**
   * Creates a new ListOfGroups using the given SBML Level, Version and
   * &ldquo;groups&rdquo; package version.
   *
   * @param level an unsigned int, the SBML Level to assign to this
   * ListOfGroups
   *
   * @param version an unsigned int, the SBML Version to assign to this
   * ListOfGroups
   *
   * @param pkgVersion an unsigned int, the SBML Groups Version to assign to
   * this ListOfGroups
   *
   * @throws SBMLConstructorException
   * Thrown if the given @p level and @p version combination, or this kind of
   * SBML object, are either invalid or mismatched with respect to the parent
   * SBMLDocument object.
   * @copydetails doc_note_setting_lv
   */
  ListOfGroups(unsigned int level = GroupsExtension::getDefaultLevel(),
               unsigned int version = GroupsExtension::getDefaultVersion(),
               unsigned int pkgVersion =
                 GroupsExtension::getDefaultPackageVersion());


  /**
   * Creates a new ListOfGroups using the given GroupsPkgNamespaces object.
   *
   * @param groupsns the GroupsPkgNamespaces object
   *
   * @throws SBMLConstructorException
   * Thrown if the given @p level and @p version combination, or this kind of
   * SBML object, are either invalid or mismatched with respect to the parent
   * SBMLDocument object.
   * @copydetails doc_note_setting_lv
   */
  ListOfGroups(GroupsPkgNamespaces *groupsns);


  /**
   * Copy constructor for ListOfGroups.
   *
   * @param orig; the ListOfGroups instance to copy.
   */
  ListOfGroups(const ListOfGroups& orig);


  /**
   * Assignment operator for ListOfGroups.
   *
   * @param rhs; the ListOfGroups object whose values are to be used as the
   * basis of the assignment
   */
  ListOfGroups& operator=(const ListOfGroups& rhs);


  /**
   * Creates and returns a deep copy of this ListOfGroups object.
   *
   * @return a (deep) copy of this ListOfGroups object.
   */
  virtual ListOfGroups* clone() const;


  /**
   * Destructor for ListOfGroups.
   */
  virtual ~ListOfGroups();


  /**
   * Get a Group from the ListOfGroups.
   *
   * @param n, an unsigned int representing the index of the Group to retrieve.
   *
   * @return the nth Group in this ListOfGroups.
   *
   * @see size()
   */
  virtual Group* get(unsigned int n);


  /**
   * Get a Group from the ListOfGroups.
   *
   * @param n, an unsigned int representing the index of the Group to retrieve.
   *
   * @return the nth Group in this ListOfGroups.
   *
   * @see size()
   */
  virtual const Group* get(unsigned int n) const;


  /**
   * Get a Group from the ListOfGroups based on its identifier.
   *
   * @param sid a string representing the identifier of the Group to retrieve.
   *
   * @return the Group in this ListOfGroups with the given id or NULL if no
   * such Group exists.
   *
   * @see size()
   */
  virtual Group* get(const std::string& sid);


  /**
   * Get a Group from the ListOfGroups based on its identifier.
   *
   * @param sid a string representing the identifier of the Group to retrieve.
   *
   * @return the Group in this ListOfGroups with the given id or NULL if no
   * such Group exists.
   *
   * @see size()
   */
  virtual const Group* get(const std::string& sid) const;


  /**
   * Removes the nth Group from this ListOfGroups and returns a pointer to it.
   *
   * @param n, an unsigned int representing the index of the Group to remove.
   *
   * @return a pointer to the nth Group in this ListOfGroups.
   *
   * @see size()
   *
   * @note the caller owns the returned object and is responsible for deleting
   * it.
   */
  virtual Group* remove(unsigned int n);


  /**
   * Removes the Group from this ListOfGroups based on its identifier and
   * returns a pointer to it.
   *
   * @param sid, a string representing the identifier of the Group to remove.
   *
   * @return the Group in this ListOfGroups based on the identifier or NULL if
   * no such Group exists.
   *
   * @note the caller owns the returned object and is responsible for deleting
   * it.
   */
  virtual Group* remove(const std::string& sid);


  /**
   * Adds a copy of the given Group to this ListOfGroups.
   *
   * @param g, the Group object to add.
   *
   * @copydetails doc_returns_success_code
   * @li @sbmlconstant{LIBSBML_OPERATION_SUCCESS, OperationReturnValues_t}
   * @li @sbmlconstant{LIBSBML_OPERATION_FAILED, OperationReturnValues_t}
   *
   * @copydetails doc_note_object_is_copied
   *
   * @see createGroup()
   */
  int addGroup(const Group* g);


  /**
   * Get the number of Group objects in this ListOfGroups.
   *
   * @return the number of Group objects in this ListOfGroups.
   */
  unsigned int getNumGroups() const;


  /**
   * Creates a new Group object, adds it to this ListOfGroups object and
   * returns the Group object created.
   *
   * @return a new Group object instance.
   *
   * @see addGroup(const Group* g)
   */
  Group* createGroup();


  /**
   * Returns the XML element name of this ListOfGroups object.
   *
   * For ListOfGroups, the XML element name is always @c "listOfGroups".
   *
   * @return the name of this element, i.e. @c "listOfGroups".
   */
  virtual const std::string& getElementName() const;


  /**
   * Returns the libSBML type code for this ListOfGroups object.
   *
   * @copydetails doc_what_are_typecodes
   *
   * @return the SBML type code for this object:
   *
   * @sbmlconstant{SBML_LIST_OF, SBMLTypeCode_t}
   *
   * @copydetails doc_warning_typecodes_not_unique
   */
  virtual int getTypeCode() const;


  /**
   * Returns the libSBML type code for the SBML objects contained in this
   * ListOfGroups object.
   *
   * @copydetails doc_what_are_typecodes
   *
   * @return the SBML typecode for the objects contained in this ListOfGroups:
   *
   * @sbmlconstant{SBML_GROUPS_GROUP, SBMLGroupsTypeCode_t}
   *
   * @copydetails doc_warning_typecodes_not_unique
   *
   * @see getElementName()
   * @see getPackageName()
   */
  virtual int getItemTypeCode() const;


protected:


  /** @cond doxygenLibsbmlInternal */

  /**
   * Creates a new Group in this ListOfGroups
   */
  virtual SBase* createObject(XMLInputStream& stream);

  /** @endcond */



  /** @cond doxygenLibsbmlInternal */

  /**
   * Writes the namespace for the Groups package
   */
  virtual void writeXMLNS(XMLOutputStream& stream) const;

  /** @endcond */


};



LIBSBML_CPP_NAMESPACE_END




#endif /* __cplusplus */




#ifndef SWIG




LIBSBML_CPP_NAMESPACE_BEGIN




BEGIN_C_DECLS


/**
 * Get a Group_t from the ListOf_t.
 *
 * @param lo, the ListOf_t structure to search.
 *
 * @param n, an unsigned int representing the index of the Group_t to retrieve.
 *
 * @return the nth Group_t in this ListOf_t.
 *
 * @memberof Group_t
 */
LIBSBML_EXTERN
const Group_t*
ListOfGroups_getGroup(ListOf_t* lo, unsigned int n);


/**
 * Get a Group_t from the ListOf_t based on its identifier.
 *
 * @param lo, the ListOf_t structure to search.
 *
 * @param sid a string representing the identifier of the Group_t to retrieve.
 *
 * @return the Group_t in this ListOf_t with the given id or NULL if no such
 * Group_t exists.
 *
 * @memberof Group_t
 */
LIBSBML_EXTERN
const Group_t*
ListOfGroups_getById(ListOf_t* lo, const char *sid);


/**
 * Removes the nth Group_t from this ListOf_t and returns a pointer to it.
 *
 * @param lo, the ListOf_t structure to search.
 *
 * @param n, an unsigned int representing the index of the Group_t to remove.
 *
 * @return a pointer to the nth Group_t in this ListOf_t.
 *
 * @memberof Group_t
 */
LIBSBML_EXTERN
Group_t*
ListOfGroups_remove(ListOf_t* lo, unsigned int n);


/**
 * Removes the Group_t from this ListOf_t based on its identifier and returns a
 * pointer to it.
 *
 * @param lo, the ListOf_t structure to search.
 *
 * @param sid, a string representing the identifier of the Group_t to remove.
 *
 * @return the Group_t in this ListOf_t based on the identifier or NULL if no
 * such Group_t exists.
 *
 * @memberof Group_t
 */
LIBSBML_EXTERN
Group_t*
ListOfGroups_removeById(ListOf_t* lo, const char* sid);




END_C_DECLS




LIBSBML_CPP_NAMESPACE_END




#endif /* !SWIG */




#endif /* !ListOfGroups_H__ */


