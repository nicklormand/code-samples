#!/usr/bin/env python
#SETMODE 777

#----------------------------------------------------------------------------------------#
#------------------------------------------------------------------------------ HEADER --#

"""
:author:
   F

:synopsis:
    Makes a GUI to create a rig for the user

:description:
    makes a gui with 3 phases to intake info from the user and make a rig, first checks
    the maya scene to see if the gui has been run before and enables the proper phase.
    Also runs the code for mirroring and binding.

:applications:
   Maya

:see_also:
    step_one
    step_two
    step_three
    gen_utils
    maya_enums
"""

#----------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------- IMPORTS --#

# Default Python Imports
from PySide2.QtCore import Qt
from PySide2 import QtWidgets, QtGui
from maya import OpenMayaUI as omui
from shiboken2 import wrapInstance
import maya.cmds as cmds

# Imports That You Wrote
import auto_rigger.step_one as step_one
import auto_rigger.step_two as step_two
import auto_rigger.step_three as step_three
import auto_rigger.gen_utils as gu
from auto_rigger.maya_enums import MayaCommandEnums, NamingConventionEnums
#----------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------- FUNCTIONS --#
def get_maya_window():
    """
    this gets a pointer to the maya window

    :return: pointer to maya window
    :type: pointer
    """
    maya_main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(maya_main_window_ptr), QtWidgets.QWidget)
#----------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------- CLASSES --#

class AutoRiggerGUI(QtWidgets.QDialog):
    """
    This class builds the GUI for the auto rigger
    """
    def __init__(self):
        QtWidgets.QDialog.__init__(self, parent=get_maya_window())
        #make the line edits to intake the prefixes
        self.left_prefix_le = None
        self.right_prefix_le = None
        #a variable to save the prefix choice
        self.left_prefix = None
        self.right_prefix = None
        #make the spin to intake the number of joints to make
        self.num_fingers_sb = None
        self.num_toes_sb = None
        self.num_vertebrae_sb = None
        #a variable to save the number of vertebrae
        self.num_vertebrae = None
        #make the comboboxes to intake the color choices
        self.left_side_color_cb = None
        self.right_side_color_cb = None
        self.center_color_cb = None
        # a variable to save the colors of the sides
        self.left_side_color = None
        self.right_side_color = None
        self.center_color = None
        # make the comboboxes to intake the control style choices
        self.fk_control_style_cb = None
        self.ik_control_style_cb = None
        #variables to save the outputs from steps 1 and 2 for later use
        self.joint_structure = None
        self.joint_list = None
        self.cc_list = None
        #makes the layouts that will be used
        self.main_vb = None
        self.step_one_layout = None
        self.step_two_layout = None
        self.step_three_layout = None
        #makes the layouts of the extra buttons and to control the xray feature
        self.mirror_vb = None
        self.xray_vb = None
        self.xray_btn = None
        self.xray_objs = []
        self.xray_on = False
        self.bind_btn = None

        self.step = ''

    def init_gui(self):
        """
        Displays the GUI to the user
        """
        #checks to see if there are items in the scene that were made by the tool
        main_cc = 'fake_rig' + NamingConventionEnums.CONTROL_CURVE_SUFFIX
        master_group = NamingConventionEnums.RIG_HIERARCHY[0]
        #checks if the master_group has been made from step 3 and sets step to bind
        if cmds.objExists(master_group):
            self.step = 'bind'
        #if the master node hasn't been made then check if the main_cc has been made
        elif cmds.objExists(main_cc):
            #get all the previous values from the step thats already been run and save
            # them to the class variables
            self.right_prefix = cmds.getAttr(main_cc + '.right_prefix')
            self.left_prefix = cmds.getAttr(main_cc + '.left_prefix')
            NamingConventionEnums.LEFT = self.left_prefix
            NamingConventionEnums.RIGHT = self.right_prefix

            self.left_side_color = cmds.getAttr(main_cc + '.left_side_color')
            self.right_side_color = cmds.getAttr(main_cc + '.right_side_color')
            self.center_color = cmds.getAttr(main_cc + '.center_color')
            self.num_vertebrae = int(cmds.getAttr(main_cc + '.num_vertebrae'))

            #check if the main_cc has the step 2 attribute
            if cmds.attributeQuery(NamingConventionEnums.STEP_TWO_ATTR,
                                               node = main_cc,exists=True):
                #set step to 3 and get and save the controls that were made in step 2
                self.step = '3'
                self.cc_list = cmds.listRelatives\
                    (main_cc + '|controls'+ NamingConventionEnums.GROUP_SUFFIX,
                     shapes=False, allDescendents=True, type = 'transform')
            #else then make step = 2
            else:
                self.step = '2'
        #if neither main_cc or master node have been made then set step to 1
        else:
            self.step = '1'

        #creats the main layout as if step 1 is being run
        self.main_vb = QtWidgets.QVBoxLayout(self)

        self.step_one_layout = self.create_step_one()

        self.step_two_layout = self.create_step_two()
        self.disable_layout(self.step_two_layout)

        self.step_three_layout = self.create_step_three()
        self.disable_layout(self.step_three_layout)

        #mirror buttons
        self.mirror_l_to_r_btn = QtWidgets.QPushButton('Mirror L -> R')
        self.mirror_l_to_r_btn.clicked.connect(self.mirror_l_to_r)

        self.mirror_r_to_l_btn = QtWidgets.QPushButton('Mirror R -> L')
        self.mirror_r_to_l_btn.clicked.connect(self.mirror_r_to_l)

        self.mirror_vb = QtWidgets.QHBoxLayout()
        self.mirror_vb.addWidget(self.mirror_l_to_r_btn)
        self.mirror_vb.addWidget(self.mirror_r_to_l_btn)
        self.disable_layout(self.mirror_vb)

        # model transparency button
        self.xray_btn = QtWidgets.QPushButton('X-Ray Model')
        self.xray_btn.clicked.connect(self.xray_model)

        self.xray_vb = QtWidgets.QHBoxLayout()
        self.xray_vb.addWidget(self.xray_btn)
        self.disable_layout(self.xray_vb)

        #creates the extra buttons
        cancel_btn = QtWidgets.QPushButton('Cancel')
        cancel_btn.setStyleSheet('background-color: red')
        cancel_btn.clicked.connect(self.close)

        #creates the layout main
        self.main_vb.addLayout(self.step_one_layout)
        self.main_vb.addLayout(self.mirror_vb)
        self.main_vb.addLayout(self.xray_vb)
        self.main_vb.addLayout(self.step_two_layout)
        self.main_vb.addLayout(self.step_three_layout)
        self.main_vb.addWidget(cancel_btn)

        #add min/max
        self.setWindowFlags(Qt.Window
                            | Qt.WindowSystemMenuHint
                            | Qt.WindowMinimizeButtonHint
                            | Qt.WindowCloseButtonHint)

        # display the window to the user
        self.setGeometry(300, 300, 400, 200)
        self.setFixedSize(400, 600)
        self.setWindowTitle('Auto Rigger')
        self.show()

        # Enable and disable parts of the gui, based on where the user left off
        if self.step == '2':
            self.disable_layout(self.step_one_layout)
            self.enable_layout(self.step_two_layout)
            self.enable_layout(self.mirror_vb)
            self.enable_layout(self.xray_vb)
        elif self.step == '3':
            self.disable_layout(self.step_one_layout)
            self.disable_layout(self.step_two_layout)
            self.enable_layout(self.step_three_layout)
            self.bind_btn.setEnabled(False)
            self.mirror_vb.setEnabled(True)
            self.mirror_l_to_r_btn.setEnabled(True)
            self.mirror_r_to_l_btn.setEnabled(True)
            self.xray_btn.setEnabled(True)
        elif self.step == 'bind':
            self.disable_layout(self.step_one_layout)
            self.mirror_vb.setEnabled(False)
            self.mirror_l_to_r_btn.setEnabled(False)
            self.mirror_r_to_l_btn.setEnabled(False)
            self.disable_layout(self.step_three_layout)
            self.bind_btn.setEnabled(True)





    def create_step_one(self):
        """
        This creates a QVBoxLayout for the  first step of the auto rigger

        :return: QVBoxLayout with all of step one
        :type: QVBoxLayout
        """
        # first step layout
        step_one_lbl = QtWidgets.QLabel('Step 1: Create and Position Guides')

        #creates the naming conventions line edits
        left_prefix_lbl = QtWidgets.QLabel('Left side prefix: ')
        self.left_prefix_le = QtWidgets.QLineEdit(NamingConventionEnums.LEFT)
        left_prefix_hb = QtWidgets.QHBoxLayout()
        left_prefix_hb.addWidget(left_prefix_lbl)
        left_prefix_hb.addWidget(self.left_prefix_le)

        right_prefix_lbl = QtWidgets.QLabel('Right side prefix: ')
        self.right_prefix_le = QtWidgets.QLineEdit(NamingConventionEnums.RIGHT)
        right_prefix_hb = QtWidgets.QHBoxLayout()
        right_prefix_hb.addWidget(right_prefix_lbl)
        right_prefix_hb.addWidget(self.right_prefix_le)

        # spin boxes to get num of fingers, toes, and vertebrae
        num_fingers_lbl = QtWidgets.QLabel('Number of Fingers: ')
        self.num_fingers_sb = QtWidgets.QSpinBox()
        self.num_fingers_sb.setValue(5)
        self.num_fingers_sb.setRange(0, 5)
        num_fingers_hb = QtWidgets.QHBoxLayout()
        num_fingers_hb.addWidget(num_fingers_lbl)
        num_fingers_hb.addWidget(self.num_fingers_sb)

        num_toes_lbl = QtWidgets.QLabel('Number of Toes: ')
        self.num_toes_sb = QtWidgets.QSpinBox()
        self.num_toes_sb.setValue(0)
        self.num_toes_sb.setRange(0, 5)
        num_toe_hb = QtWidgets.QHBoxLayout()
        num_toe_hb.addWidget(num_toes_lbl)
        num_toe_hb.addWidget(self.num_toes_sb)

        num_vertebrae_lbl = QtWidgets.QLabel('Number of Vertebrae: ')
        self.num_vertebrae_sb = QtWidgets.QSpinBox()
        self.num_vertebrae_sb.setValue(5)
        self.num_vertebrae_sb.setRange(3, 7)
        num_vertebrae_hb = QtWidgets.QHBoxLayout()
        num_vertebrae_hb.addWidget(num_vertebrae_lbl)
        num_vertebrae_hb.addWidget(self.num_vertebrae_sb)

        # creates combo boxes to get the color for each side
        left_side_color_lbl = QtWidgets.QLabel('Left Side Controls Color: ')
        self.left_side_color_cb = QtWidgets.QComboBox()
        self.left_side_color_cb.addItems(['Red', 'Blue', 'Yellow'])
        left_side_color_hb = QtWidgets.QHBoxLayout()
        left_side_color_hb.addWidget(left_side_color_lbl)
        left_side_color_hb.addWidget(self.left_side_color_cb)

        center_color_lbl = QtWidgets.QLabel('Center Controls Color: ')
        self.center_color_cb = QtWidgets.QComboBox()
        self.center_color_cb.addItems(['Red', 'Blue', 'Yellow'])
        self.center_color_cb.setCurrentText('Yellow')
        center_color_hb = QtWidgets.QHBoxLayout()
        center_color_hb.addWidget(center_color_lbl)
        center_color_hb.addWidget(self.center_color_cb)

        right_side_color_lbl = QtWidgets.QLabel('Right Side Controls Color:')
        self.right_side_color_cb = QtWidgets.QComboBox()
        self.right_side_color_cb.addItems(['Red', 'Blue', 'Yellow'])
        self.right_side_color_cb.setCurrentText('Blue')
        right_side_color_hb = QtWidgets.QHBoxLayout()
        right_side_color_hb.addWidget(right_side_color_lbl)
        right_side_color_hb.addWidget(self.right_side_color_cb)

        # create the run step button
        step_one_btn = QtWidgets.QPushButton('Step One')
        step_one_btn.setObjectName('stepOne')
        step_one_btn.clicked.connect(self.run_step)

        #add everything to layout that gets returned
        step_one_vb = QtWidgets.QVBoxLayout()
        step_one_vb.addWidget(step_one_lbl)
        step_one_vb.addLayout(left_prefix_hb)
        step_one_vb.addLayout(right_prefix_hb)
        step_one_vb.addLayout(num_fingers_hb)
        step_one_vb.addLayout(num_toe_hb)
        step_one_vb.addLayout(num_vertebrae_hb)
        step_one_vb.addLayout(left_side_color_hb)
        step_one_vb.addLayout(center_color_hb)
        step_one_vb.addLayout(right_side_color_hb)
        step_one_vb.addWidget(step_one_btn)

        return step_one_vb

    def create_step_two(self):
        """
        This creates a QVBoxLayout for the second step of the auto rigger

        :return: QVBoxLayout with all of step one
        :type: QVBoxLayout
        """
        # second step layout
        step_two_lbl = QtWidgets.QLabel('Step 2: Create and Position Controls')

        # creates combo boxes to get the controller style for FK and IK
        fk_control_style_lbl = QtWidgets.QLabel('FK Controls Style:')
        self.fk_control_style_cb = QtWidgets.QComboBox()
        self.fk_control_style_cb.addItems(['Circle', '4-Point Star', 'Box'])
        fk_control_style_hb = QtWidgets.QHBoxLayout()
        fk_control_style_hb.addWidget(fk_control_style_lbl)
        fk_control_style_hb.addWidget(self.fk_control_style_cb)

        ik_control_style_lbl = QtWidgets.QLabel('IK Controls Style:')
        self.ik_control_style_cb = QtWidgets.QComboBox()
        self.ik_control_style_cb.addItems(['Circle', '4-Point Star', 'Box'])
        self.ik_control_style_cb.setCurrentText('4-Point Star')
        ik_control_style_hb = QtWidgets.QHBoxLayout()
        ik_control_style_hb.addWidget(ik_control_style_lbl)
        ik_control_style_hb.addWidget(self.ik_control_style_cb)

        #create the run step button
        step_two_btn = QtWidgets.QPushButton('Step Two')
        step_two_btn.setObjectName('stepTwo')
        step_two_btn.clicked.connect(self.run_step)
        step_two_btn.setDisabled(True)

        # add everything to layout that gets returned
        step_two_vb = QtWidgets.QVBoxLayout()
        step_two_vb.addWidget(step_two_lbl)
        step_two_vb.addLayout(fk_control_style_hb)
        step_two_vb.addLayout(ik_control_style_hb)
        step_two_vb.addWidget(step_two_btn)

        return step_two_vb

    def create_step_three(self):
        """
        This creates a QVBoxLayout for the third step of the auto rigger

        :return: QVBoxLayout with all of step one
        :type: QVBoxLayout
        """
        # third Step Layout
        step_three_lbl = QtWidgets.QLabel('Step 3: Make Rig!')
        step_three_btn = QtWidgets.QPushButton('Step Three')
        step_three_btn.setObjectName('stepThree')
        step_three_btn.clicked.connect(self.run_step)
        step_three_btn.setDisabled(True)

        # binding options
        self.bind_btn = QtWidgets.QPushButton('Bind Selected Mesh')
        self.bind_btn.setObjectName('bind')
        self.bind_btn.clicked.connect(self.run_step)

        # add everything to layout that gets returned
        step_three_vb = QtWidgets.QVBoxLayout()
        step_three_vb.addWidget(step_three_lbl)
        step_three_vb.addWidget(step_three_btn)
        step_three_vb.addWidget(self.bind_btn)


        return step_three_vb

    def run_step(self):
        """
        Runs the step that was clicked
        """

        #check to see if sender exist
        sender = self.sender()
        if sender:
            #check the name of sender and add the string to the correct line edit
            obj_name = str(sender.objectName())
            if obj_name == 'stepOne':
                #sets the naming convention and the colors
                self.right_prefix = self.right_prefix_le.text()
                self.left_prefix = self.left_prefix_le.text()
                NamingConventionEnums.LEFT = self.left_prefix
                NamingConventionEnums.RIGHT = self.right_prefix

                self.left_side_color = self.left_side_color_cb.currentText()
                self.right_side_color = self.right_side_color_cb.currentText()
                self.center_color = self.center_color_cb.currentText()
                self.num_vertebrae = self.num_vertebrae_sb.value()

                root = step_one.read_xml()
                self.joint_structure = step_one.Skeleton(root, self.num_fingers_sb.value()
                                    ,self.num_toes_sb.value(),
                                    self.num_vertebrae).joint_structure
                self.joint_structure.group()
                # colors the joints based on side
                self.joint_list = self.joint_structure.get_joint_list()
                #loop through joint list to color the joints based on side
                for item in self.joint_list:
                    # color based on the side
                    if item.startswith(NamingConventionEnums.RIGHT):
                        gu.set_color(item, self.right_side_color)
                    elif item.startswith(NamingConventionEnums.LEFT):
                        gu.set_color(item, self.left_side_color)
                    else:
                        gu.set_color(item, self.center_color)

                #add the user inputs to the main_cc so that if closed and reopened we
                #can still read it
                main_cc = 'fake_rig' + NamingConventionEnums.CONTROL_CURVE_SUFFIX
                cmds.addAttr('|' + main_cc, longName='num_vertebrae',
                             attributeType='float')
                cmds.setAttr(main_cc+'.num_vertebrae', self.num_vertebrae)

                cmds.addAttr('|' + main_cc, longName='left_side_color',
                             dataType='string')
                cmds.setAttr(main_cc + '.left_side_color', self.left_side_color,
                             type='string')

                cmds.addAttr('|' + main_cc, longName='right_side_color',
                             dataType='string')
                cmds.setAttr(main_cc + '.right_side_color', self.right_side_color,
                             type='string')

                cmds.addAttr('|' + main_cc, longName='center_color',
                             dataType='string')
                cmds.setAttr(main_cc + '.center_color', self.center_color, type='string')

                cmds.addAttr('|' + main_cc, longName='left_prefix',
                             dataType='string')
                cmds.setAttr(main_cc + '.left_prefix', self.left_prefix, type='string')

                cmds.addAttr('|' + main_cc, longName='right_prefix',
                             dataType='string')
                cmds.setAttr(main_cc + '.right_prefix', self.right_prefix, type='string')

                #disables step one and enables step 2
                self.disable_layout(self.step_one_layout)
                self.enable_layout(self.step_two_layout)
                self.enable_layout(self.mirror_vb)
                self.enable_layout(self.xray_vb)

            elif obj_name == 'stepTwo':
                #call step 2 run step and save the cc list
                self.cc_list = step_two.run_step(gu.get_joint_list(),
                              self.right_side_color, self.left_side_color,
                              self.center_color,self.fk_control_style_cb.currentText(),
                              self.ik_control_style_cb.currentText(), self.num_vertebrae)

                #lock transforms on the main cc
                main_cc = 'fake_rig' + NamingConventionEnums.CONTROL_CURVE_SUFFIX
                gu.lock_all_channels(main_cc)

                #disables step 2 and enables step 3
                self.disable_layout(self.step_two_layout)
                self.enable_layout(self.step_three_layout)
                self.bind_btn.setEnabled(False)

            elif obj_name == 'stepThree':

                #create the rig structure
                gu.create_hierarchy()
                #run step three
                step_three.run_step(self.cc_list, self.num_vertebrae)

                # create the move scale rotate control
                main_cc = 'fake_rig' + NamingConventionEnums.CONTROL_CURVE_SUFFIX
                cmds.delete(main_cc)

                # create global controller and set color
                new_cc_name = "moveScaleRotate01_shape"
                gu.create_four_point_arrow(new_cc_name)
                gu.set_color(new_cc_name, 'green')

                # rescale global controller based off of pelvis_CC
                pelvis_bbox = cmds.exactWorldBoundingBox('pelvis_CC')
                cc_bbox = cmds.exactWorldBoundingBox(new_cc_name)

                x_scale = (pelvis_bbox[3]-pelvis_bbox[0])/(cc_bbox[3]-cc_bbox[0])
                cmds.xform(new_cc_name, scale = (x_scale, 1, x_scale), relative = True)
                cmds.makeIdentity(apply=True, translate=1, rotate=1, scale=1, normal=0)

                # parent controller scape to moveScaleRotate01 and delete leftover curve
                obj_shape = cmds.listRelatives(shapes=True)
                cmds.parent(obj_shape, 'moveScaleRotate01', add=True, shape=True)
                cmds.delete("moveScaleRotate01_shape")

                #clean the outliner
                cmds.delete(cmds.ls('transform*', assemblies=True))

                # setup the gui for the binding step
                self.mirror_vb.setEnabled(False)
                self.mirror_l_to_r_btn.setEnabled(False)
                self.mirror_r_to_l_btn.setEnabled(False)
                self.disable_layout(self.step_three_layout)

                self.warn_user('Auto Rigger', 'The rig is complete!')
                self.bind_btn.setEnabled(True)


            #run if the bind button is called
            elif obj_name== 'bind':
                #selects all the joints
                sel = cmds.ls( type='joint')
                bind_list = []

                #makes a new list of all the joints that are BIND joints
                for joint in sel:
                    if joint.find(NamingConventionEnums.BIND_JOINT_SUFFIX) != -1:
                        bind_list.append(joint)

                #gets the selected mesh
                mesh_list = cmds.ls( selection=True )

                #if there was a mesh selected call bind with the BIND joints and mesh
                if len(mesh_list) > 0:
                    self.bind(bind_list, mesh_list)
                    self.warn_user('Auto Rigger',
                              'Your geometry has been bound to your new rig!')
                    self.close()
                else:
                    self.warn_user('Auto Rigger', 'Please select geometry to bind')


    def mirror_l_to_r(self):
        """
        Mirror the joints and controls on the left side to the right side
        """
        # get the joint list and make the list of objects to mirror
        if self.joint_structure:
            for item in self.joint_list:
                # get the opposite side of the jnt
                if item.startswith(NamingConventionEnums.LEFT):
                    # get the opposite side of the jnt
                    jnt = item.replace(NamingConventionEnums.LEFT,'', 1)
                # makes a temp object that is a mirrored version then moves the matching
                    # right side obj to the temp
                    gu.mirror(item, 'x', 'TEMP_Mirror_GRP', NamingConventionEnums.LEFT,
                              'TEMP_',
                              'fake_rig' + NamingConventionEnums.CONTROL_CURVE_SUFFIX)
                    mirror_item = cmds.listRelatives('TEMP_Mirror_GRP', children=True)[0]
                    gu.place_on(NamingConventionEnums.RIGHT + jnt, mirror_item)
                    cmds.delete('TEMP_Mirror_GRP')
        # checks if the cc list has values
        if self.cc_list:
            for item in self.cc_list:
                if item.startswith(NamingConventionEnums.LEFT):
                    # get the opposite side of the jnt
                    cc = item.replace(NamingConventionEnums.LEFT, '', 1)
                # makes a temp object that is a mirrored version then moves the matching
                    # right side obj to the temp
                    gu.mirror(item, 'x', 'TEMP_Mirror_GRP', NamingConventionEnums.LEFT,
                              'TEMP_',
                              'fake_rig' + NamingConventionEnums.CONTROL_CURVE_SUFFIX)
                    mirror_item = cmds.listRelatives('TEMP_Mirror_GRP', children=True)[0]

                    #fix foot mirror
                    if cc.find('foot') != -1:
                        cmds.parent(mirror_item, world = True)

                    gu.place_on(NamingConventionEnums.RIGHT + cc, mirror_item, True)
                    cmds.delete(mirror_item)
                    cmds.delete('TEMP_Mirror_GRP')

                    # fix the fingers mirroring
                    for finger_name in NamingConventionEnums.DIGITS:
                        if cc.find(finger_name) != -1:
                            cmds.xform(NamingConventionEnums.RIGHT + cc, scale=(1, -1, 1),
                                       relative = True)





    def mirror_r_to_l(self):
        """
        Mirror the joints and controls on the right side to the left side
        """
        # get the joint list and make the list of objects to mirror
        if self.joint_structure:
            for item in self.joint_list:
                # get the opposite side of the jnt
                if item.startswith(NamingConventionEnums.RIGHT):
                    # get the opposite side of the jnt
                    jnt = item.replace(NamingConventionEnums.RIGHT, '', 1)
                # makes a temp object that is a mirrored version then moves the matching
                    # right side obj to the temp
                    gu.mirror(item, 'x', 'TEMP_Mirror_GRP', NamingConventionEnums.RIGHT,
                              'TEMP_',
                              'fake_rig' + NamingConventionEnums.CONTROL_CURVE_SUFFIX)
                    mirror_item = cmds.listRelatives('TEMP_Mirror_GRP', children=True)[0]
                    gu.place_on(NamingConventionEnums.LEFT + jnt, mirror_item)
                    cmds.delete('TEMP_Mirror_GRP')
        if self.cc_list:
            for item in self.cc_list:
                if item.startswith(NamingConventionEnums.RIGHT):
                    # get the opposite side of the jnt
                    cc = item.replace(NamingConventionEnums.RIGHT, '')
                 # makes a temp object that is a mirrored version then moves the matching
                    # right side obj to the temp
                    gu.mirror(item, 'x', 'TEMP_Mirror_GRP', NamingConventionEnums.RIGHT,
                              'TEMP_',
                              'fake_rig' + NamingConventionEnums.CONTROL_CURVE_SUFFIX)
                    mirror_item = cmds.listRelatives('TEMP_Mirror_GRP', children=True)[0]

                    # fix foot mirror
                    if cc.find('foot') != -1:
                        cmds.parent(mirror_item, world=True)

                    gu.place_on(NamingConventionEnums.LEFT + cc, mirror_item, True)

                    cmds.delete(mirror_item)
                    cmds.delete('TEMP_Mirror_GRP')

                    #fix the fingers mirroring
                    for finger_name in NamingConventionEnums.DIGITS:
                        if cc.find(finger_name) != -1:
                            cmds.xform(NamingConventionEnums.LEFT + cc, scale=(1, 1, 1),
                                       relative = True)

    def bind(self, joint_list, mesh_list):
        """
        bind the given mesh to the given joints

        :param joint_list: list of joints
        :type: list of strings

        :param mesh_list: list of meshes
        :type: list of strings
        """
        cmds.select(clear = True)
        #loop through all the mesh and bind them one at a time
        for mesh in mesh_list:
            cmds.select(joint_list, add=True)
            cmds.select(mesh, add=True)
            cmds.skinCluster(toSelectedBones = True, bindMethod = 0, maximumInfluences = 3
                         ,obeyMaxInfluences = False, removeUnusedInfluence = True)

    def xray_model(self):
        """
        Makes the selected model semi transparent
        """
        # stores the user's selection
        sel = cmds.ls(selection=True, dagObjects=True, allPaths=True, type='surfaceShape')
        # if there is a selection and the user is currently not using the xray button
        if sel and self.xray_on is False:
            # add objecst to xray mode
            # change gui to reflect changes
            for obj in sel:
                self.xray_objs.append(obj)
                self.xray_on = True
                self.xray_btn.setStyleSheet('background-color: red')
                self.xray_btn.setText('Cancel X-ray')
                # set object to template
                gu.toggle_template(obj)
            cmds.select(clear = True)
        elif self.xray_on is True:
            # remove all objects from xray mode
            # change gui to reflect changes
            for obj in self.xray_objs:
                self.xray_on = False
                self.xray_btn.setStyleSheet('background-color: #5d5d5d')
                self.xray_btn.setText('X-ray Model')
                gu.toggle_template(obj)
            self.xray_objs = []
        else:
            # if there is no selection, select all mesh in the scene
            cmds.select(all = True )
            sel = cmds.ls(selection=True, dagObjects=True, allPaths=True,
                          type='surfaceShape')
            # if there was any mesh in the scene
            if sel:
                # set objects to xray mode
                for obj in sel:
                    self.xray_objs.append(obj)
                    self.xray_on = True
                    self.xray_btn.setStyleSheet('background-color: red')
                    self.xray_btn.setText('Cancel X-ray')
                    gu.toggle_template(obj)
                cmds.select(clear = True)
                self.warn_user('Warning', 'Putting all geometry on X-ray Mode')
            else:
                self.warn_user('Warning', 'There is no geometry in the scene')


    @classmethod
    def warn_user(cls, title, message):
        """
        this method displays a warning to the user

        :param title: The title of the message box
        :type: str

        :param message: a message for the user
        :type: str
        """
        message_box = QtWidgets.QMessageBox()
        message_box.setText(message)
        message_box.setWindowTitle(title)
        message_box.exec_()

    def disable_layout(self, layout):
        """
        disables the widgets in the given layout so the user cant break them

        :param layout: layout to disable
        :type: QLayout
        """
        #loops through each item in the given layout
        for index in range(layout.count()):
            #doesnt know the type so gets both as widget and layout
            widget = layout.itemAt(index).widget()
            new_layout = layout.itemAt(index).layout()
            #disables it if widget or recursively calls this if layout
            if widget:
                widget.setEnabled(False)
            if new_layout:
                self.disable_layout(new_layout)

    def enable_layout(self, layout):
        """
        disables the widgets in the given layout so the user cant break them

        :param layout: layout to disable
        :type: QLayout
        """
        #loops through each item in the given layout
        for index in range(layout.count()):
            #doesnt know the type so gets both as widget and layout
            widget = layout.itemAt(index).widget()
            new_layout = layout.itemAt(index).layout()
            #disables it if widget or recursively calls this if layout
            if widget:
                widget.setEnabled(True)
            if new_layout:
                self.enable_layout(new_layout)