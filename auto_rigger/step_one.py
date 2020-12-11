#!/usr/bin/env python
#SETMODE 777

#----------------------------------------------------------------------------------------#
#------------------------------------------------------------------------------ HEADER --#

"""
:author:
    Nick Lormand & Blake Day

:synopsis:
    This module has the classes and functions to complete step one of the autorigger.



:description:
    It creates fake joints in the scene from skeleton info in an xml file and connects
     them with connection curves. There are also functions to get the list of groups
     and joints.

:applications:
    Maya

:see_also:
    step_two
    step_three
    gen_utils
    maya_enums
    auto_rig_gui
"""

#----------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------- IMPORTS --#

# Default Python Imports

# Imports That You Wrote
import os
import xml.etree.ElementTree as et
import maya.cmds as cmds
import auto_rigger.gen_utils as gu
from maya_enums import MayaCommandEnums, NamingConventionEnums
#----------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------- FUNCTIONS --#

def read_xml():
    """
    Finds the XML file in the XML_utils folder and parses it
    :return: xml root object
    """
    prog_dir = os.path.abspath(os.path.dirname(__file__))
    os.chdir(prog_dir)
    #print prog_dir
    file_path = "%s/xml_utils/biped.xml" % (prog_dir)
    if file_path:
        xml_fh = et.parse(file_path)
        root = xml_fh.getroot()
        return root
    else:
        print "the biped.xml file is missing"
        return None

#----------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------- CLASSES --#

class FakeJointStructure(object):
    """
    Class to store fake joint data and child joints
    """
    def __init__(self):
        self.name = ''

        # transform values for maya
        self.tx = 0
        self.ty = 0
        self.tz = 0
        self.rx = 0
        self.ry = 0
        self.rz = 0

        # name of the connection curve
        self.connector = ''
        self.children = []


    def group(self):
        """
        selects and groups the list returned from get_hierarchy_list()
        :return: Success of the function
        """
        gu.create_four_point_arrow("fake_rig" +NamingConventionEnums.CONTROL_CURVE_SUFFIX)
        cmds.group(empty=True, name='joints'+NamingConventionEnums.GROUP_SUFFIX)
        cmds.parent(self.name, "joints"+NamingConventionEnums.GROUP_SUFFIX)
        cmds.parent("joints"+NamingConventionEnums.GROUP_SUFFIX,
                    "fake_rig"+NamingConventionEnums.CONTROL_CURVE_SUFFIX)
        cmds.parent('connectors'+NamingConventionEnums.GROUP_SUFFIX, "fake_rig"
                    +NamingConventionEnums.CONTROL_CURVE_SUFFIX)

        handles = cmds.ls('*Handle*', transforms = True)
        for handle in handles:
            gu.scale_const("fake_rig" +NamingConventionEnums.CONTROL_CURVE_SUFFIX, handle,
                           handle + "_scale" + NamingConventionEnums.CONSTRAIN_SUFFIX)

        #add global attr
        cmds.addAttr('|fake_rig'+NamingConventionEnums.CONTROL_CURVE_SUFFIX,
                     longName=NamingConventionEnums.STEP_ONE_ATTR, attributeType='bool')

        cmds.select("fake_rig"+NamingConventionEnums.CONTROL_CURVE_SUFFIX)

    def get_joint_list(self):
        """
        Recursively cycles through the joint structure and adds joint names to a list
        :return: list of joint names in the structure
        """
        list = cmds.listRelatives("joints"+NamingConventionEnums.GROUP_SUFFIX,
                                  ad=True, type = "transform")
        list.reverse()
        return list


    def get_connector_list(self):
        """
        Recursively cycles through the joint structure and adds connector names to a list
        :return: list of joint connector names in the structure
        """
        list = cmds.listRelatives("connectors"+NamingConventionEnums.GROUP_SUFFIX,
                                  c = True)
        list.reverse()
        return list


class Skeleton(object):
    """
    Class that builds a skeleton of fake joints. Has a Fake_joint_structure as an
    attribute. Has number of fingers passed in from the gui.
    """
    def __init__(self, root, num_fingers = 5, num_toes = 5, num_vertabrae = 7):
        # get the list of xml objects that are children to the root
        children = root.getchildren()

        # starts with the pelvis
        node = children[0]

        #create a group for the connectors
        connector_grp = cmds.group(empty=True,
                                   name='connectors'+NamingConventionEnums.GROUP_SUFFIX)
        cmds.setAttr(connector_grp + '.inheritsTransform', 0)

        self.number_of_fingers = num_fingers
        self.number_of_vertebrae = num_vertabrae-1
        self.number_of_toes = num_toes
        self.joint_structure = self.create_fake_skeleton(node)
        self.vertebrae_count = 0
        self.base_vertebrae_height = None


    def create_fake_skeleton(self, node, new_name = None):
        """
        this module recursively goes through the xml data to get the translation values
        and call create_fake_joint with those values.
        :param node: xml object containing the joint data
        :return: FakeJointStructure object filled with joint names and locations
        """
        node_joint = FakeJointStructure()
        node_attributes = node.getchildren()
        name = node.tag

        # takes out the vertebrae prefixes
        if "__FIRST_VERTEBRAE__" in name:
            name = name.replace("__FIRST_VERTEBRAE__", '')
        if "__SECOND_VERTEBRAE__" in name:
            name = name.replace("__SECOND_VERTEBRAE__", '')
        if "__THIRD_VERTEBRAE__" in name:
            name = name.replace("__THIRD_VERTEBRAE__", '')
        if "__FOURTH_VERTEBRAE__" in name:
            name = name.replace("__FOURTH_VERTEBRAE__", '')
        if "__FIFTH_VERTEBRAE__" in name:
            name = name.replace("__FIFTH_VERTEBRAE__", '')
        if "__SIXTH_VERTEBRAE__" in name:
            name = name.replace("__SIXTH_VERTEBRAE__", '')
        if "__SEVENTH_VERTEBRAE__" in name:
            name = name.replace("__SEVENTH_VERTEBRAE__", '')

        # takes out prefixes for removing fingers
        if "__FIRST_FINGER__" in name:
            name = name.replace("__FIRST_FINGER__", '')
        if "__SECOND_FINGER__" in name:
            name = name.replace("__SECOND_FINGER__", '')
        if "__THIRD_FINGER__" in name:
            name = name.replace("__THIRD_FINGER__", '')
        if "__FOURTH_FINGER__" in name:
            name = name.replace("__FOURTH_FINGER__", '')
        if "__FIFTH_FINGER__" in name:
            name = name.replace("__FIFTH_FINGER__", '')

        # takes out prefixes for removing toes
        if "__FIRST_TOE__" in name:
            name = name.replace("__FIRST_TOE__", '')
        if "__SECOND_TOE__" in name:
            name = name.replace("__SECOND_TOE__", '')
        if "__THIRD_TOE__" in name:
            name = name.replace("__THIRD_TOE__", '')
        if "__FOURTH_TOE__" in name:
            name = name.replace("__FOURTH_TOE__", '')
        if "__FIFTH_TOE__" in name:
            name = name.replace("__FIFTH_TOE__", '')

        # takes out left and right prefixes and replaces with enum
        if "__LEFT__" in name:
            name = name.replace("__LEFT__", NamingConventionEnums.LEFT)
        if "__RIGHT__" in name:
            name = name.replace("__RIGHT__", NamingConventionEnums.RIGHT)

        name = name.replace("__JOINT__", NamingConventionEnums.FAKE_JOINT_SUFFIX)

        # if a name was passed in during the recursion process
        # make it the current name
        if new_name:
            node_joint.name = new_name
        else:
            node_joint.name = name

        # stores all of the joint location data in the xml object into the
        # FakeJointStructure object (translation and rotation)
        for node_attr in node_attributes:
            if node_attr.tag == MayaCommandEnums.TRANSLATION_X:
                node_joint.tx = float(node_attr.attrib['value'])
                        
            elif node_attr.tag == MayaCommandEnums.TRANSLATION_Y:
                node_joint.ty = float(node_attr.attrib['value'])
                
            elif node_attr.tag == MayaCommandEnums.TRANSLATION_Z:
                node_joint.tz = float(node_attr.attrib['value'])
                
            elif node_attr.tag == MayaCommandEnums.ROTATION_X:
                node_joint.rx = float(node_attr.attrib['value'])
                
            elif node_attr.tag == MayaCommandEnums.ROTATION_Y:
                node_joint.ry = float(node_attr.attrib['value'])
                
            elif node_attr.tag == MayaCommandEnums.ROTATION_Z:
                node_joint.rz = float(node_attr.attrib['value'])

        # creates fake spine joint and spaces it out according to the number of vertabrae
        if 'spine' in node_joint.name or 'pelvis' in node_joint.name:
            height_scale = 40 / self.number_of_vertebrae+1

            # if its the pelvis, do nothing
            if 'pelvis' in node_joint.name:
                self.base_vertebrae_height = node_joint.ty
                self.vertebrae_count = 0
            # changes the height based off the vertebrae count
            new_y = self.base_vertebrae_height +(height_scale*self.vertebrae_count)

            # creates fake joint in 3d space
            gu.create_fake_joint(node_joint.name, node_joint.tx, new_y,
                                node_joint.tz, node_joint.rx, node_joint.ry,
                                node_joint.rz)
            self.vertebrae_count +=1
        # creates fake joint in 3d space
        else:
            gu.create_fake_joint(node_joint.name, node_joint.tx, node_joint.ty,
                             node_joint.tz, node_joint.rx, node_joint.ry, node_joint.rz)

        # grabs child node of the current xml object
        node_children = node_attributes[9].getchildren()

        # base case
        if not node_children:
            return node_joint
        else:
            list_of_children = []
            # recursive step, appends returned joints to the children list
            for child_node in node_children:
                # checks for fingers to be removed
                if "__FIRST_FINGER__" in child_node.tag and self.number_of_fingers <= 4:
                    continue
                if "__SECOND_FINGER__" in child_node.tag and self.number_of_fingers <= 3:
                    continue
                if "__THIRD_FINGER__" in child_node.tag and self.number_of_fingers <= 2:
                    continue
                if "__FOURTH_FINGER__" in child_node.tag and self.number_of_fingers <= 1:
                    continue
                if "__FIFTH_FINGER__" in child_node.tag and self.number_of_fingers == 0:
                    continue

                # checks for toes to be removed
                if "__FIRST_TOE__" in child_node.tag and self.number_of_toes <= 4:
                    continue
                if "__SECOND_TOE__" in child_node.tag and self.number_of_toes <= 3:
                    continue
                if "__THIRD_TOE__" in child_node.tag and self.number_of_toes <= 2:
                    continue
                if "__FOURTH_TOE__" in child_node.tag and self.number_of_toes <= 1:
                    continue
                if "__FIFTH_TOE__" in child_node.tag and self.number_of_toes == 0:
                    continue

                # If there is only 1 vertebrae
                if "__FIRST_VERTEBRAE__" in child_node.tag and\
                        self.number_of_vertebrae == 1:
                    # skips the remaining vertebrae in the xml chain
                    children = child_node.getchildren()
                    child = children[9].getchildren()[0]
                    children = child.getchildren()
                    child = children[9].getchildren()[0]
                    children = child.getchildren()
                    child = children[9].getchildren()[0]
                    children = child.getchildren()
                    child = children[9].getchildren()[0]
                    children = child.getchildren()
                    child = children[9].getchildren()[0]
                    children = child.getchildren()
                    child = children[9].getchildren()[0]
                    #print child
                    new_name = "spine_1" + NamingConventionEnums.FAKE_JOINT_SUFFIX
                    temp_child = self.create_fake_skeleton(child, new_name)
                    list_of_children.append(temp_child)
                    node_joint.connector = gu.create_connection_curve(node_joint.name,
                                                                      temp_child.name)
                    # adding connectors to connectors group
                    cmds.parent(node_joint.connector, "connectors"
                                + NamingConventionEnums.GROUP_SUFFIX)
                    # parents child joint ot parent joint
                    cmds.parent(temp_child.name, node_joint.name)

                # If there is only 2 vertebrae
                elif "__SECOND_VERTEBRAE__" in child_node.tag and \
                        self.number_of_vertebrae == 2:
                    # skips the remaining vertebrae in the xml chain
                    children = child_node.getchildren()
                    child = children[9].getchildren()[0]
                    children = child.getchildren()
                    child = children[9].getchildren()[0]
                    children = child.getchildren()
                    child = children[9].getchildren()[0]
                    children = child.getchildren()
                    child = children[9].getchildren()[0]
                    children = child.getchildren()
                    child = children[9].getchildren()[0]
                    #print child
                    new_name = "spine_2" + NamingConventionEnums.FAKE_JOINT_SUFFIX
                    temp_child = self.create_fake_skeleton(child, new_name)
                    list_of_children.append(temp_child)
                    node_joint.connector = gu.create_connection_curve(node_joint.name,
                                                                      temp_child.name)
                    # adding connectors to connectors group
                    cmds.parent(node_joint.connector, "connectors"
                                + NamingConventionEnums.GROUP_SUFFIX)
                    # parents child joint ot parent joint
                    cmds.parent(temp_child.name, node_joint.name)

                # If there is only 3 vertebrae
                elif "__THIRD_VERTEBRAE__" in child_node.tag and \
                        self.number_of_vertebrae == 3:
                    # skips the remaining vertebrae in the xml chain
                    children = child_node.getchildren()
                    child = children[9].getchildren()[0]
                    children = child.getchildren()
                    child = children[9].getchildren()[0]
                    children = child.getchildren()
                    child = children[9].getchildren()[0]
                    children = child.getchildren()
                    child = children[9].getchildren()[0]

                    new_name = "spine_3" + NamingConventionEnums.FAKE_JOINT_SUFFIX
                    temp_child = self.create_fake_skeleton(child, new_name)
                    list_of_children.append(temp_child)
                    node_joint.connector = gu.create_connection_curve(node_joint.name,
                                                                      temp_child.name)
                    # adding connectors to connectors group
                    cmds.parent(node_joint.connector, "connectors"
                                + NamingConventionEnums.GROUP_SUFFIX)
                    # parents child joint ot parent joint
                    cmds.parent(temp_child.name, node_joint.name)

                # If there is only 4 vertebrae
                elif "__FOURTH_VERTEBRAE__" in child_node.tag and \
                        self.number_of_vertebrae == 4:
                    # skips the remaining vertebrae in the xml chain
                    children = child_node.getchildren()
                    child = children[9].getchildren()[0]
                    children = child.getchildren()
                    child = children[9].getchildren()[0]
                    children = child.getchildren()
                    child = children[9].getchildren()[0]

                    new_name = "spine_4" + NamingConventionEnums.FAKE_JOINT_SUFFIX
                    temp_child = self.create_fake_skeleton(child, new_name)
                    list_of_children.append(temp_child)
                    node_joint.connector = gu.create_connection_curve(node_joint.name,
                                                                      temp_child.name)
                    # adding connectors to connectors group
                    cmds.parent(node_joint.connector, "connectors"
                                + NamingConventionEnums.GROUP_SUFFIX)
                    # parents child joint ot parent joint
                    cmds.parent(temp_child.name, node_joint.name)

                # If there is only 5 vertebrae
                elif "__FIFTH_VERTEBRAE__" in child_node.tag and \
                        self.number_of_vertebrae == 5:
                    # skips the remaining vertebrae in the xml chain
                    children = child_node.getchildren()
                    child = children[9].getchildren()[0]
                    children = child.getchildren()
                    child = children[9].getchildren()[0]

                    new_name = "spine_5" + NamingConventionEnums.FAKE_JOINT_SUFFIX
                    temp_child = self.create_fake_skeleton(child, new_name)
                    list_of_children.append(temp_child)
                    node_joint.connector = gu.create_connection_curve(node_joint.name,
                                                                      temp_child.name)
                    # adding connectors to connectors group
                    cmds.parent(node_joint.connector, "connectors"
                                + NamingConventionEnums.GROUP_SUFFIX)
                    # parents child joint ot parent joint
                    cmds.parent(temp_child.name, node_joint.name)

                # If there is only 6 vertebrae
                elif "__SIXTH_VERTEBRAE__" in child_node.tag and \
                        self.number_of_vertebrae == 6:
                    # skips the remaining vertebrae in the xml chain
                    children = child_node.getchildren()
                    child = children[9].getchildren()[0]

                    new_name = "spine_6" + NamingConventionEnums.FAKE_JOINT_SUFFIX
                    temp_child = self.create_fake_skeleton(child, new_name)
                    list_of_children.append(temp_child)
                    node_joint.connector = gu.create_connection_curve(node_joint.name,
                                                                      temp_child.name)
                    # adding connectors to connectors group
                    cmds.parent(node_joint.connector, "connectors"
                                + NamingConventionEnums.GROUP_SUFFIX)
                    # parents child joint ot parent joint
                    cmds.parent(temp_child.name, node_joint.name)
                else:
                    temp_child = self.create_fake_skeleton(child_node)
                    list_of_children.append(temp_child)
                    node_joint.connector = gu.create_connection_curve(node_joint.name,
                                                                temp_child.name)
                    # adding connectors to connectors group
                    cmds.parent(node_joint.connector, "connectors"
                                +NamingConventionEnums.GROUP_SUFFIX)
                    # parents child joint ot parent joint
                    cmds.parent(temp_child.name, node_joint.name)

            # add the returned children to the current joints list of children
            node_joint.children.extend(list_of_children)

            # return the current joint
            return node_joint



