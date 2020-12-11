#!/usr/bin/env python
#SETMODE 777

#----------------------------------------------------------------------------------------#
#------------------------------------------------------------------------------ HEADER --#

"""
:author:
    Blake Day & Nick Lormand

:synopsis:
    a bunch of utils used throughout the auto_rigger

:description:
    a function to make parent constraints, point constraint, orient constraint,
    scale constraint, move obj to another obj, orient joints, create box controls,
    create circle controls, create arrow controls, create star controls, creates finger
    controls, creates foot control, creates fake joints and connectors, create buffers for
    maya objs, changes shape colors, mirrors objs, rename objs, makes objs display as
    template, lock and unlock channels, places pole vectors, makes and ik fk switch,
    makes fk controls, create the hierarchy, replace fake joints with real joints,
    get the joint list out of the maya scene

:applications:
    Maya

:see_also:
    step_one
    step_two
    step_three
    maya_enums
    auto_rig_gui
"""

#----------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------- IMPORTS --#

# Default Python Imports
import maya.cmds as cmds
from maya import OpenMaya as om
import math

# Imports That You Wrote
from maya_enums import MayaCommandEnums, NamingConventionEnums
#----------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------- FUNCTIONS --#
# parent constraint
def parent_const(parent_obj, child_obj, const_name, maintain_offset=False, tx=True,
                 ty=True, tz=True, rx=True, ry=True, rz=True):
    """
    This function creates a parent constraint on the given objects with the given params

    :param parent_obj: name of the parent object
    :type: str

    :param child_obj: name of the child object
    :type: str

    :param const_name: name of the constraint after its created
    :type: str

    :param maintain_offset: bool to have maintain offset on or off. defaults False (off)
    :type: bool

    :param tx: bool to include translate x in the constraint. default on
    :type: bool

    :param ty: bool to include translate y in the constraint. default on
    :type: bool

    :param tz: bool to include translate z in the constraint. default on
    :type: bool

    :param rx: bool to include rotate x in the constraint. default on
    :type: bool

    :param ry: bool to include rotate y in the constraint. default on
    :type: bool

    :param rz: bool to include rotate z in the constraint. default on
    :type: bool
    """
    # checks to see if any of the individual channels are off
    if tx and ty and tz and rx and ry and rz:
        #makes constraint with all of the channels on
        cmds.parentConstraint(parent_obj, child_obj, maintainOffset=maintain_offset,
                              name=const_name)
    else:
        #checks to see which channels are off and creates a string to_run of the command
        # with the skip flags
        to_run = 'cmds.parentConstraint(parent_obj, child_obj, maintainOffset = ' \
                 'maintain_offset, name = const_name'
        if not tx:
            to_run += ', skipTranslate = \'x\''
        if not ty:
            to_run += ', skipTranslate = \'y\''
        if not tz:
            to_run += ', skipTranslate = \'z\''
        if not rx:
            to_run += ', skipRotate = \'x\''
        if not ry:
            to_run += ', skipRotate = \'y\''
        if not rz:
            to_run += ', skipRotate = \'z\''
        to_run += ')'
        exec (to_run)

# point constraint
def point_const(parent_obj, child_obj, const_name, maintain_offset=False, tx=True,
                ty=True, tz=True):
    """
    This function creates a point constraint on the given objects with the given params

    :param parent_obj: name of the parent object
    :type: str

    :param child_obj: name of the child object
    :type: str

    :param const_name: name of the constraint after its created
    :type: str

    :param maintain_offset: bool to have maintain offset on or off. defaults False (off)
    :type: bool

    :param tx: bool to include translate x in the constraint. default on
    :type: bool

    :param ty: bool to include translate y in the constraint. default on
    :type: bool

    :param tz: bool to include translate z in the constraint. default on
    :type: bool
    """
    # checks to see if any of the individual channels are off
    if tx and ty and tz:
        # makes constraint with all of the channels on
        cmds.pointConstraint(parent_obj, child_obj, maintainOffset=maintain_offset,
                             name=const_name)
    else:
        # checks to see which channels are off and creates a string to_run of the command
        # with the skip flags
        to_run = 'cmds.pointConstraint(parent_obj, child_obj, maintainOffset = ' \
                 'maintain_offset, name = const_name'
        if not tx:
            to_run += ', skip = \'x\''
        if not ty:
            to_run += ', skip = \'y\''
        if not tz:
            to_run += ', skip = \'z\''
        to_run += ')'
        exec (to_run)

# aim constraint
def aim_const(parent_obj, child_obj, const_name, aimVector = (1,0,0), upVector = (0,1,0),
              worldUpType = None, worldUpObject = None,
              maintain_offset=False, tx=True, ty=True, tz=True):
    """
    This function creates an aim constraint on the given objects with the given params

    :param parent_obj: name of the parent object
    :type: str

    :param child_obj: name of the child object
    :type: str

    :param const_name: name of the constraint after its created
    :type: str

    :param maintain_offset: bool to have maintain offset on or off. defaults False (off)
    :type: bool

    :param tx: bool to include translate x in the constraint. default on
    :type: bool

    :param ty: bool to include translate y in the constraint. default on
    :type: bool

    :param tz: bool to include translate z in the constraint. default on
    :type: bool
    """
    # checks to see if any of the individual channels are off
    if tx and ty and tz:
        if worldUpObject and worldUpType:
            # makes constraint with all of the channels on
            cmds.aimConstraint(parent_obj, child_obj, aimVector = aimVector,
                           maintainOffset=maintain_offset, name=const_name,
                           upVector = upVector, worldUpType = worldUpType,
                           worldUpObject = worldUpObject)
        else:
            cmds.aimConstraint(parent_obj, child_obj, aimVector=aimVector,
                               maintainOffset=maintain_offset, name=const_name,
                               upVector=upVector, worldUpType='vector',
                               worldUpVector=(0,1,0))
    else:
        # checks to see which channels are off and creates a string to_run of the command
        # with the skip flags
        to_run = 'cmds.aimConstraint(parent_obj, child_obj, maintainOffset = ' \
                 'maintain_offset, name = const_name, upVector = upVector, ' \
                 'worldUpType = worldUpType, worldUpObject = worldUpObject'
        if not tx:
            to_run += ', skip = \'x\''
        if not ty:
            to_run += ', skip = \'y\''
        if not tz:
            to_run += ', skip = \'z\''
        to_run += ')'
        exec (to_run)

# orient constraint
def orient_const(parent_obj, child_obj, const_name, maintain_offset=False, rx=True,
                 ry=True, rz=True):
    """
     This function creates a point constraint on the given objects with the given params

    :param parent_obj: name of the parent object
    :type: str

    :param child_obj: name of the child object
    :type: str

    :param const_name: name of the constraint after its created
    :type: str

    :param maintain_offset: bool to have maintain offset on or off. defaults False (off)
    :type: bool

    :param rx: bool to include rotate x in the constraint. default on
    :type: bool

    :param ry: bool to include rotate y in the constraint. default on
    :type: bool

    :param rz: bool to include rotate z in the constraint. default on
    :type: bool
    """
    # checks to see if any of the individual channels are off
    if rx and ry and rz:
        # makes constraint with all of the channels on
        cmds.orientConstraint(parent_obj, child_obj, maintainOffset=maintain_offset,
                              name=const_name)
    else:
        # checks to see which channels are off and creates a string to_run of the command
        # with the skip flags
        to_run = 'cmds.orientConstraint(parent_obj, child_obj, maintainOffset = ' \
                 'maintain_offset, name = const_name'
        if not rx:
            to_run += ', skip = \'x\''
        if not ry:
            to_run += ', skip = \'y\''
        if not rz:
            to_run += ', skip = \'z\''
        to_run += ')'
        exec (to_run)

# scale constraint
def scale_const(parent_obj, child_obj, const_name, maintain_offset=False, sx=True,
                sy=True, sz=True):
    """
     This function creates a point constraint on the given objects with the given params

    :param parent_obj: name of the parent object
    :type: str

    :param child_obj: name of the child object
    :type: str

    :param const_name: name of the constraint after its created
    :type: str

    :param maintain_offset: bool to have maintain offset on or off. defaults False (off)
    :type: bool

    :param sx: bool to include rotate x in the constraint. default on
    :type: bool

    :param sy: bool to include rotate y in the constraint. default on
    :type: bool

    :param sz: bool to include rotate z in the constraint. default on
    :type: bool
    """
    # checks to see if any of the individual channels are off
    if sx and sy and sz:
        # makes constraint with all of the channels on
        cmds.scaleConstraint(parent_obj, child_obj, maintainOffset=maintain_offset,
                             name=const_name)
    else:
        # checks to see which channels are off and creates a string to_run of the command
        # with the skip flags
        to_run = 'cmds.scaleConstraint(parent_obj, child_obj, maintainOffset = ' \
                 'maintain_offset, name = const_name'
        if not sx:
            to_run += ', skip = \'x\''
        if not sy:
            to_run += ', skip = \'y\''
        if not sz:
            to_run += ', skip = \'z\''
        to_run += ')'
        exec (to_run)

# move onto
def place_on(to_move_obj, target_obj, scale = False):
    """
    moves an object to the same position as another object by making a parent constraint
    and deleting the constraint right after

    :param to_move_obj: name of the object to move
    :type: str

    :param target_obj: name of the object to move to
    :type: str
    """
    #makes a parent constraint with maintain offset off to move the object then deletes
    # constraint
    parent_const(target_obj, to_move_obj, 'temp_const')
    cmds.delete('temp_const')
    if scale:
        scale_const(target_obj, to_move_obj, 'temp_const')
        cmds.delete('temp_const')




def orient_joints(root_jnt, main_axis, secondary_axis, extra_axis, secondary_axis_orient):
    """
    orients joints based off the given info

    :param root_jnt: name of the root joint of the hierarchy being oriented
    :type: str

    :param main_axis: the axis that will point to the next joint. will be 'x' 'y' or 'z'
    :type: str

    :param secondary_axis: secondary axis to orient. will be 'x' 'y' or 'z'
    :type: str

    :param extra_axis: the remaining axis. will be 'x' 'y' or 'z'
    :type: str

    :param secondary_axis_orient: direction to orient secondary axis.
        will be 'xup' 'xdown' 'yup' 'ydown' 'zup' or 'zdown'
    :type: str
    """
    #check to make sure each axis is unique, if any arent then exit the function
    if (main_axis == secondary_axis or main_axis == extra_axis or
            secondary_axis == extra_axis):
        return None

    #if the axis are all unique then make a string of all three -> 'xyz'
    orient = main_axis + secondary_axis + extra_axis

    #check the that secondary_axis_orient is an acceptable str
    if (secondary_axis_orient == 'xup' or secondary_axis_orient == 'xdown' or
            secondary_axis_orient == 'yup' or secondary_axis_orient == 'ydown' or
            secondary_axis_orient == 'zup' or secondary_axis_orient == 'zdown'):
        #runs the joint command in edit mode and uses the inputs to orient joints
        cmds.joint(root_jnt, edit=True, orientJoint=orient,
                   secondaryAxisOrient=secondary_axis_orient, children=True,
                   zeroScaleOrient=True)



def create_box(obj_name):
    """
    Creates a curve box at the origin with the given name

    :param obj_name: name of the box
    :type: str
    """
    #uses curve command to make the box
    cmds.curve(degree=1, point=[(0.5, 0.5, 0.5), (-0.5, 0.5, 0.5), (-0.5, 0.5, -0.5),
                                (0.5, 0.5, -0.5), (0.5, 0.5, 0.5), (0.5, -0.5, 0.5),
                                (0.5, -0.5, -0.5), (0.5, 0.5, -0.5), (0.5, 0.5, 0.5),
                                (0.5, -0.5, 0.5), (-0.5, -0.5, 0.5), (-0.5, 0.5, 0.5),
                                (-0.5, -0.5, 0.5), (-0.5, -0.5, -0.5), (-0.5, 0.5, -0.5),
                                (-0.5, -0.5, -0.5), (0.5, -0.5, -0.5)],
               knot=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16],
               name=obj_name)
    cmds.xform(obj_name, absolute=True, scale=[3,3,3])

    # adds the globabl attr
    cmds.addAttr('|' + obj_name, longName=NamingConventionEnums.GLOBAL_ATTR_NAME,
                 attributeType='bool')
    #clear history
    cmds.select(obj_name)
    cmds.DeleteHistory()
    return obj_name

def create_foot_CC(obj_name):
    """
    Creates a curve foot controller at the origin with the given name

    :param obj_name: name of the controller
    :type: str
    """
    #uses curve command to make the box
    cmds.curve(degree=1, point=[(0.5, 0.5, 0.5), (-0.5, 0.5, 0.5), (-0.5, 0.5, -0.5),
                                (0.5, 0.5, -0.5), (0.5, 0.5, 0.5), (0.5, -0.5, 0.5),
                                (0.5, -0.5, -0.5), (0.5, 0.5, -0.5), (0.5, 0.5, 0.5),
                                (0.5, -0.5, 0.5), (-0.5, -0.5, 0.5), (-0.5, 0.5, 0.5),
                                (-0.5, -0.5, 0.5), (-0.5, -0.5, -0.5), (-0.5, 0.5, -0.5),
                                (-0.5, -0.5, -0.5), (0.5, -0.5, -0.5)],
               knot=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16],
               name=obj_name)
    cmds.xform(obj_name, absolute=True, scale=[4,3,10])

    cmds.select(obj_name + '.cv[0:1]',obj_name+".cv[4:5]", obj_name+".cv[8:12]")
    cmds.xform(scale=[.6, 1, 1], relative=True)
    cmds.select(obj_name + '.cv[0:1]', obj_name + ".cv[4]", obj_name + ".cv[8]",
                obj_name + ".cv[11]")
    cmds.xform(translation=[0, -.55, 0], relative=True)

    cmds.select(obj_name)
    cmds.xform(obj_name, relative=True, scale=[1.5, 1.5, 1.5])
    #cmds.xform(obj_name, absolute=True, rotation=[0, 0, 0])
    #cmds.xform(obj_name, a=True, t=[2, 0, 0])
    cmds.makeIdentity(obj_name, apply=True,translate=True, rotate=True,scale=True)

    # adds the globabl attr
    cmds.addAttr('|' + obj_name, longName=NamingConventionEnums.GLOBAL_ATTR_NAME,
                 attributeType='bool')
    #clear history
    cmds.select(obj_name)
    cmds.DeleteHistory()
    return obj_name

def create_circle(obj_name, normal_x=0, normal_y=0, normal_z=0):
    """
    creates a nurbs circle with the given name and normal axis.

    :param obj_name: name of the circle
    :type: str

    :param normal_x: normal in the x direction
    :type: int

    :param normal_y: normal in the y direction
    :type: int

    :param normal_z: normal in the z direction
    :type: int
    """
    # creates circle at the origin with the normal facing the given direction and named
    cmds.circle(normal=(normal_x, normal_y, normal_z), center=(0, 0, 0), name=obj_name)

    # adds the globabl attr
    cmds.addAttr('|' + obj_name, longName=NamingConventionEnums.GLOBAL_ATTR_NAME,
                 attributeType='bool')

    cmds.xform(scale = (3,3,3))

    cmds.makeIdentity(obj_name, apply=True, translate=True, rotate=True, scale=True,
                      normal=False, preserveNormals=1)
    #clear history
    cmds.select(obj_name)
    cmds.DeleteHistory()
    return obj_name

def create_finger_tweaker(obj_name):
    """
    creates a finger tweaker shape

    :param obj_name: what to name the tweaker
    :type: str
    """
    # makes and moves a circle a little bit off origin
    circ = cmds.circle(center=[0, 0, 0], normal=[1, 0, 0], sweep=360, radius=.5,
                       degree=3, useTolerance=0, tolerance=0, sections=8, caching=1)[0]
    cmds.select(circ + '.cv[0:7]')
    cmds.xform(translation=[0, 2, 0], relative=True)
    cmds.xform(absolute=True, worldSpace=True, pivots=[0, 0, 0])
    cmds.makeIdentity(circ, apply=True, translate=True, rotate=True, scale=True,
                      normal=False, preserveNormals=1)
    # cmds.makeIdentity(apply=True, t=1, r=1, s=1, n=0, pn=1)

    # makes a line from origin to circle
    line = cmds.curve(degree=1, point=[(0, 0, 0), (0, 1.5, 0)], knot=[0, 1])

    # gets the shape nodes of the line and circle
    shapes = cmds.listRelatives([circ, line], shapes=True)

    # creates an empty group and parents the shape nodes to it
    grp = cmds.group(empty=True, name=obj_name)
    cmds.parent(shapes, grp, add=True, shape=True, relative=True)

    cmds.delete(circ, line)
    #clear history
    cmds.select(obj_name)
    cmds.DeleteHistory()

    # adds the globabl attr
    cmds.addAttr('|' + obj_name, longName=NamingConventionEnums.GLOBAL_ATTR_NAME,
                 attributeType='bool')

def create_star_control(obj_name):
    """
    creates a 4 point star shape curve

    :param obj_name: what to name the control
    :type: str
    """
    create_circle(obj_name, normal_x=1)
    cmds.select(obj_name+".cv[0]", obj_name+".cv[2]",
                obj_name+".cv[4]",obj_name+".cv[6]")
    cmds.scale(0.19, 0.19, 0.19, relative= True)
    cmds.select(clear=True)
    cmds.xform(obj_name, scale = (1.27, 1.27, 1.27))
    cmds.select(obj_name)
    cmds.xform(scale=(3, 3, 3))
    cmds.makeIdentity(obj_name, apply=True, translate=True, rotate=True, scale=True,
                      normal=False, preserveNormals=1)
    cmds.makeIdentity(apply=True, translate=1, rotate=1, scale=1, normal=0, pn=1)
    #clear history
    cmds.select(obj_name)
    cmds.DeleteHistory()

def create_four_point_arrow(obj_name):
    """
    creates a 4 point arrow of the given name at the origin
    :param obj_name: name of the arrow
    :type: str
    """
    cmds.curve(degree=1,
               point=[(-1, 0, -2), (-2, 0, -2), (0, 0, -4), (2, 0, -2), (1, 0, -2),
                      (1, 0, 0),(3, 0, 0), (3, 0, -1), (5, 0, 1), (3, 0, 3), (3, 0, 2),
                      (1, 0, 2), (1, 0, 4), (2, 0, 4), (0, 0, 6), (-2, 0, 4), (-1, 0, 4),
                      (-1, 0, 2),(-3, 0, 2), (-3, 0, 3), (-5, 0, 1), (-3, 0, -1),
                      (-3, 0, 0), (-1, 0, 0), (-1, 0, -2)],
            knot=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19,
                  20, 21, 22, 23, 24], name = obj_name)
    cmds.CenterPivot()
    cmds.xform(relative=True, translation=(0, 0, -1), scale= (10, 10, 10))
    cmds.makeIdentity(obj_name, apply=True, translate=True, rotate=True, scale=True,
                      normal=False, preserveNormals=1)

    # adds the globabl attr
    cmds.addAttr('|' + obj_name, longName=NamingConventionEnums.GLOBAL_ATTR_NAME,
                 attributeType='bool')

def create_two_point_arrow(obj_name):
    """
    creates a 4 point arrow of the given name at the origin
    :param obj_name: name of the arrow
    :type: str
    """
    cmds.curve(degree=1, point=[(-4, 0, 0), (-2, 2, 0), (-2, 1, 0), (2, 1, 0), (2, 2, 0),
                           (4, 0, 0), (2, -2, 0), (2, -1, 0), (-2, -1, 0), (-2, -2, 0),
                           (-4, 0, 0)], knot=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
              name = obj_name)

    cmds.CenterPivot()
    cmds.xform(relative=True, rotation = (90,0,90), scale= (3, 3, 3))
    cmds.makeIdentity(obj_name, apply=True, translate=True, rotate=True, scale=True,
                      normal=False, preserveNormals=1)

    # adds the globabl attr
    cmds.addAttr('|' + obj_name, longName=NamingConventionEnums.GLOBAL_ATTR_NAME,
                 attributeType='bool')

    return obj_name


def create_fake_joint( name, tx, ty, tz, rx, ry, rz):
    """
    creates a fake joint curve and adds it to the display layer
    :param name: name of the joint
    :param tx: translation value for x
    :param ty: translation value for y
    :param tz: translation value for z
    :return: name of the fake joint
    """
    # creates 3 nurbs circles and rotates them to look like a joint
    cmds.circle(normal=(0, 1, 0), center=(0, 0, 0))
    cmds.xform(absolute=True, translation=(tx, ty, tz))
    obj1 = cmds.ls(selection=True)
    cmds.circle(normal=(0, 0, 1), center=(0, 0, 0))
    cmds.xform(absolute=True, translation=(tx, ty, tz))
    obj2 = cmds.ls(selection=True)
    obj2shape = cmds.listRelatives(shapes=True)
    cmds.xform(absolute=True, translation=(tx, ty, tz))
    cmds.circle(normal=(1, 0, 0), center=(0, 0, 0))
    obj3 = cmds.ls(selection=True)
    obj3shape = cmds.listRelatives(shapes=True)

    # add shapes of two of the circles to the last one to make it one object
    cmds.parent(obj2shape, obj1, add=True, shape=True)
    cmds.parent(obj3shape, obj1, add=True, shape=True)

    # delete the leftover circles
    cmds.delete(obj2)
    cmds.delete(obj3)
    cmds.select(obj1, replace=True)
    # move the fake joint to the specified spot in the xml
    cmds.xform( absolute=True, rotation =(rx, ry, rz))
    cmds.rename(name)

    # adds the globabl attr
    cmds.addAttr('|' + name, longName = NamingConventionEnums.GLOBAL_ATTR_NAME,
                 attributeType = 'bool')

def create_connection_curve(parent_obj, child_obj):
    """
    creates a connection curve in the middle of two fake joints
    :param parent_obj: the parent joint
    :param child_obj: the child joint
    :return: name of the connection
    """
    cmds.curve(degree=1,
               point=[(0, -1, 1), (-5, 0, 0), (0, -1, -1), (1, 0, 0), (0, 1, -1),
                  (-5, 0, 0),  (0, 1, 1), (1, 0, 0), (0, -1, 1), (0, -1, -1), (0, 1, -1),
                  (0, 1, 1), (0, -1, 1)], knot=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])

    # rotate and freeze transforms
    #cmds.xform(r = True, ro = (0, 180, 0))
    #cmds.makeIdentity(apply=True, t=1, r=1, s=1, n=0)

    name = cmds.rename(parent_obj+"__"+child_obj)

    #adds the globabl attr
    cmds.addAttr('|'+name, longName=NamingConventionEnums.GLOBAL_ATTR_NAME,
                 attributeType='bool')

    # create clusters
    child_cluster =cmds.cluster(name+".cv[1]", name+".cv[5]", name=child_obj)
    child_name = child_cluster[1]

    parent_cluster =cmds.cluster(name+".cv[0]", name+".cv[2:4]", name+".cv[6:12]",
                                 name = parent_obj)
    parent_name = parent_cluster[1]

    # move pivot so the connection curve starts at the center of the parent joint
    cmds.xform(pivots=(1, 0, 0))

    # creates a locator to use for parenting the control curve
    # will only create the locator for the first
    locator_name = "%s_locator"%parent_obj
    sel = cmds.ls()
    make_locator = True
    for item in sel:
        if locator_name in item:
            make_locator = False

    if make_locator:
        cmds.spaceLocator(name = locator_name, position=(0, 0, 0))
        cmds.parent(locator_name, parent_name)
        cmds.xform(locator_name, translation = (1, 0,0))
        if locator_name.startswith(NamingConventionEnums.RIGHT):
            cmds.xform(locator_name, rotation = (0,0,180))

    # constrain clusters so that they connect the joints
    point_const(parent_obj, parent_name, parent_obj + "_point"
                +NamingConventionEnums.CONSTRAIN_SUFFIX)
    point_const(child_obj, child_name, parent_obj + "_point"
                +NamingConventionEnums.CONSTRAIN_SUFFIX)
    aim_const(child_obj, parent_name, parent_obj+"Handle"+"_aim"
              +NamingConventionEnums.CONSTRAIN_SUFFIX, [-1, 0, 0])

    # parent clusters to curve
    cmds.parent(parent_name, name)
    cmds.parent(child_name, name)

    # turn off visibility
    cmds.setAttr(parent_name + '.visibility', 0)
    cmds.setAttr(child_name + '.visibility', 0)

    # make template
    set_template(name)
    set_template(parent_name)
    set_template(child_name)

    return name

def set_color(selection, new_color):
    """
    sets the color of the shape node of the given item to the given color

    :param selection: name of the item to color
    :type: str or list

    :param new_color: color to make item
    :type: str
    """
    #checks the color and makes an int to put into the setAttr command
    if new_color.lower() == 'blue':
        color_index = 6
    elif new_color.lower() == 'red':
        color_index = 13
    elif new_color.lower() == 'green':
        color_index = 14
    elif new_color.lower() == 'yellow':
        color_index = 17

    #select the item
    sel = cmds.listRelatives(selection, shapes = True)

    #if given a list it converts all the items
    for item in sel:
        # Enable color override
        if cmds.getAttr((item + ".overrideEnabled")) == 0:
            cmds.setAttr((item + ".overrideEnabled"), 1)
        # Recolor curve/wireframe to Red
        cmds.setAttr((item + ".overrideColor"), color_index)

def mirror(to_mirror, axis, group_name, to_find, replace_with, mirror_space = 'w'):
    """
    mirrors the given objects across the given axis by grouping and scaling the group -1
    also renames the mirrored objects
    puts the mirrored object in a new group of name group_name
    :param to_mirror: the objects to mirror
    :type: str or list

    :param axis: axis to mirror across
    :type: str

    :param group_name: name of the group to place the mirrored objects in
    :type:str

    :param to_find: str to find and then replace
    :type: str

    :param replace_with: what to replace to_find with
    :type: str

    :param mirror_space: what pivot to mirror across, default world
    :type: str
    """
    #duplicates the objects and renames the children so they're unique with rc flag
    dupes = cmds.duplicate(to_mirror, renameChildren=True)
    #renames the duplicated objects
    renamed = find_replace_names(dupes, to_find, replace_with)
    #groups the duplicated objects and sets pivot to world origin
    if mirror_space == 'w':
        cmds.group(renamed, world=True, name=group_name)
    else:
        cmds.group(renamed, parent = mirror_space, name = group_name)
    cmds.xform(group_name, pivots = (0,0,0))
    #scales in -1 along the given axis to mirror
    cmds.setAttr((group_name + '.s' + axis), -1)

def find_replace_names(items, to_find, replace_with):
    """
    takes a list of objects and replaces to_find with replace_with in the names

    :param items: list of objects to rename
    :type: list

    :param to_find: str to find and then replace
    :type: str

    :param replace_with: what to replace to_find with
    :type: str

    :return: list with the new names
    """
    #creates the list that will be returned
    to_return = ['to_remove']
    #because how maya names things reverse the list so the top level is named last
    items.reverse()
    #loops through all the items
    for item in items:
        #splits the name on | because maya names things -> parent|child
        split_name = item.rsplit('|', 1)
        #uses .replace to make the new name
        temp_name = split_name[-1].replace(to_find, replace_with, 1)
        new_name = temp_name.rsplit('1', 1)[0]
        #calls rename command
        cmds.rename(item, new_name)
        #adds new name to the return list
        to_return.append(new_name)
    #returns the list and unreverses it
    to_return.remove('to_remove')
    to_return.reverse()
    return to_return

def set_template(obj_name):
    """
    sets the display type of the given object to template

    :param obj_name: name of obj to set to template
    :type: str
    """
    #select the shape nodes of the item
    sel = cmds.listRelatives(obj_name, shapes = True)

    #loops through all the shapes
    for item in sel:
        # Enable drawing override
        if cmds.getAttr((item + ".overrideEnabled")) == 0:
            cmds.setAttr((item + ".overrideEnabled"), 1)
        # sets it to template
        cmds.setAttr((item+".overrideDisplayType"), 1)

def toggle_template(obj_shape):
    """
    sets the display type of the given object to template

    :param obj_name: name of obj to set to template
    :type: str
    """
    # Enable drawing override
    if cmds.getAttr((obj_shape + ".overrideEnabled")) == 0:
        cmds.setAttr((obj_shape + ".overrideEnabled"), 1)
    # sets it to template if it is not already
    # else it will take it off template
    if cmds.getAttr((obj_shape + ".overrideDisplayType")) == 0:
        cmds.setAttr((obj_shape+".overrideDisplayType"), 1)
    elif cmds.getAttr((obj_shape + ".overrideDisplayType")) == 1:
        cmds.setAttr((obj_shape + ".overrideDisplayType"), 0)


def create_buffer(obj_name):
    """
    creates a buffer group above the given obj so that the obj can have 0 transforms

    :param obj_name: name of obj to 0 and create the buffer for
    :type: str

    :return: name of the buffer group
    :type: str
    """
    #creates a new group with pivot at world origin
    group_name = cmds.group(obj_name, name=obj_name + NamingConventionEnums.GROUP_SUFFIX)
    cmds.xform(pivots=(0, 0, 0))

    #freeze the scale on the obj so that there is no weird scale later
    cmds.makeIdentity(obj_name, apply=True, scale=True)

    update_buffer(obj_name, group_name)

    return group_name

def update_buffer(obj_name, group_name):
    """
    takes an object with a buffer and re-zeros it out

    :param obj_name: name of object to 0
    :type: str

    :param group_name: name of buffer group
    :type: str
    """
    #gets the objs matrix and then sets the group to that matrix
    obj_matrix = cmds.xform(obj_name, matrix=True, query=True, worldSpace=True)
    cmds.xform(group_name, matrix=obj_matrix)

    #0s the transforms on the obj so it goes back to original spot
    cmds.xform(obj_name, translation=(0, 0, 0), rotation=(0, 0, 0), scale=(1, 1, 1))

def lock_channels(obj_name,channel, to_lock = True, to_show = False):
    """
    locks the channels on the given obj

    :param obj_name: name of obj to lock the channels
    :type: str

    :param channel: the name of the channel to lock
    :type: str

    :param to_lock: bool to lock of unlock it
    :type: bool

    :param to_show: bool to hide or unhide it
    :type: bool
    """
    #lock the given attr
    cmds.setAttr(obj_name + '.' + channel, lock=to_lock, keyable=to_show,
                 channelBox=to_show)

def unlock_all_channels(obj_name):
    """
    unlocks all the trans/rotate/scale of the given object

    :param obj_name: obj to unlock
    :type: str
    """
    cmds.setAttr(obj_name + ".tx", lock = False, keyable = True, channelBox = False)
    cmds.setAttr(obj_name + ".ty", lock = False, keyable = True, channelBox = False)
    cmds.setAttr(obj_name + ".tz", lock = False, keyable = True, channelBox = False)
    cmds.setAttr(obj_name + ".rx", lock = False, keyable = True, channelBox = False)
    cmds.setAttr(obj_name + ".ry", lock = False, keyable = True, channelBox = False)
    cmds.setAttr(obj_name + ".rz", lock = False, keyable = True, channelBox = False)
    cmds.setAttr(obj_name + ".sx", lock = False, keyable = True, channelBox = False)
    cmds.setAttr(obj_name + ".sy", lock = False, keyable = True, channelBox = False)
    cmds.setAttr(obj_name + ".sz", lock = False, keyable = True, channelBox = False)

def lock_all_channels(obj_name):
    """
    locks all the trans/rotate/scale of the given object

    :param obj_name: obj to lock
    :type: str
    """
    cmds.setAttr(obj_name + ".tx", lock = True, keyable = False, channelBox = False)
    cmds.setAttr(obj_name + ".ty", lock = True, keyable = False, channelBox = False)
    cmds.setAttr(obj_name + ".tz", lock = True, keyable = False, channelBox = False)
    cmds.setAttr(obj_name + ".rx", lock = True, keyable = False, channelBox = False)
    cmds.setAttr(obj_name + ".ry", lock = True, keyable = False, channelBox = False)
    cmds.setAttr(obj_name + ".rz", lock = True, keyable = False, channelBox = False)
    cmds.setAttr(obj_name + ".sx", lock = True, keyable = False, channelBox = False)
    cmds.setAttr(obj_name + ".sy", lock = True, keyable = False, channelBox = False)
    cmds.setAttr(obj_name + ".sz", lock = True, keyable = False, channelBox = False)
    cmds.setAttr(obj_name + ".visibility", lock=True, keyable=False, channelBox=False)

def place_pole_vector(start_obj, mid_obj, end_obj):
    """
    https://vimeo.com/66262994 by Marco Giordano
    places a pole vector based on the three given objects

    :param start_obj: first obj in chain
    :type: str

    :param mid_obj: second obj in chain
    :type: str

    :param end_obj: third obj in chain
    :type: str

    :return: location to place pv
    """
    #get the locations of the 3 objs
    start = cmds.xform(start_obj, query=1, worldSpace=1, translation=1)
    mid = cmds.xform(mid_obj, query=1, worldSpace=1, translation=1)
    end = cmds.xform(end_obj, query=1, worldSpace=1, translation=1)

    #convert those locations into vectors
    startV = om.MVector(start[0], start[1], start[2])
    midV = om.MVector(mid[0], mid[1], mid[2])
    endV = om.MVector(end[0], end[1], end[2])

    #get the first to last obj vector and the first to mid obj vector
    startEnd = endV - startV
    startMid = midV - startV

    #find the projection point on startEnd vector fo the PV vector
    dotP = startMid * startEnd
    proj = float(dotP) / float(startEnd.length())
    startEndN = startEnd.normal()
    projV = startEndN * proj

    #create the pv vector and move it to the mid obj
    arrowV = startMid - projV

    #make the distance from mid joint equal to total length of the 3 joints
    start_to_mid_length = (midV - startV).length()
    mid_to_end_length = (endV - midV).length()
    total_length = start_to_mid_length + mid_to_end_length
    arrowV = arrowV.normal() * total_length

    finalV = arrowV + midV

    #finds the cross product of the plane to orient the pole vector control's y axis
    cross1 = startEnd ^ startMid
    cross1.normalize()

    # finds the cross product of the plane to orient the pole vector control's z axis
    cross2 = cross1 ^ arrowV
    cross2.normalize()
    arrowV.normalize()

    #creates a matrix of the above orientations
    matrixV = [arrowV.x, arrowV.y, arrowV.z, 0,
               cross1.x, cross1.y, cross1.z, 0,
               cross2.x, cross2.y, cross2.z, 0,
               0, 0, 0, 1]

    matrixM = om.MMatrix()

    om.MScriptUtil.createMatrixFromList(matrixV, matrixM)

    matrixFn = om.MTransformationMatrix(matrixM)

    #pulls the rotation out of the matrix and converts it to degrees
    rot = matrixFn.eulerRotation()
    rotation = [(rot.x / math.pi * 180.0), (rot.y / math.pi * 180.0),
                (rot.z / math.pi * 180.0)]

    #set the translation
    translation = [finalV.x, finalV.y, finalV.z]

    return {'rot' : rotation, 'trans' : translation}


def ik_fk_switch(blend_objs, ik_objs, fk_objs, switch_obj, pole_vector_obj):
    """
    creates an ik fk switch between the given objects

    :param blend_objs: the objs to be driven by the ik and fk
    :type: list

    :param ik_objs: list of the ik objs
    :type: list

    :param fk_objs: list of fk objs
    :type: list

    :param switch_obj: name of object to get the ik fk switch
    :type: str

    :param pole_vector_obj: name of the obj to be the pole vector
    :type: str
    """
    #first  create the ik handle
    cmds.select(ik_objs[0], replace = True)
    cmds.select(ik_objs[-1], add = True)
    ik_names = cmds.ikHandle()
    #rename the objs that the ik handle makes
    base = ik_objs[-1].rsplit('_', 1)[0]
    ik_handle = cmds.rename(ik_names[0], base + '_RPIK')
    cmds.rename(ik_names[1], base + '_Effector')

    #parent the ik handle to the cc and the pv to the ik
    ik_cc = base + '_IK' +NamingConventionEnums.CONTROL_CURVE_SUFFIX
    cmds.parent(ik_handle, ik_cc)
    cmds.select(pole_vector_obj, replace = True)
    cmds.select(ik_handle, add = True)
    cmds.PoleVectorConstraint()

    #orient the wrist to the IK control so the rotation follows it
    orient_const(ik_cc,ik_objs[-1],
                 base + 'IK_' + NamingConventionEnums.CONSTRAIN_SUFFIX)

    #set the visibility of the ik control
    lock_channels(ik_cc, 'visibility', to_lock=False)
    lock_channels(pole_vector_obj, 'visibility', to_lock=False)
    cmds.connectAttr(switch_obj + '.ikFkSwitch', ik_cc + '.visibility')
    cmds.connectAttr(switch_obj + '.ikFkSwitch', pole_vector_obj + '.visibility')

    #create the FK controls
    for fk_jnt in fk_objs:
        create_fk_control(fk_jnt)

    #set the vis of the FK controls
    rev = cmds.shadingNode('reverse', asUtility=True, name= blend_objs[-1] + '_REV')
    cmds.connectAttr(switch_obj + '.ikFkSwitch', rev + '.inputX')
    cmds.connectAttr(rev + '.outputX', fk_objs[0] + '.visibility')


    #blend the ik and fk joints to the main chain
    for i in range(len(blend_objs)):
        #create the blend colors
        bc = cmds.shadingNode('blendColors', asUtility = True,
                              name = blend_objs[i] + '_BC')

        #connect everything
        cmds.connectAttr(fk_objs[i] + '.rotate', bc + '.color2')
        cmds.connectAttr(ik_objs[i] + '.rotate', bc + '.color1')
        cmds.connectAttr(bc + '.output', blend_objs[i] + '.rotate')

        #connect the switch obj
        cmds.connectAttr(switch_obj + '.ikFkSwitch', bc + '.blender')


    group_name = blend_objs[0].replace(NamingConventionEnums.JOINT_SUFFIX,
                                    NamingConventionEnums.GROUP_SUFFIX)
    group_name = group_name.replace('hip', 'leg_jnts')
    group_name = group_name.replace('shoulder', 'arm_jnts')
    cmds.group([blend_objs[0], ik_objs[0], fk_objs[0]], name = group_name)

    #parent the controls to the rig hierarchy
    #get the buffer group above the ik cc and the pv cc
    ik_buffer = cmds.listRelatives(ik_cc, parent = True)[0]
    pv_buffer = cmds.listRelatives(pole_vector_obj, parent=True)[0]
    cmds.parent(ik_buffer, NamingConventionEnums.RIG_HIERARCHY[8])
    cmds.parent(pv_buffer, NamingConventionEnums.RIG_HIERARCHY[8])

    #hide the ik handles
    cmds.setAttr(ik_handle + '.visibility', 0)


def create_fk_control(fk_jnt):
    """
    creates and fk control on the given jnt with the parent add shape command

    :param fk_jnt: name of the joint to become fk
    :type: str
    """
    fk_cc_base = fk_jnt.rsplit('_', 1)[0]
    fk_cc = fk_cc_base + '_FK' + NamingConventionEnums.CONTROL_CURVE_SUFFIX

    # unlocks all the channels and then freezes them on the fk joint so that it
    # preserves the transforms when parented
    unlock_all_channels(fk_cc)
    cmds.parent(fk_cc, fk_jnt)
    cmds.makeIdentity(fk_cc, apply=True, translate=True, rotate=True, scale=True,
                      normal=False, preserveNormals=1)
    cmds.parent(fk_cc, world=True)

    # get the shape node of the control curve
    cmds.select(fk_cc)
    cmds.pickWalk(direction='down')
    shape = cmds.ls(selection=True)[0]

    # parent the shape node to the fk jnt
    cmds.parent(shape, fk_jnt, add=True, shape=True)

    # delete the old transform node
    cmds.delete(fk_cc)

    # lock the fk joints channels
    # lock the extra channels on the knees and elbows
    for cc_type in NamingConventionEnums.LOCK_CHANNLES:
        if fk_jnt.find(cc_type) != -1:
            for channel in NamingConventionEnums.LOCK_CHANNLES[cc_type]:
                lock_channels(fk_jnt, channel)

    # lock the standard fk channels
    for channel in MayaCommandEnums.SCALE:
        lock_channels(fk_jnt, channel)
    for channel in MayaCommandEnums.TRANSLATION:
        lock_channels(fk_jnt, channel)
    lock_channels(fk_jnt, 'visibility', False, False)
    lock_channels(fk_jnt, 'radi', False, False)

    cmds.parent(fk_jnt, world=True)
    cmds.undo()

def create_hierarchy(rig_dict = NamingConventionEnums.RIG_HIERARCHY_DICT,
                     parent_path = "" ):
    """
    creates the group hierarchy in maya for the rig
    """
    for item in rig_dict:
        if parent_path == "":
            #print "creating " + item
            cmds.group(name = item, empty = True, world = True)
        else:
            #print "creating " + item + " under " + parent_path
            cmds.group(name='null', empty=True, parent = parent_path)
            cmds.rename('null', item)
        if isinstance(rig_dict[item], dict) is True:
            #print "next dictionary"
            create_hierarchy(rig_dict[item], parent_path+"|"+item)
        elif isinstance(rig_dict[item], list) is True:
            #print "creating %s" % rig_dict[item]
            #print "       under " + parent_path
            for child in rig_dict[item]:
                cmds.group(name='null', empty=True, parent=parent_path + "|" + item)
                cmds.rename('null', child)
        elif isinstance(rig_dict[item], str) is True and rig_dict[item] is not "":
            #print "creating " + rig_dict[item] + " under " + parent_path
            cmds.group(name='null', empty=True, parent=parent_path + "|" + item)
            cmds.rename('null', rig_dict[item])

    if not cmds.attributeQuery(NamingConventionEnums.STEP_THREE_ATTR,
                         node = NamingConventionEnums.RIG_HIERARCHY[0], exists=True):
        # adds the globabl attr
        cmds.addAttr('|' + NamingConventionEnums.RIG_HIERARCHY[0],
                    longName=NamingConventionEnums.STEP_THREE_ATTR, attributeType='bool')


def create_real_skeleton(joint = None):
    """
    Looks at the fake joint curves in the hierarchy and creates a matching skeleton
    :param joint: str
    :return: joint_name
    :type: str
    """

    # if its the first joint to be created (its the pelvis)
    if joint is None:
        joint = 'pelvis'+NamingConventionEnums.FAKE_JOINT_SUFFIX
        # create a temporary group so that we wont get any errors
        cmds.group(name = 'temp'+ NamingConventionEnums.GROUP_SUFFIX,
                   parent = "fake_rig"+NamingConventionEnums.CONTROL_CURVE_SUFFIX
                    ,empty = True)

    # creates the joint and renames it to the FakeJointStructure object name
    joint_name = joint.replace(NamingConventionEnums.FAKE_JOINT_SUFFIX,
                                   NamingConventionEnums.JOINT_SUFFIX)
    temp_name = cmds.joint(p=(0, 0, 0))
    cmds.rename(temp_name, joint_name)

    # if the joint is a Tip, reverse foot joint, wrist, or pelvis
    # place the joint on the actual joint
    if joint_name.find('Tip') != -1 or \
            joint_name.find(NamingConventionEnums.REVERSE) != -1 or \
            joint_name.find('wrist') != -1 or joint_name.find('pelvis') != -1:
        place_on(joint_name, joint)
    # otherwise place it on the locator in the joint
    else:
        place_on(joint_name, joint + '_locator')

    #move joint to world
    cmds.parent(joint_name, world=True)

    # if not a tip
    if 'Tip' not in joint_name:
        children = cmds.listRelatives(joint, shapes = False, children = True)
        # function calls itself recursively and parents the children to the parent
        for child in children:
            if 'Shape' not in child:
                child_name = create_real_skeleton(child)
                cmds.parent(child_name, joint_name)

    # freeze transformations
    cmds.makeIdentity(joint_name, apply=True)

    return joint_name


def get_joint_list(step = 2):
    """
    grabs the list of joints
    :return: list of joint names in the structure
    """
    if step == 2:
        list = cmds.listRelatives("joints"+NamingConventionEnums.GROUP_SUFFIX,
                              ad=True, type = "transform")
    elif step == 3:
        list = cmds.listRelatives("joints" + NamingConventionEnums.GROUP_SUFFIX,
                                  ad=True, type="transform")
    list.reverse()
    return list

#----------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------- CLASSES --#

