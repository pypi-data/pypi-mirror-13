/**
 * @file GroupsModelPlugin.h
 * @brief Definition of the GroupsModelPlugin class.
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
 * @class GroupsModelPlugin
 * @sbmlbrief{groups} Extension of Model.
 */


#ifndef GroupsModelPlugin_H__
#define GroupsModelPlugin_H__


#include <sbml/common/extern.h>


#ifdef __cplusplus


#include <sbml/extension/SBasePlugin.h>
#include <sbml/packages/groups/sbml/ListOfGroups.h>
#include <sbml/packages/groups/sbml/Group.h>


LIBSBML_CPP_NAMESPACE_BEGIN


class LIBSBML_EXTERN GroupsModelPlugin : public SBasePlugin
{
protected:

  /** @cond doxygenLibsbmlInternal */

  ListOfGroups mGroups;

  /** @endcond */

public:

  /**
   * Creates a new GroupsModelPlugin using the given uri, prefix and package
   * namespace.
   *
   * @param uri a string, representing the uri of the package
   *
   * @param prefix a string, the prefix to be used
   *
   * @param groupsns, a pointer to the GroupsPkgNamespaces object to be used
   */
  GroupsModelPlugin(const std::string& uri,
                    const std::string& prefix,
                    GroupsPkgNamespaces* groupsns);


  /**
   * Copy constructor for GroupsModelPlugin.
   *
   * @param orig; the GroupsModelPlugin instance to copy.
   */
  GroupsModelPlugin(const GroupsModelPlugin& orig);


  /**
   * Assignment operator for GroupsModelPlugin.
   *
   * @param rhs; the GroupsModelPlugin object whose values are to be used as
   * the basis of the assignment
   */
  GroupsModelPlugin& operator=(const GroupsModelPlugin& rhs);


  /**
   * Creates and returns a deep copy of this GroupsModelPlugin object.
   *
   * @return a (deep) copy of this GroupsModelPlugin object.
   */
  virtual GroupsModelPlugin* clone() const;


  /**
   * Destructor for GroupsModelPlugin.
   */
  virtual ~GroupsModelPlugin();


  /**
   * Returns the ListOfGroups from this GroupsModelPlugin.
   *
   * @return the ListOfGroups from this GroupsModelPlugin.
   */
  const ListOfGroups* getListOfGroups() const;


  /**
   * Returns the ListOfGroups from this GroupsModelPlugin.
   *
   * @return the ListOfGroups from this GroupsModelPlugin.
   */
  ListOfGroups* getListOfGroups();


  /**
   * Get a Group from the GroupsModelPlugin.
   *
   * @param n, an unsigned int representing the index of the Group to retrieve.
   *
   * @return the nth Group in the ListOfGroups within this GroupsModelPlugin.
   *
   * @see getNumGroups()
   */
  Group* getGroup(unsigned int n);


  /**
   * Get a Group from the GroupsModelPlugin.
   *
   * @param n, an unsigned int representing the index of the Group to retrieve.
   *
   * @return the nth Group in the ListOfGroups within this GroupsModelPlugin.
   *
   * @see getNumGroups()
   */
  const Group* getGroup(unsigned int n) const;


  /**
   * Get a Group from the GroupsModelPlugin based on its identifier.
   *
   * @param sid a string representing the identifier of the Group to retrieve.
   *
   * @return the Group in the ListOfGroups within this GroupsModelPlugin with
   * the given id or NULL if no such Group exists.
   *
   * @see getGroup(unsigned int n)
   * @see getNumGroups()
   */
  Group* getGroup(const std::string& sid);


  /**
   * Get a Group from the GroupsModelPlugin based on its identifier.
   *
   * @param sid a string representing the identifier of the Group to retrieve.
   *
   * @return the Group in the ListOfGroups within this GroupsModelPlugin with
   * the given id or NULL if no such Group exists.
   *
   * @see getGroup(unsigned int n)
   * @see getNumGroups()
   */
  const Group* getGroup(const std::string& sid) const;


  /**
   * Adds a copy of the given Group to this GroupsModelPlugin.
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
   * Get the number of Group objects in this GroupsModelPlugin.
   *
   * @return the number of Group objects in this GroupsModelPlugin.
   */
  unsigned int getNumGroups() const;


  /**
   * Creates a new Group object, adds it to this GroupsModelPlugin object and
   * returns the Group object created.
   *
   * @return a new Group object instance.
   *
   * @see addGroup(const Group* g)
   */
  Group* createGroup();


  /**
   * Removes the nth Group from this GroupsModelPlugin and returns a pointer to
   * it.
   *
   * @param n, an unsigned int representing the index of the Group to remove.
   *
   * @return a pointer to the nth Group in this GroupsModelPlugin.
   *
   * @see getNumGroups
   *
   * @note the caller owns the returned object and is responsible for deleting
   * it.
   */
  Group* removeGroup(unsigned int n);


  /**
   * Removes the Group from this GroupsModelPlugin based on its identifier and
   * returns a pointer to it.
   *
   * @param sid, a string representing the identifier of the Group to remove.
   *
   * @return the Group in this GroupsModelPlugin based on the identifier or
   * NULL if no such Group exists.
   *
   * @note the caller owns the returned object and is responsible for deleting
   * it.
   */
  Group* removeGroup(const std::string& sid);


  /**
   * Predicate returning @c true if all the required elements for this
   * GroupsModelPlugin object have been set.
   *
   * @return @c true to indicate that all the required elements of this
   * GroupsModelPlugin have been set, otherwise @c false is returned.
   *
   *
   * @note The required elements for the GroupsModelPlugin object are:
   */
  virtual bool hasRequiredElements() const;



  /** @cond doxygenLibsbmlInternal */

  /**
   * Write any contained elements
   */
  virtual void writeElements(XMLOutputStream& stream) const;

  /** @endcond */



  /** @cond doxygenLibsbmlInternal */

  /**
   * Accepts the given SBMLVisitor
   */
  virtual bool accept(SBMLVisitor& v) const;

  /** @endcond */



  /** @cond doxygenLibsbmlInternal */

  /**
   * Sets the parent SBMLDocument
   */
  virtual void setSBMLDocument(SBMLDocument* d);

  /** @endcond */



  /** @cond doxygenLibsbmlInternal */

  /**
   * Connects to child elements
   */
  virtual void connectToChild();

  /** @endcond */



  /** @cond doxygenLibsbmlInternal */

  /**
   * Connects to parent element
   */
  virtual void connectToParent(SBase* base);

  /** @endcond */



  /** @cond doxygenLibsbmlInternal */

  /**
   * Enables/disables the given package with this element
   */
  virtual void enablePackageInternal(const std::string& pkgURI,
                                     const std::string& pkgPrefix,
                                     bool flag);

  /** @endcond */


  /**
   * Returns the first child element that has the given @p id in the model-wide
   * SId namespace, or @c NULL if no such object is found.
   *
   * @param id a string representing the id attribute of the object to
   * retrieve.
   *
   * @return a pointer to the SBase element with the given @p id.
   */
  virtual SBase* getElementBySId(const std::string& id);


  /**
   * Returns the first child element that has the given @p metaid, or @c NULL
   * if no such object is found.
   *
   * @param metaid a string representing the metaid attribute of the object to
   * retrieve.
   *
   * @return a pointer to the SBase element with the given @p metaid.
   */
  virtual SBase* getElementByMetaId(const std::string& metaid);


  /**
   * Returns a List of all child SBase objects, including those nested to an
   * arbitrary depth.
   *
   * filter, an ElementFilter that may impose restrictions on the objects to be
   * retrieved.
   *
   * @return a List* pointer of pointers to all SBase child objects with any
   * restriction imposed.
   */
  virtual List* getAllElements(ElementFilter * filter = NULL);



  /**
   * For nested groups (Member objects that reference a ListOfMembers 
   * object), SBO terms, Notes, and Annotation from the
   * parent ListOfMembers applies to the child.  This function
   * copies any information from any of those three things to all 
   * child ListOfMembers, and if that information is not already 
   * set.  After calling
   * this function, it is sufficient to check any ListOfMembers
   * to see if its SBO term, Notes, or Annotation is set, without
   * further checking to see if that element was nested in another
   * Group.
   */
  virtual void copyInformationToNestedLists();



  /** @cond doxygenLibsbmlInternal */

  /**
   * Append items from model (used in comp flattening)
   *
   * @param model a pointer to a model object
   *
   */
  int appendFrom(const Model* model);

  /** @endcond */


protected:


  /** @cond doxygenLibsbmlInternal */

  /**
   * Creates a new object from the next XMLToken on the XMLInputStream
   */
  virtual SBase* createObject(XMLInputStream& stream);

  /** @endcond */


};



LIBSBML_CPP_NAMESPACE_END




#endif /* __cplusplus */




#endif /* !GroupsModelPlugin_H__ */


