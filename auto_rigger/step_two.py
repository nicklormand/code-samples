#!/usr/bin/env python
#SETMODE 777

#----------------------------------------------------------------------------------------#
#------------------------------------------------------------------------------ HEADER --#

"""
:author:
    Blake Day & Nick Lormand

:synopsis:
    runs step two of the auto rigger, making the controls

:description:
    takes in a list of joints, the different sides' colors and the style of the controls
    then makes the controls and moves them under the main_ cc

:applications:
    Maya

:see_also:
    step_one
    step_three
    gen_utils
    maya_enums
    auto_rig_gui
"""

#----------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------- IMPORTS --#

# Default Python Imports
import maya.cmds as cmds
import math

# Imports That You Wrote
import auto_rigger.gen_utils as gu
from maya_enums import MayaCommandEnums, NamingConventionEnums
import auto_rigger.step_one as step_one
#----------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------- FUNCTIONS --#
def run_step(joint_list, right_color, left_color, center_color, fk_style, ik_style,
             num_vertebrae):
    """
    adds box control curves to all joints

    :param joint_list: list of joints to put controls on
    :type: list

    :param right_color: color for right side objs
    :type: str

    :param left_color: color for left side objs
    :type: str

    :param fk_style: style for the fk controls
    :type: str

    :param ik_style: style for the ik controls
    :type: str

    :param num_vertebrae: number of vertebrae total so we can only make 3 controls
    :type: int

    :return: list of ccs
    """
    main_cc = 'fake_rig' + NamingConventionEnums.CONTROL_CURVE_SUFFIX
    cc_list = create_cc(joint_list, fk_style, ik_style, num_vertebrae)
    buffer_list = []
    for cc in cc_list:
        #sets color based on side
        if cc.find('pelvis') == -1:
            if cc.startswith(NamingConventionEnums.RIGHT):
                gu.set_color(cc, right_color)
                #cmds.xform(cc, rotation=(0, 0, -180), relative=True)
            elif cc.startswith(NamingConventionEnums.LEFT):
                gu.set_color(cc, left_color)
            else:
                gu.set_color(cc, center_color)
        #colors and scales the pelvis differently
        else:
            gu.set_color(cc, 'green')
            cmds.xform(cc, scale=(5, 1.2, 1.2), relative=True)
        #scale the control based on the scale of the main_cc
        cc_scale = cmds.xform(cc, scale = True, query = True, relative = True)
        main_scale = cmds.xform(main_cc, scale = True, query = True, relative = True)
        cmds.xform(cc, scale = (cc_scale[0] * main_scale[0], cc_scale[1] * main_scale[1],
                                cc_scale[2] * main_scale[2]))
    #move the controls under the main_cc
    cc_grp = cmds.group(cc_list, name = 'controls' + NamingConventionEnums.GROUP_SUFFIX)
    cmds.parent(cc_grp, main_cc)
    cmds.select(clear = True)

    # add global attr
    cmds.addAttr('|' + main_cc,
                 longName=NamingConventionEnums.STEP_TWO_ATTR, attributeType='bool')

    return cc_list

def create_cc(joint_list, fk_style, ik_style, num_vertebrae):
    """
    based on this given joint name makes the appropriate control

    :param joint_list: name of joint to make the controls on
    :type: str

    :param fk_style: style for the fk controls
    :type: str

    :param ik_style: style for the ik controls
    :type: str

    :param num_vertebrae: number of vertebrae total so we can only make 3 controls
    :type: int

    :return: list of the controls made
    """
    #creates a cc_list that will be returned
    cc_list = []

    #loops through all joints
    for jnt_name in joint_list:
        if jnt_name.find('_Tip_') == -1 \
                and NamingConventionEnums.REVERSE not in jnt_name:
            #reset make_fk and cc_name
            make_fk = True
            cc_name = ''

            #checks if it is an ik obj
            for ik_obj in NamingConventionEnums.IK_OBJS:
                if jnt_name.find(ik_obj) != -1:
                    #will still make an fk if theres an ik
                    make_fk = True

                    #get the new name for the control and create it
                    cc_name_ik = jnt_name.replace(NamingConventionEnums.FAKE_JOINT_SUFFIX
                                   ,'_IK' + NamingConventionEnums.CONTROL_CURVE_SUFFIX)
                    call_utils(cc_name_ik, ik_style)
                    cc_list.append(cc_name_ik)

                    #place the ik control in the right spot
                    gu.place_on(cc_name_ik, jnt_name)

            #checks if there is a pole vector
            for pv_obj in NamingConventionEnums.PV_OBJS:
                if jnt_name.find(pv_obj) != -1:
                    #will still make an fk if theres an Pole vector
                    make_fk = True

                    #get the new name for the control and create it
                    cc_name_pv = jnt_name.replace(NamingConventionEnums.FAKE_JOINT_SUFFIX
                                   ,'_PV' + NamingConventionEnums.CONTROL_CURVE_SUFFIX)
                    call_utils(cc_name_pv, 'PV')
                    cc_list.append(cc_name_pv)

                    #place the ik control in the right spot
                    first_obj = cmds.listRelatives(jnt_name, parent = True)[0]
                    third_obj = cmds.listRelatives(jnt_name, children = True,
                                                   type = 'transform')[0]
                    transforms = gu.place_pole_vector(first_obj, jnt_name, third_obj)
                    cmds.xform(cc_name_pv, rotation = transforms['rot'],
                               translation = transforms['trans'])

            #checks if its a finger/toe to apply that tweaker
            for finger_name in NamingConventionEnums.DIGITS:
                if jnt_name.find(finger_name) != -1:
                    #wont make an fk for finger
                    make_fk = False

                    # get the new name for the control and create it
                    cc_name = jnt_name.replace(NamingConventionEnums.FAKE_JOINT_SUFFIX,
                                               NamingConventionEnums.CONTROL_CURVE_SUFFIX)
                    call_utils(cc_name, 'finger')
                    cc_list.append(cc_name)

                    #flip fingers on right side
                    if jnt_name.startswith(NamingConventionEnums.RIGHT):
                        cmds.xform(cc_name, scale = (0, -1, 0), relative = True)

            #checks if its hand/foot to apply a box
            for box_control in NamingConventionEnums.BOX_CTRLS:
                if jnt_name.find(box_control) != -1:
                    # wont make an fk for finger
                    make_fk = False

                    # get the new name for the control and create it
                    box_cc = jnt_name.replace(NamingConventionEnums.FAKE_JOINT_SUFFIX,
                                               NamingConventionEnums.CONTROL_CURVE_SUFFIX)
                    if box_control is 'palm':
                        call_utils(box_cc, 'Box')
                        cc_name = None
                        gu.place_on(box_cc, jnt_name)
                    #make the ball control and the foot ik fk switch
                    elif box_control is 'ball':
                        make_fk = True
                        box_cc = box_cc.replace('ball', 'foot')
                        call_utils(box_cc, 'Foot')
                        point_const = 'to_delete'
                        gu.point_const(jnt_name, box_cc, point_const)
                        cmds.delete(point_const)
                    cmds.addAttr(box_cc, longName="ikFkSwitch",
                                 attributeType='enum', enumName = 'FK:IK:')
                    cmds.setAttr(box_cc + '.ikFkSwitch', keyable = True)
                    cc_list.append(box_cc)
                    # place the box control in the right spot


            #checks if it is a spine obj
            if jnt_name.find('spine') != -1:
                # wont make an fk for spines
                make_fk = False
                num = str(num_vertebrae-1)
                mid = str(int(math.ceil(num_vertebrae/2.0))-1)

                if jnt_name.find(num) != -1:
                    # set the name to chest if its the last vertebrae
                    cc_name = jnt_name.replace(NamingConventionEnums.FAKE_JOINT_SUFFIX,
                                               NamingConventionEnums.CONTROL_CURVE_SUFFIX)
                    cc_name = cc_name.replace('spine' + '_' + num,
                                              NamingConventionEnums.SPINE_CTRLS[2])
                    call_utils(cc_name, 'Box')
                    cmds.xform(cc_name, scale=(3, 20, 25))
                    cc_list.append(cc_name)

                elif jnt_name.find(mid) != -1:
                    #set the name to spine mid if its the middle jnt
                    cc_name = jnt_name.replace(NamingConventionEnums.FAKE_JOINT_SUFFIX,
                                               NamingConventionEnums.CONTROL_CURVE_SUFFIX)
                    cc_name = cc_name.replace('spine' + '_' + mid,
                                              NamingConventionEnums.SPINE_CTRLS[1])
                    call_utils(cc_name, 'Box')
                    cmds.xform(cc_name, scale=(3, 20, 25))
                    cc_list.append(cc_name)


            #checks if its the pelvis
            if jnt_name.find('pelvis') != -1:
                # wont make an fk for spines
                make_fk = False

                # get the new name for the control and create it
                cc_name = jnt_name.replace(NamingConventionEnums.FAKE_JOINT_SUFFIX,
                                           NamingConventionEnums.CONTROL_CURVE_SUFFIX)
                call_utils(cc_name, 'Box')
                cmds.xform(cc_name, scale = (3, 20, 25))
                cc_list.append(cc_name)

                # also makes the first spine control
                cc_name_spine0 = jnt_name.replace(NamingConventionEnums.FAKE_JOINT_SUFFIX,
                                           NamingConventionEnums.CONTROL_CURVE_SUFFIX)
                cc_name_spine0 = cc_name_spine0.replace('pelvis',
                                                    NamingConventionEnums.SPINE_CTRLS[0])

                call_utils(cc_name_spine0, 'Box')
                cmds.xform(cc_name_spine0, scale=(25, 3, 20))
                cc_list.append(cc_name_spine0)
                gu.place_on(cc_name_spine0, jnt_name)

                #also make the back control
                main_cc = 'fake_rig' + NamingConventionEnums.CONTROL_CURVE_SUFFIX
                main_scale = cmds.xform(main_cc, scale=True, query=True, relative=True)

                back_cc = gu.create_two_point_arrow('back' +
                                        NamingConventionEnums.CONTROL_CURVE_SUFFIX)
                gu.place_on(back_cc, jnt_name)
                cmds.xform(back_cc, translation=(0, 0, -30 * main_scale[0]),relative=True)
                cc_list.append(back_cc)


             #if it was neither a main or a finger then it gets an FK
            if make_fk:
                # get the new name for the control and create it
                cc_name = jnt_name.replace(NamingConventionEnums.FAKE_JOINT_SUFFIX,
                                      '_FK' + NamingConventionEnums.CONTROL_CURVE_SUFFIX )
                call_utils(cc_name, fk_style)
                cc_list.append(cc_name)

             # moves the control
            if 'ankle' in jnt_name:
                gu.place_on(cc_name, jnt_name)
            elif cc_name:
                gu.place_on(cc_name, jnt_name+"_locator")

        # sets the joint to template so the user cant move them
        gu.set_template(jnt_name)


    return cc_list

def call_utils(obj_name, style):
    """
    calls utils to create the obj of the given style

    :param obj_name: name of the object
    :type: str

    :param style: what way to make the obj
    :type: str
    """
    #checks the style then calls corresponding gen_util create function
    if style == 'Circle':
        gu.create_circle(obj_name, normal_x = 1)
    elif style == '4-Point Star':
        gu.create_star_control(obj_name)
    elif style == '4-Point Arrow':
        gu.create_four_point_arrow(obj_name)
    elif style == 'Box':
        gu.create_box(obj_name)
    elif style == 'finger':
        gu.create_finger_tweaker(obj_name)
    elif style == 'PV':
        gu.create_box(obj_name)
    elif style == 'Foot':
        gu.create_foot_CC(obj_name)

#----------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------- CLASSES --#

