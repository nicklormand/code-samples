#!/usr/bin/env python
#SETMODE 777

#----------------------------------------------------------------------------------------#
#------------------------------------------------------------------------------ HEADER --#

"""
:author:
    Blake day & Nick Lormand

:synopsis:
    runs step three of the auto rigger, creating the rig

:description:
    takes in a list of joints, and controls and then creates a rig from those. Sets up the
    ik/fk arms and legs, the hands, reverse feet, head, and ribbon spine

:applications:
    Maya

:see_also:
    step_one
    step_two
    gen_utils
    maya_enums
    auto_rig_gui
"""

#----------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------- IMPORTS --#

# Default Python Imports
import maya.cmds as cmds
import maya.mel as mel
import math

# Imports That You Wrote
import auto_rigger.gen_utils as gu
from maya_enums import MayaCommandEnums, NamingConventionEnums
import auto_rigger.step_one as step_one
#----------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------- FUNCTIONS --#
def run_step(control_list, num_vertebrae):
    """
    adds box control curves to all joints

    :param control_list: list of the controls in the scene
    :type: list

    :param num_vertebrae: number of vertebrae to help with spine creation
    :type: int
    """
    # loop through controls and 0 transforms then lock scale
    for control in control_list:
        #0 transforms
        if control.find('FK') == -1:
            gu.create_buffer(control)

        #delete history on the curve
        cmds.select(control)
        cmds.DeleteHistory()

        #lock channels
        for cc_type in NamingConventionEnums.LOCK_CHANNLES:
            if control.find(cc_type) != -1:
                for channel in NamingConventionEnums.LOCK_CHANNLES[cc_type]:
                    gu.lock_channels(control, channel)
        #add the extra attrs to the controls that have them
        for cc_type in NamingConventionEnums.EXTRA_ATTRS:
            if control.find(cc_type) != -1:
                for attr in NamingConventionEnums.EXTRA_ATTRS[cc_type]:
                    cmds.addAttr(control, longName = attr, attributeType='float')
                    cmds.setAttr(control + '.' + attr, keyable = True)
        #lock the visibility and scale of all controls
        gu.lock_channels(control, 'visibility')
        for channel in MayaCommandEnums.SCALE:
            gu.lock_channels(control, channel)

    # replicate joint structure with real joints
    cmds.select(d=True)
    gu.create_real_skeleton()

    joint_list = cmds.listRelatives('pelvis' + NamingConventionEnums.JOINT_SUFFIX,
                                         children=True, shapes=False, allDescendents=True)
    joint_list.append('pelvis' + NamingConventionEnums.JOINT_SUFFIX)
    joint_list.reverse()

    cmds.parent('pelvis'+NamingConventionEnums.JOINT_SUFFIX,
                'joints'+NamingConventionEnums.GROUP_SUFFIX)


    # delete old structure
    cmds.delete('connectors' + NamingConventionEnums.GROUP_SUFFIX)
    cmds.delete('pelvis'+NamingConventionEnums.FAKE_JOINT_SUFFIX)

    # loop through the joints and calls the necessary functions to make the rig
    for jnt_name in joint_list:

        #check if the joint needs an ik fk switch
        for ik_obj in NamingConventionEnums.IK_JOINTS:
            if jnt_name.find(ik_obj) != -1:

                #check side of joint first
                side = jnt_name.split('_')[0]

                #checks what obj has the ik fk switch
                switch_jnt = (side + '_' + NamingConventionEnums.IK_JOINTS[ik_obj] +
                        NamingConventionEnums.JOINT_SUFFIX)

                #call the make_ik_fk
                make_ik_fk(jnt_name, switch_jnt)

        #check if its the head joint and calls the set up for it
        if jnt_name.find('head') != -1 and jnt_name.find('Tip') == -1:
            setup_head(jnt_name)

        if jnt_name.find('clavicle') != -1:
            #create the fk control for the clavicle
            gu.create_fk_control(jnt_name)
            #rename the clavicle bind suffix
            bind_name = jnt_name.replace(NamingConventionEnums.JOINT_SUFFIX,
                                         NamingConventionEnums.BIND_JOINT_SUFFIX)
            cmds.rename(jnt_name, bind_name)

        # Constrain left hand_cc_GRP to wrist_cc
        if jnt_name.find('palm') != -1 and \
                jnt_name.find(NamingConventionEnums.LEFT) != -1:
            palm_cc_grp = NamingConventionEnums.LEFT + 'palm' \
          + NamingConventionEnums.CONTROL_CURVE_SUFFIX+ NamingConventionEnums.GROUP_SUFFIX
            cmds.parent(palm_cc_grp, jnt_name)
            cmds.select(clear=True)
            cmds.group(name=NamingConventionEnums.LEFT+'digits'
                            +NamingConventionEnums.GROUP_SUFFIX, empty = True)
            cmds.parent(NamingConventionEnums.LEFT + 'digits'
                        +NamingConventionEnums.GROUP_SUFFIX, jnt_name)

            # rename the palm to bind suffix
            bind_name = jnt_name.replace(NamingConventionEnums.JOINT_SUFFIX,
                                         NamingConventionEnums.BIND_JOINT_SUFFIX)
            cmds.rename(jnt_name, bind_name)

        # Constrain left hand_cc_GRP to wrist_cc
        if jnt_name.find('palm') != -1 and \
                jnt_name.find(NamingConventionEnums.RIGHT) != -1:
            palm_cc_grp = NamingConventionEnums.RIGHT + 'palm' \
          + NamingConventionEnums.CONTROL_CURVE_SUFFIX+ NamingConventionEnums.GROUP_SUFFIX
            cmds.parent(palm_cc_grp, jnt_name)
            cmds.select(clear=True)
            cmds.group(name=NamingConventionEnums.RIGHT + 'digits'
                            +NamingConventionEnums.GROUP_SUFFIX, empty = True)
            cmds.parent(NamingConventionEnums.RIGHT + 'digits'
                        +NamingConventionEnums.GROUP_SUFFIX, jnt_name)

            #rename the palm to bind suffix
            bind_name = jnt_name.replace(NamingConventionEnums.JOINT_SUFFIX,
                                         NamingConventionEnums.BIND_JOINT_SUFFIX)
            cmds.rename(jnt_name, bind_name)

        # left or right side enum
        side = ''

        # Connects all of the attributes in the hand_CC to the finger rotations
        for digit in NamingConventionEnums.DIGITS:
            # if the digit is not a toe or tip
            if jnt_name.find(digit) != -1 and jnt_name.find('Tip') == -1 \
                    and jnt_name.find('Toe') == -1:
                # Calls setup_digits for each side to setup the hierarchy and lock values
                if jnt_name.find(NamingConventionEnums.LEFT) != -1:
                    setup_digits(jnt_name, NamingConventionEnums.LEFT)
                    side = NamingConventionEnums.LEFT
                if jnt_name.find(NamingConventionEnums.RIGHT)!= -1:
                    setup_digits(jnt_name, NamingConventionEnums.RIGHT)
                    side = NamingConventionEnums.RIGHT

                # Connects the attributes for the index finger to the hand_CC
                if jnt_name.find('index_1') != -1:
                    node = cmds.shadingNode('multiplyDivide',
                        name=jnt_name.replace('_1'+NamingConventionEnums.JOINT_SUFFIX,
                                                      '') + "_MD", asUtility=True)
                    cmds.connectAttr(side + 'palm_CC.indexCurl', node + '.input1Z',
                                     force=True)
                    cmds.connectAttr(node + '.outputZ', jnt_name + '.rotateZ', force=True)
                    cmds.connectAttr(node + '.outputZ', jnt_name.replace('1', '2')
                                     + '.rotateZ', force=True)
                    cmds.connectAttr(node + '.outputZ', jnt_name.replace('1', '3')
                                     + '.rotateZ', force=True)
                    cmds.setAttr(node + ".input2Z", 2)
                    cmds.connectAttr(side + 'palm_CC.fingerSpread', node + '.input1Y',
                                     force=True)
                    cmds.connectAttr(node + '.outputY', jnt_name + '.rotateY', force=True)
                    cmds.setAttr(node + ".input2Y", -1)

                # Connects the attributes for the middle finger to the hand_CC
                elif jnt_name.find('middle_1') != -1:
                    node = cmds.shadingNode('multiplyDivide', name=jnt_name.replace(
                                                '_1' + NamingConventionEnums.JOINT_SUFFIX,
                                                '') + "_MD", asUtility=True)
                    cmds.connectAttr(side + 'palm_CC.middleCurl', node + '.input1Z',
                                     force=True)
                    cmds.connectAttr(node + '.outputZ', jnt_name + '.rotateZ', force=True)
                    cmds.connectAttr(node + '.outputZ', jnt_name.replace('1', '2')
                                     + '.rotateZ', force=True)
                    cmds.connectAttr(node + '.outputZ', jnt_name.replace('1', '3')
                                     + '.rotateZ', force=True)
                    cmds.setAttr(node+".input2Z", 2)
                    cmds.connectAttr(side + 'palm_CC.fingerSpread', node + '.input1Y',
                                     force=True)
                    cmds.connectAttr(node + '.outputY', jnt_name + '.rotateY', force=True)
                    cmds.setAttr(node + ".input2Y", -.5)

                # Connects the attributes for the ring finger to the hand_CC
                elif jnt_name.find('ring_1') != -1:
                    node = cmds.shadingNode('multiplyDivide', name=jnt_name.replace(
                                                '_1' + NamingConventionEnums.JOINT_SUFFIX,
                                                '') + "_MD", asUtility=True)
                    cmds.connectAttr(side + 'palm_CC.ringCurl', node + '.input1Z',
                                     force=True)
                    cmds.connectAttr(node + '.outputZ', jnt_name + '.rotateZ', force=True)
                    cmds.connectAttr(node + '.outputZ', jnt_name.replace('1', '2')
                                     + '.rotateZ', force=True)
                    cmds.connectAttr(node + '.outputZ', jnt_name.replace('1', '3')
                                     + '.rotateZ', force=True)
                    cmds.setAttr(node + ".input2Z", 2)
                    cmds.connectAttr(side + 'palm_CC.fingerSpread', node + '.input1Y',
                                     force=True)
                    cmds.connectAttr(node + '.outputY', jnt_name + '.rotateY', force=True)
                    cmds.setAttr(node + ".input2Y", .5)

                # Connects the attributes for the pinky finger to the hand_CC
                elif jnt_name.find('pinky_1') != -1:
                    node = cmds.shadingNode('multiplyDivide', name=jnt_name.replace(
                                                '_1' + NamingConventionEnums.JOINT_SUFFIX,
                                                '') + "_MD", asUtility=True)
                    cmds.connectAttr(side + 'palm_CC.pinkyCurl', node + '.input1Z',
                                     force=True)
                    cmds.connectAttr(node + '.outputZ', jnt_name + '.rotateZ', force=True)
                    cmds.connectAttr(node + '.outputZ', jnt_name.replace('1', '2')
                                     + '.rotateZ', force=True)
                    cmds.connectAttr(node + '.outputZ', jnt_name.replace('1', '3')
                                     + '.rotateZ', force=True)
                    cmds.setAttr(node + ".input2Z", 2)
                    cmds.connectAttr(side + 'palm_CC.fingerSpread', node + '.input1Y',
                                     force=True)
                    cmds.connectAttr(node + '.outputY', jnt_name + '.rotateY', force=True)
                    cmds.setAttr(node + ".input2Y", 1)

                # Connects the attributes for the thumb to the hand_CC
                elif jnt_name.find('thumb_1') != -1:
                    node = cmds.shadingNode('multiplyDivide', name=jnt_name.replace(
                                                '_1' + NamingConventionEnums.JOINT_SUFFIX,
                                                '') + "_MD", asUtility=True)
                    cmds.connectAttr(side + 'palm_CC.thumbCurl', node + '.input1Z',
                                     force=True)
                    cmds.connectAttr(node + '.outputZ', jnt_name + '.rotateZ', force=True)
                    cmds.connectAttr(node + '.outputZ', jnt_name.replace('1', '2')
                                     + '.rotateZ', force=True)
                    cmds.connectAttr(node + '.outputZ', jnt_name.replace('1', '3')
                                     + '.rotateZ', force=True)
                    cmds.setAttr(node + ".input2Z", 2)
                    cmds.connectAttr(side + 'palm_CC.fingerSpread', node + '.input1Y',
                                     force=True)
                    cmds.connectAttr(node + '.outputY', jnt_name + '.rotateY', force=True)
                    cmds.setAttr(node + ".input2Y", -1)
            # if hte digit is a toe, but not a tip
            elif jnt_name.find(digit) != -1 and jnt_name.find('Tip') == -1 \
                    and jnt_name.find('Toe') != -1:
                # calls setup toes for each side
                if jnt_name.find(NamingConventionEnums.LEFT) != -1:
                    setup_toes(jnt_name, NamingConventionEnums.LEFT)
                    side = NamingConventionEnums.LEFT
                if jnt_name.find(NamingConventionEnums.RIGHT) != -1:
                    setup_toes(jnt_name, NamingConventionEnums.RIGHT)
                    side = NamingConventionEnums.RIGHT


        #checks if its the foot joint and calls the reverse foot
        if jnt_name.find('ball') != -1:
            setup_reverse_foot(jnt_name)

        #call the spine set up
        if jnt_name.find('pelvis') != -1:
            #fix the pelvis orientation
            control_name = 'pelvis' + NamingConventionEnums.CONTROL_CURVE_SUFFIX
            gu.unlock_all_channels(control_name)
            cmds.select(control_name)
            cmds.pickWalk(direction='up')
            control_buffer = cmds.ls(selection=True)
            cmds.makeIdentity(control_buffer, apply=True, translate=True, rotate=True,
                              scale=True, normal=False, preserveNormals=1)

            for channel in MayaCommandEnums.SCALE:
                gu.lock_channels(control_name, channel)

            #call the spine setup
            setup_spine(jnt_name, num_vertebrae)

    #connect the arms and legs to the spine
    #make a list with the arms and legs the parent them to the right spot
    clavicles = cmds.ls('*clavicle*', type = 'transform')
    #unlock the clavicles so they can be parented
    for clav in clavicles:
        gu.unlock_all_channels(clav)
        cmds.parent(clav, NamingConventionEnums.SPINE_CTRLS[-1] +
                NamingConventionEnums.CONTROL_CURVE_SUFFIX)
        #relock the clavicles
        for channel in MayaCommandEnums.SCALE:
            gu.lock_channels(clav, channel)
        for channel in MayaCommandEnums.TRANSLATION:
            gu.lock_channels(clav, channel)
    #parent the legs
    legs = cmds.ls('*leg*', type='transform')
    cmds.parent(legs, NamingConventionEnums.SPINE_CTRLS[0] +
                NamingConventionEnums.CONTROL_CURVE_SUFFIX)


    #rename all of the fingers to bind suffix
    for type in NamingConventionEnums.DIGITS:
        digits = cmds.ls('*' + type + '*', type = 'joint')
        for digit in digits:
            digit_bind_name = digit.replace(NamingConventionEnums.JOINT_SUFFIX,
                                            NamingConventionEnums.BIND_JOINT_SUFFIX)
            #skips the tips
            if cmds.objExists(digit) and digit.find('Tip') == -1:
                cmds.rename(digit, digit_bind_name)


    #hide the extra groups in the master node
    cmds.setAttr(NamingConventionEnums.RIG_HIERARCHY[9] + '.visibility', 0)
    cmds.setAttr(NamingConventionEnums.RIG_HIERARCHY[10] + '.visibility', 0)
    cmds.setAttr(NamingConventionEnums.RIG_HIERARCHY[11] + '.visibility', 0)
    cmds.setAttr(NamingConventionEnums.RIG_HIERARCHY[12] + '.visibility', 0)


def make_ik_fk(blend_root, switch_jnt):
    """
    this code takes the blend root joint and makes an ik fk switch out of it

    :param blend_root: name of the root joint
    :type: str

    :param switch_jnt: name of the obj to have the ik and fk switch on it
    :type: str

    """
    # unparents the jnt at the end of the chain so it isnt duped

    cmds.select(switch_jnt)
    cmds.pickWalk(direction='up')
    to_parent = cmds.ls(selection=True)
    cmds.parent(switch_jnt, world=True)

    # get the obj with the ik/fk switch
    switch_obj_temp = switch_jnt.replace(NamingConventionEnums.JOINT_SUFFIX,
                                    NamingConventionEnums.CONTROL_CURVE_SUFFIX)
    switch_obj = switch_obj_temp.replace('ball', 'foot')

    # duplicate IKs
    ik_children = cmds.duplicate(blend_root, renameChildren=True)
    # duplicate FKs
    fk_children = cmds.duplicate(blend_root, renameChildren=True)

    # makes a list of the 3 blend joints
    blend_objs = [blend_root]
    blend_children = cmds.listRelatives(blend_root, allDescendents=True)
    blend_children.reverse()
    blend_objs.extend(blend_children)

    # get the pole vector obj
    pv_obj = blend_objs[1].replace(NamingConventionEnums.JOINT_SUFFIX,
                                   '_PV' + NamingConventionEnums.CONTROL_CURVE_SUFFIX)

    # calls the ik_fk_switch in gen utils
    gu.ik_fk_switch(blend_objs, ik_children, fk_children, switch_obj, pv_obj)

    cmds.setAttr(switch_obj + ".ikFkSwitch", 1)
    cmds.setAttr(ik_children[0] + '.visibility', 0)

    # rename ik_children
    for joint in ik_children:
        if '1' in joint:
            cmds.rename(joint,
                        joint.rsplit(NamingConventionEnums.JOINT_SUFFIX)[0]
                        + '_IK' + NamingConventionEnums.JOINT_SUFFIX)
    # rename fk_children
    for joint in fk_children:
        if '2' in joint:
            cmds.rename(joint,
                        joint.rsplit(NamingConventionEnums.JOINT_SUFFIX)[0]
                        + '_FK' + NamingConventionEnums.JOINT_SUFFIX)

    # re-parent the switch obj
    cmds.parent(switch_jnt, to_parent)

    #rename the bind joints
    for joint in blend_objs:
        bind_jnt = joint.replace(NamingConventionEnums.JOINT_SUFFIX,
                                          NamingConventionEnums.BIND_JOINT_SUFFIX)
        if joint.find('ankle') == -1:
            cmds.rename(joint, bind_jnt)





def setup_head(head_jnt):
    """
    sets up the head controls

    :param head_jnt: name of the head joint
    :type: str
    """
    #get the neck joint
    cmds.select(head_jnt)
    cmds.pickWalk(direction='up')
    neck_jnt = cmds.ls(selection=True)[0]

    #get the neck controller
    neck_cc = neck_jnt.replace(NamingConventionEnums.JOINT_SUFFIX,
                               '_FK' + NamingConventionEnums.CONTROL_CURVE_SUFFIX)

    #get the head controller
    head_cc = head_jnt.replace(NamingConventionEnums.JOINT_SUFFIX,
                               '_FK' + NamingConventionEnums.CONTROL_CURVE_SUFFIX)

    #zero out the two controls with the a buffer
    gu.unlock_all_channels(head_cc)
    gu.unlock_all_channels(neck_cc)
    head_buffer = gu.create_buffer(head_cc)
    neck_buffer = gu.create_buffer(neck_cc)

    #create the hierarchy
    cmds.select(neck_jnt)
    cmds.pickWalk(direction='up')
    to_parent = cmds.ls(selection=True)[0]

    cmds.parent(neck_jnt, neck_cc)
    cmds.parent(head_jnt, head_cc)
    cmds.parent(head_buffer, neck_cc)
    cmds.parent(neck_buffer, to_parent)

    #create the neck tip joint by duplicating the head jnt
    dupe = cmds.duplicate(head_jnt, renameChildren = True)
    to_delete = cmds.listRelatives(dupe[0], allDescendents = True)
    cmds.delete(to_delete)
    neck_tip = cmds.rename(dupe[0], 'neck_Tip' + NamingConventionEnums.JOINT_SUFFIX)
    cmds.parent(neck_tip, neck_jnt)

    #create the locators that will serve as the aim target
    head_loc = cmds.spaceLocator(name = 'head' + NamingConventionEnums.LOCATOR_SUFFIX)
    gu.place_on(head_loc, head_cc)
    cmds.parent(head_loc, head_cc)
    cmds.makeIdentity(head_loc, apply=True, translate=True, rotate=True, scale=True,
                      normal=False, preserveNormals=1)

    neck_loc = cmds.spaceLocator(name='neckUpVector' +
                                      NamingConventionEnums.LOCATOR_SUFFIX)
    gu.place_on(neck_loc, neck_cc)
    cmds.parent(neck_loc, neck_cc)
    cmds.makeIdentity(neck_loc, apply=True, translate=True, rotate=True, scale=True,
                      normal=False, preserveNormals=1)
    cmds.xform(neck_loc, translation = (0, 0, -10))

    #setup the constraints
    #point constrain on the head jnt from the neck end jnt
    gu.point_const(neck_tip, head_jnt, 'head' + NamingConventionEnums.CONSTRAIN_SUFFIX)
    gu.aim_const(head_loc, neck_jnt, 'neck_aim' + NamingConventionEnums.CONSTRAIN_SUFFIX,
                 (1, 0, 0), (0,0,1),'object', neck_loc[0], maintain_offset = True)

    for channel in MayaCommandEnums.SCALE:
        gu.lock_channels(head_cc, channel)
        gu.lock_channels(neck_cc, channel)

    #parent the neck to the main hierarchy
    cmds.parent(neck_buffer, NamingConventionEnums.SPINE_CTRLS[-1] +
                NamingConventionEnums.CONTROL_CURVE_SUFFIX)

    #rename the bind joints
    head_bind_name = head_jnt.replace(NamingConventionEnums.JOINT_SUFFIX,
                               NamingConventionEnums.BIND_JOINT_SUFFIX)
    cmds.rename(head_jnt, head_bind_name)
    neck_bind_name = neck_jnt.replace(NamingConventionEnums.JOINT_SUFFIX,
                                      NamingConventionEnums.BIND_JOINT_SUFFIX)
    cmds.rename(neck_jnt, neck_bind_name)

    #hide the two locators
    cmds.setAttr(head_loc[0] + '.visibility', 0)
    cmds.setAttr(neck_loc[0] + '.visibility', 0)

def setup_digits(digit_jnt, side):
    """
    sets up the finger controls
    :param digit_jnt: name of the finger joint
    :type: str
    :param side of the body (left or right enum)
    :type: str
    """
    # the name of the joints cc, cc_grp, and the digits_grp
    joint_cc = digit_jnt.replace(NamingConventionEnums.JOINT_SUFFIX,
                                NamingConventionEnums.CONTROL_CURVE_SUFFIX)
    joint_cc_grp = joint_cc+NamingConventionEnums.GROUP_SUFFIX
    digits_grp = side+'digits'+NamingConventionEnums.GROUP_SUFFIX

    # if its the first joint in the digit
    if digit_jnt.find('1') != -1:
        # parent the cc_grp to the digit group
        cmds.parent(joint_cc_grp, digits_grp)
        # parent joint to the cc
        cmds.parent(digit_jnt, joint_cc)

    elif digit_jnt.find('2') != -1:
        # parent the cc_grp to the digit group
        cmds.parent(joint_cc_grp, digit_jnt.replace('2','1'))
        # parent joint to the cc
        cmds.parent(digit_jnt, joint_cc)

        # locks the specified transform channels
        for channel in NamingConventionEnums.LOCK_CHANNLES['digits']:
            gu.lock_channels(joint_cc, channel)

    elif digit_jnt.find('3') != -1:
        # parent the cc_grp to the digit group
        cmds.parent(joint_cc_grp, digit_jnt.replace('3','2'))
        # parent joint to the cc
        cmds.parent(digit_jnt, joint_cc)

        # locks the specified transform channels
        for channel in NamingConventionEnums.LOCK_CHANNLES['digits']:
            gu.lock_channels(joint_cc, channel)

def setup_toes(digit_jnt, side):
    """
    sets up the finger controls
    :param digit_jnt: name of the finger joint
    :type: str
    :param side of the body (left or right enum)
    :type: str
    """
    joint_cc = digit_jnt.replace(NamingConventionEnums.JOINT_SUFFIX,
                                NamingConventionEnums.CONTROL_CURVE_SUFFIX)
    joint_cc_grp = joint_cc+NamingConventionEnums.GROUP_SUFFIX
    ball_jnt = side+'ball'+NamingConventionEnums.BIND_JOINT_SUFFIX

    if digit_jnt.find('1') != -1:
        # parent cc_grp to digit group
        cmds.parent(joint_cc_grp, ball_jnt)
        # parent joint to the cc
        cmds.parent(digit_jnt, joint_cc)

    elif digit_jnt.find('2') != -1:
        # parent cc_grp to digit group
        cmds.parent(joint_cc_grp, digit_jnt.replace('2','1'))
        # parent joint to the cc
        cmds.parent(digit_jnt, joint_cc)
        # locks the specified transform channels
        for channel in NamingConventionEnums.LOCK_CHANNLES['digits']:
            gu.lock_channels(joint_cc, channel)

def setup_reverse_foot(ball_jnt):
    """
    makes the reverse foot

    :param ball_jnt: name of the ball joint
    :type: str
    """
    #gets the children of the ball joint
    all_children = cmds.listRelatives(ball_jnt, allDescendents =True)
    toes = []
    rev_jnts = {}
    for child in all_children:
        #seperate the reverse foot joints from the toes
        if child.find('__REVERSE__') != -1:
            if child.find('heel') != -1:
                rev_jnts['heel'] = child
            elif child.find('bankIn') != -1:
                rev_jnts['bankIn'] = child
            elif child.find('bankOut') != -1:
                rev_jnts['bankOut'] = child
            elif child.find('toe') != -1:
                rev_jnts['toe'] = child
        else:
            toes.append(child)

    #get the ankle jnt
    ankle_jnt = cmds.listRelatives(ball_jnt, parent=True)[0]

    #add ankle and ball to the rev_jnts dict
    rev_jnts['ankle'] = ankle_jnt
    rev_jnts['ball'] = ball_jnt

    #for each rev jnt make the empty group at the correct position
    rev_grps = {}
    for item in rev_jnts:
        #get the group name
        grp_name_temp = rev_jnts[item].replace('__REVERSE__', '')
        grp_name = grp_name_temp.replace(NamingConventionEnums.JOINT_SUFFIX,
                                    NamingConventionEnums.GROUP_SUFFIX)
        #make the group
        cmds.group(empty=True, name= grp_name)
        gu.place_on(grp_name, rev_jnts[item])
        cmds.makeIdentity(grp_name, apply=True, translate=True, rotate=True,
                          scale=True, normal=False, preserveNormals=1)
        #adds the group to the new dict to set up the hierarchy
        rev_grps[item] = grp_name

    #deletes the extra rev joints
    for item in rev_jnts:
        if rev_jnts[item].find('__REVERSE__') != -1 and cmds.objExists(rev_jnts[item]):
            cmds.delete(rev_jnts[item])

    #grabs the ik control and the actual ik to setup hierarchy
    ik_cc = ankle_jnt.replace(NamingConventionEnums.JOINT_SUFFIX, '_IK' +
                              NamingConventionEnums.CONTROL_CURVE_SUFFIX)
    ik_handle = ankle_jnt.replace(NamingConventionEnums.JOINT_SUFFIX, '_RPIK')

    #setup the hierarchy
    cmds.parent(ik_handle, rev_grps['ankle'])
    cmds.parent(rev_grps['ankle'], rev_grps['ball'])
    cmds.parent(rev_grps['ball'], rev_grps['toe'])
    cmds.parent(rev_grps['toe'], rev_grps['heel'])
    cmds.parent(rev_grps['heel'], rev_grps['bankOut'])
    cmds.parent(rev_grps['bankOut'], rev_grps['bankIn'])
    rev_grp = cmds.group(rev_grps['bankIn'],
                         name = rev_grps['bankIn'].replace('bankIn', 'revFoot'))
    cmds.parent(rev_grp, ik_cc)

    #get the foot controller with the rev controls on it and parent it to the ankle
    side = ball_jnt.split('_', 1)[0]
    foot_cc = side + '_foot' + NamingConventionEnums.CONTROL_CURVE_SUFFIX
    foot_cc_grp = cmds.listRelatives(foot_cc, parent = True)[0]

    #dupelicate the ankle joint and parent the dupe and ball under the old ankle
    dupe = cmds.duplicate(ankle_jnt, renameChildren = True)
    to_delete = cmds.listRelatives(dupe[0], allDescendents = True)
    cmds.delete(to_delete)
    new_name = dupe[0].replace(NamingConventionEnums.JOINT_SUFFIX,
                               NamingConventionEnums.BIND_JOINT_SUFFIX)
    new_name = new_name.replace('1', '')
    ankle_dupe = cmds.rename(dupe[0], new_name)
    #parent the ball under the new ankle and the new ankle under the original
    cmds.parent(ankle_dupe, ankle_jnt)
    cmds.parent(ball_jnt, ankle_dupe)
    cmds.parent(foot_cc_grp, ankle_dupe)

    #find the fk ankle
    fk_ankle = ankle_jnt.replace(NamingConventionEnums.JOINT_SUFFIX,
                                 '_FK' + NamingConventionEnums.JOINT_SUFFIX)

    #get the reverse node from the ikfk switch
    rev_node = ankle_jnt + '_REV'

    #get the ball controller and make a buffer group for it
    ball_cc = ball_jnt.replace(NamingConventionEnums.JOINT_SUFFIX, '_FK' +
                               NamingConventionEnums.CONTROL_CURVE_SUFFIX)
    gu.unlock_all_channels(ball_cc)
    ball_cc_grp = gu.create_buffer(ball_cc)
    for channel in NamingConventionEnums.LOCK_CHANNLES['ball']:
        gu.lock_channels(ball_cc, channel)

    #makes the single chain ik solver on the foot so the ball follows properly
    cmds.select(ball_jnt, replace=True)
    cmds.select(ankle_dupe, add=True)
    ik_names = cmds.ikHandle(solver = 'ikSCsolver')
    #rename the ikhandle and the effector
    base = ball_jnt.rsplit('_', 1)[0]
    ik_handle = cmds.rename(ik_names[0], base + '_SCIK')
    cmds.rename(ik_names[1], base + '_Effector')
    #parent the constrain the ik handle to follow the proper objs depending on ik or fk
    const_name = ik_handle + NamingConventionEnums.CONSTRAIN_SUFFIX
    gu.parent_const([fk_ankle, rev_grps['ball']], ik_handle, const_name,
                    maintain_offset = True)
    #connect the weights of the two constraints to the ik fk switch
    cmds.connectAttr(foot_cc + '.ikFkSwitch', const_name + '.' + rev_grps['ball'] + 'W1')
    cmds.connectAttr(rev_node + '.outputX', const_name + '.' + fk_ankle + 'W0')

    #constrain the ball control to the ball jnt
    gu.orient_const(ball_cc, ball_jnt, ball_jnt + NamingConventionEnums.CONSTRAIN_SUFFIX,
                    maintain_offset=True)
    ball_grp_const = ball_cc_grp + NamingConventionEnums.CONSTRAIN_SUFFIX
    gu.parent_const([fk_ankle, rev_grps['toe']], ball_cc_grp, ball_grp_const,
                    maintain_offset = True)
    #connect the weights of the ball grp's two constraints to the ik fk switch
    cmds.connectAttr(foot_cc + '.ikFkSwitch', ball_grp_const+ '.'+ rev_grps['toe'] + 'W1')
    cmds.connectAttr(rev_node + '.outputX', ball_grp_const + '.' + fk_ankle + 'W0')

    #connect all of the rev attrs from the foot control to the objs
    #create a new plusMinusAverage node so i dont have have to connect ikfk switch
    # into all 3 channels on the multiplyDivide nodes everytime
    pass_node = cmds.shadingNode('plusMinusAverage', asUtility=True,
                              name=foot_cc + '_Pass_PMA')
    cmds.connectAttr(foot_cc + '.ikFkSwitch', pass_node + '.input3D[0].input3Dx')
    cmds.connectAttr(foot_cc + '.ikFkSwitch', pass_node + '.input3D[0].input3Dy')
    cmds.connectAttr(foot_cc + '.ikFkSwitch', pass_node + '.input3D[0].input3Dz')

    #make first mult and connect the ikfk pass node to it
    mult01 = cmds.shadingNode('multiplyDivide', asUtility=True,
                              name=foot_cc + '_onOff_MULT')
    cmds.connectAttr(pass_node + '.output3D', mult01 + '.input2')
    #connect the rev controls to the mult now and the mult to the group
    #ball roll
    cmds.connectAttr(foot_cc + '.ballRoll', mult01 + '.input1X')
    cmds.connectAttr(mult01 + '.outputX',
                     rev_grps['ball'] + '.' + MayaCommandEnums.ROTATION_X)
    #toe roll
    cmds.connectAttr(foot_cc + '.toeRoll', mult01 + '.input1Y')
    cmds.connectAttr(mult01 + '.outputY',
                     rev_grps['toe'] + '.' + MayaCommandEnums.ROTATION_X)
    #heel roll
    cmds.connectAttr(foot_cc + '.heelRoll', mult01 + '.input1Z')
    cmds.connectAttr(mult01 + '.outputZ',
                     rev_grps['heel'] + '.' + MayaCommandEnums.ROTATION_X)

    #make a new mult node
    mult02 = cmds.shadingNode('multiplyDivide', asUtility=True,
                              name=foot_cc + '_onOff_MULT')
    cmds.connectAttr(pass_node + '.output3D', mult02 + '.input2')

    #toe pivot
    cmds.connectAttr(foot_cc + '.toePivot', mult02 + '.input1X')
    cmds.connectAttr(mult02 + '.outputX',
                     rev_grps['toe'] + '.' + MayaCommandEnums.ROTATION_Y)
    #heel pivot
    cmds.connectAttr(foot_cc + '.heelPivot', mult02 + '.input1Y')
    cmds.connectAttr(mult02 + '.outputY',
                     rev_grps['heel'] + '.' + MayaCommandEnums.ROTATION_Y)
    #bank
    cmds.connectAttr(foot_cc + '.bank', mult02 + '.input1Z')
    cmds.connectAttr(mult02 + '.outputZ',
                     rev_grps['bankIn'] + '.' + MayaCommandEnums.ROTATION_Z)
    cmds.connectAttr(mult02 + '.outputZ',
                     rev_grps['bankOut'] + '.' + MayaCommandEnums.ROTATION_Z)
    #lock the transforms on the bank so it works and the right side is locked inverse

    if foot_cc.startswith(NamingConventionEnums.RIGHT):
        cmds.transformLimits(rev_grps['bankIn'], enableRotationZ=(False, True),
                             rotationZ=(0, 0))
        cmds.transformLimits(rev_grps['bankOut'], enableRotationZ=(True, False),
                         rotationZ=(0, 0))
    else:
        cmds.transformLimits(rev_grps['bankIn'], enableRotationZ=(True, False),
                             rotationZ=(0, 0))
        cmds.transformLimits(rev_grps['bankOut'], enableRotationZ=(False, True),
                             rotationZ=(0, 0))

    #parent the foot controls and iks to the rig hierarchy
    cmds.parent(ball_cc_grp, NamingConventionEnums.RIG_HIERARCHY[8])
    cmds.parent(ik_handle, NamingConventionEnums.RIG_HIERARCHY[9])

    #rename the ball to bind suffix
    bind_name = ball_jnt.replace(NamingConventionEnums.JOINT_SUFFIX,
                                 NamingConventionEnums.BIND_JOINT_SUFFIX)
    cmds.rename(ball_jnt, bind_name)


def setup_spine(pelvis_jnt, num_vertebrae):
    """
    sets up the spine rig

    :param pelvis_jnt: name of the pelvis joint
    :type: str

    :param num_vertebrae: number of vertebrae
    :type: int
    """
    pelvis_cc = 'pelvis' + NamingConventionEnums.CONTROL_CURVE_SUFFIX

    num_vertebrae -=1

    mid = int(math.ceil(num_vertebrae/2.0))
    #get all the spine joints and add them to a list
    spine_jnts = [pelvis_jnt]
    cmds.select(pelvis_jnt)
    for i in range(0, num_vertebrae):
        cmds.pickWalk(direction = 'down')
        spine_jnts.extend(cmds.ls(selection = True))

    #create the curve that will be lofted
    crv_name = 'spine_CRV'
    points = 'point = ['
    count = 0
    for jnt in spine_jnts:
        pos = cmds.xform(jnt, query = True, worldSpace = True, translation = True)
        if count != 0:
            points += ',(' + str(pos[0]) + ',' + str(pos[1]) + ',' + str(pos[2]) + ')'
            count += 1
        else:
            points += '(' + str(pos[0]) + ',' + str(pos[1]) + ',' + str(pos[2]) + ')'
            count += 1


    points += ']'
    to_run = 'cmds.curve(degree=3,' + points + ',name = \''+crv_name+'\')'
    exec to_run

    #dupe the crv then move both to loft the crv to create the ribbon
    ribbon_name = 'spine_ribbon_SRFC'

    cmds.parent(crv_name, 'fake_rig_CC')
    cmds.xform(crv_name, translation = (5, 0, 0), relative = True)
    dupe_crv = cmds.duplicate(crv_name)
    cmds.xform(dupe_crv, translation=(-10, 0, 0), relative=True)
    cmds.loft(crv_name, dupe_crv, constructionHistory = 1, uniform = 1, close = 0,
              autoReverse = 1, degree = 3, sectionSpans = 1, range = 0, polygon = 0,
              reverseSurfaceNormals = True, name = ribbon_name)

    #make the follicles on the surface
    #get the locations of the joints to make the follicles right on their pos
    #use closest point on surface to get the uv cords of the joints on the lofted surface
    closest_point_node = cmds.createNode("closestPointOnSurface",
                                         name = 'temp_closest_point')
    #connect the lofted surface into the closest point node
    cmds.connectAttr(ribbon_name +'Shape.worldSpace[0]',
                     closest_point_node+'.inputSurface')

    #get a decompose matrix node to get the joints world positions and connect that to the
    #closest point node
    decomp_matrix_node = cmds.shadingNode('decomposeMatrix', asUtility = True)

    cmds.connectAttr(decomp_matrix_node+'.outputTranslate',
                     closest_point_node+'.inPosition')

    #for each joint connect it to the decomp matrix and save the uv cords of the ribbon
    pos_list = []
    for jnt in spine_jnts:
        cmds.connectAttr(jnt + '.worldMatrix[0]' ,decomp_matrix_node + '.inputMatrix',
                         force = True)
        uv = []
        uv.append(cmds.getAttr(closest_point_node + '.parameterU'))
        uv.append(cmds.getAttr(closest_point_node + '.parameterV'))
        pos_list.append(uv)

    #select all the surface points from the list
    for pos in pos_list:
        cmds.select(ribbon_name + '.uv[' + str(pos[0]) + '][' + str(pos[1]) + ']',
                    add = True)

    #create the hair at the selected postions
    mel.eval('createHair '+str(num_vertebrae)+' 1 10 0 0 1 1 5 0 2 2 2')

    #delete the extra stuff that was made and rename the stuff we want
    cmds.delete('hairSystem1', 'hairSystem1OutputCurves', 'nucleus1')
    follicle_grp = cmds.rename('hairSystem1Follicles', 'spine_follicles' +
                               NamingConventionEnums.GROUP_SUFFIX)
    follicles_list = cmds.listRelatives(follicle_grp, children=True)
    bind_jnts = []

    for i in range(len(follicles_list)):
        #duplicate each jnt and parent them under the follicle and rename the new joints
        dupe = cmds.duplicate(spine_jnts[i], renameChildren=True)[0]
        to_delete_dupe = cmds.listRelatives(dupe, allDescendents = True)
        cmds.delete(to_delete_dupe)
        new_name = dupe.replace(NamingConventionEnums.JOINT_SUFFIX,
                               NamingConventionEnums.BIND_JOINT_SUFFIX)
        new_name = new_name.rstrip('1')
        cmds.rename(dupe, new_name)

        #parent the joint under the follicle and delete the extra node that is left over
        # from the creation
        to_delete_curve = cmds.listRelatives(follicles_list[i], allDescendents=True,
                                             type = 'transform')
        cmds.delete(to_delete_curve)
        cmds.parent(new_name, follicles_list[i])
        bind_jnts.append(new_name)

    #create the 3 joints that will be bound to the ribbon
    controls_list = []
    controls_buffer_list = []
    ribbon_jnts = []
    for name in NamingConventionEnums.SPINE_CTRLS:
        control_name = name + NamingConventionEnums.CONTROL_CURVE_SUFFIX
        jnt_name = name + '_IK' + NamingConventionEnums.JOINT_SUFFIX

        #reorient the control to the world
        gu.unlock_all_channels(control_name)
        cmds.select(control_name)
        cmds.pickWalk(direction = 'up')
        control_buffer = cmds.ls(selection = True)
        cmds.makeIdentity(control_buffer, apply=True, translate=True, rotate=True,
                          scale=True, normal=False, preserveNormals=1)

        for channel in MayaCommandEnums.SCALE:
            gu.lock_channels(control_name, channel)

        cmds.select(clear=True)
        controls_list.append(control_name)
        controls_buffer_list.append(control_buffer)
        ribbon_jnts.append(jnt_name)

        cmds.joint(name = jnt_name, position = (0,0,0))
        gu.place_on(jnt_name, control_name)
        cmds.parent(jnt_name, control_name)

    #bind the ribbon jnts to the ribbon
    #select the joints
    for jnt in ribbon_jnts:
        cmds.select(jnt, add= True)
    #select the ribbon
    cmds.select(ribbon_name, add = True)
    cmds.skinCluster(toSelectedBones = True, bindMethod = 0, maximumInfluences = 2)

    #add the back controls
    #lock the controls
    back_cc = 'back' + NamingConventionEnums.CONTROL_CURVE_SUFFIX
    gu.unlock_all_channels(back_cc)
    back_buffer = cmds.listRelatives(back_cc, parent = True)[0]
    gu.lock_all_channels(back_cc)

    #add all the attrs for the back control
    back_attrs = [['backLoCurl', 'backMidCurl', 'backHiCurl'],
                  ['backLoSide', 'backMidSide', 'backHiSide'],
                  ['backLoTwist', 'backMidTwist', 'backHiTwist'],
                  ['revBackLoCurl', 'revBackMidCurl', 'revBackHiCurl'],
                  ['revBackLoSide', 'revBackMidSide', 'revBackHiSide'],
                  ['revBackLoTwist', 'revBackMidTwist', 'revBackHiTwist']]
    count = 5
    for attr_set in back_attrs:
        for attr in attr_set:
            cmds.addAttr(back_cc, longName=attr, attributeType='float')
            cmds.setAttr(back_cc + '.' + attr, keyable=True)
        #add a filler line to make it pretty
        temp = ''
        temp = temp.zfill(count)
        temp = temp.replace('0', '_')
        cmds.addAttr(back_cc, longName=temp, attributeType='float')
        cmds.setAttr(back_cc + '.' + temp, keyable=False, channelBox = True)
        count+=1
    cmds.deleteAttr(back_cc + '.' + temp)

    #make the rev spine joints
    rev_jnts = []
    dupe = cmds.duplicate(pelvis_jnt, renameChildren=True)[0]
    to_delete_dupe = cmds.listRelatives(dupe, allDescendents=True)
    for item in to_delete_dupe:
        if item.find('spine') != -1:
            rev_jnts.append(item)

    for rev_jnt in rev_jnts:
        to_delete_dupe.remove(rev_jnt)

    rev_jnts.append(dupe)

    #rename the rev_jnts
    for i in range(len(rev_jnts)):
        new_name = rev_jnts[i].replace(NamingConventionEnums.JOINT_SUFFIX,
                                       '_REV' + NamingConventionEnums.JOINT_SUFFIX)
        new_name = new_name.rstrip('1')
        cmds.rename(rev_jnts[i], new_name)
        rev_jnts[i] = new_name

    cmds.delete(to_delete_dupe)

    #flip the reverse joints and parent it under the original spine
    cmds.select(rev_jnts[0])
    cmds.RerootSkeleton()

    cmds.parent(rev_jnts[0], spine_jnts[-1])


    #parent the IK controls to the rev spine
    cmds.parent(controls_buffer_list[0], rev_jnts[-1])
    cmds.parent(controls_buffer_list[1], rev_jnts[mid - 1])
    cmds.parent(controls_buffer_list[2], rev_jnts[0])

    #for connecting the back controls make a high mid and low joint
    back_jnts = [[spine_jnts[mid - 1], spine_jnts[mid], spine_jnts[mid +1]],
                 [rev_jnts[mid+1], rev_jnts[mid], rev_jnts[mid -1]]]

    #nodes to make the rev spine follow the forward spine
    rev_mult_nodes = []
    rev_pma_nodes = []

    #create the multiply nodes and the plus minus average nodes
    for item in back_jnts[1]:
        name_pma = item + '_Follow_PMA'
        cmds.shadingNode('plusMinusAverage', asUtility = True, name = name_pma)
        rev_pma_nodes.append(name_pma)

        name_mult = item + '_Follow_MULT'
        cmds.shadingNode('multiplyDivide', asUtility = True, name=name_mult)
        rev_mult_nodes.append(name_mult)
        cmds.setAttr(name_mult + '.input2X', -1)
        cmds.setAttr(name_mult + '.input2Y', -1)
        cmds.setAttr(name_mult + '.input2Z', -1)

    #loop through the back attrs and attach them to the joints
    for i in range(len(back_attrs)):
        for j in range(len(back_attrs[i])):
            #make the attr string
            attr = back_cc + '.' + back_attrs[i][j]
            #get which channel to connect to based on the order of back attrs
            channel = ''
            if i % 3 == 0:
                channel = 'z'
            elif i % 3 == 1:
                channel = 'y'
            else:
                channel = 'x'

            #for the first 3 loops connect to the regular spine then last 3 iterations
            # to the reverse spine
            if i < 3:
                #connmect the attr to the spine joints appropriate control
                jnt_channel = back_jnts[0][j] + '.r' + channel
                cmds.connectAttr(attr, jnt_channel)
                #feed the spine jnt rotate into the multiply node for this node
                cmds.connectAttr(jnt_channel,
                                 rev_mult_nodes[j] + '.input1' + channel.upper())
            else:
                pma_attr_in_1 = rev_pma_nodes[j] + '.input3D[0].input3D' + channel
                pma_attr_in_2 = rev_pma_nodes[j] + '.input3D[1].input3D' + channel
                pma_attr_out = rev_pma_nodes[j] + '.output3D.output3D' + channel
                cmds.connectAttr(attr, pma_attr_in_1)
                cmds.connectAttr(rev_mult_nodes[j] + '.output' + channel.upper(),
                                 pma_attr_in_2, force = True)
                jnt_channel = back_jnts[1][j] + '.r' + channel
                cmds.connectAttr(pma_attr_out, jnt_channel)

    #parent the back control under the pelvis control
    cmds.parent(back_buffer,pelvis_cc)

    #parent the spine into the rig hierarchy
    #make a group for the spine extra nodes
    cmds.delete(dupe_crv)
    spine_extra_grp = cmds.group(ribbon_name, follicle_grp, crv_name,
               name = 'spine_extra' + NamingConventionEnums.GROUP_SUFFIX)
    cmds.parent(spine_extra_grp, NamingConventionEnums.RIG_HIERARCHY[12])

    #parent the joints under the pelvis control
    pelvis_buffer = cmds.listRelatives(pelvis_cc, parent = True)[0]
    cmds.parent(pelvis_jnt, pelvis_cc)
    #parent the pelvis cc into the rig hierarchy
    cmds.parent(pelvis_buffer, NamingConventionEnums.RIG_HIERARCHY[7])
