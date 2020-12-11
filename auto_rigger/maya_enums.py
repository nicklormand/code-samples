#!/usr/bin/env python
#SETMODE 777

#----------------------------------------------------------------------------------------#
#------------------------------------------------------------------------------ HEADER --#

"""
:author:
    Nicholas Lormand & Blake Day
:synopsis:
    A bunch of enums used for the AutoRigger tool
:description:
    A bunch of enums used for the AutoRigger tool, includes maya attributes, naming
    conventions, types of controls and attributes for objects
:applications:
    Maya
:see_also:
    step_one
    step_two
    step_three
    gen_utils
    auto_rig_gui
"""

#----------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------- IMPORTS --#

#----------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------- FUNCTIONS --#

#----------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------- CLASSES --#

# used for maya command calls
class MayaCommandEnums(object):
    TRANSLATION_X = 'tx'
    TRANSLATION_Y = 'ty'
    TRANSLATION_Z = 'tz'
    TRANSLATION = ['tx', 'ty', 'tz']
    ROTATION_X = 'rx'
    ROTATION_Y = 'ry'
    ROTATION_Z = 'rz'
    ROTATION = ['rx', 'ry', 'rz']
    SCALE_X = 'sx'
    SCALE_Y = 'sy'
    SCALE_Z = 'sz'
    SCALE = ['sx', 'sy', 'sz']
    COLORS = {"blue": 6, "red": 13, "green": 14, "yellow": 17}

# used for naming objects in outliner
class NamingConventionEnums(object):
    #naming conventions
    LEFT        = 'L_'
    RIGHT       = 'R_'
    GROUP_SUFFIX = '_GRP'
    REVERSE = '__REVERSE__'
    FAKE_JOINT_SUFFIX = '_FJNT'
    JOINT_SUFFIX = '_JNT'
    BIND_JOINT_SUFFIX = '_BIND'
    CONTROL_CURVE_SUFFIX = '_CC'
    CONSTRAIN_SUFFIX = "_const"
    LOCATOR_SUFFIX = '_LOC'
    #the hierarchy for the mast rig
    RIG_HIERARCHY = ["|%s" % "AutoRig_master",
 '|AutoRig_master|moveScaleRotate01',
 '|AutoRig_master|moveScaleRotate01|moveScaleRotate02',
 '|AutoRig_master|moveScaleRotate01|moveScaleRotate02|moveScaleRotate03',
 '|AutoRig_master|geometry',
 '|AutoRig_master|geometry|boundGeo',
 '|AutoRig_master|geometry|blendShapes',
 '|AutoRig_master|moveScaleRotate01|moveScaleRotate02|moveScaleRotate03|joints',
 '|AutoRig_master|moveScaleRotate01|moveScaleRotate02|moveScaleRotate03|controlCurves',
 '|AutoRig_master|moveScaleRotate01|moveScaleRotate02|moveScaleRotate03|ikHandles',
 '|AutoRig_master|moveScaleRotate01|moveScaleRotate02|moveScaleRotate03|clusterHandles',
 '|AutoRig_master|moveScaleRotate01|moveScaleRotate02|moveScaleRotate03|extraLocalNodes',
 '|AutoRig_master|extraNodes',
 '|AutoRig_master|geometry|boundGeo|ren_GRP',
 '|AutoRig_master|geometry|boundGeo|proxy_GRP',
                     ]
    RIG_HIERARCHY_DICT = {"AutoRig_master":
                              {'moveScaleRotate01':
                                   {'moveScaleRotate02':
                                        {'moveScaleRotate03':
                                             ['joints','controlCurves', 'ikHandles',
                                              'clusterHandles', 'extraLocalNodes']
                                         }
                                    },
                               'geometry':
                                   {'blendShapes':{'boundGeo':['proxy_GRP', 'ren_GRP']}
                                   },
                               'extraNodes':''
                               }
                          }
    GRAB_CON     = 'grabCon'
    MSR_CONTROLS = RIG_HIERARCHY[1:4]

    #attr name that all objects created by auto_rigger get so that we can find them
    GLOBAL_ATTR_NAME    = 'auto_rigger_obj'
    STEP_ONE_ATTR = 'step_1'
    STEP_TWO_ATTR = 'step_2'
    STEP_THREE_ATTR = 'step_3'

    #which type of control everything gets
    IK_OBJS = ['wrist', 'ankle']
    BOX_CTRLS = ['palm', 'ball']
    SPINE_CTRLS = ['hips', 'spineMid', 'chest']
    DIGITS = ['thumb', 'index', 'middle', 'ring', 'pinky', 'big']
    PV_OBJS = ['knee', 'elbow']

    #list of which channels to lock for each control type
    LOCK_CHANNLES = {'pelvis' : MayaCommandEnums.SCALE, 'spine' : MayaCommandEnums.SCALE,
                     'FK' : MayaCommandEnums.SCALE + MayaCommandEnums.TRANSLATION,
                     'IK' : MayaCommandEnums.SCALE,
                     'thumb' : MayaCommandEnums.SCALE + MayaCommandEnums.TRANSLATION,
                     'index' : MayaCommandEnums.SCALE + MayaCommandEnums.TRANSLATION,
                     'middle' : MayaCommandEnums.SCALE + MayaCommandEnums.TRANSLATION,
                     'ring' : MayaCommandEnums.SCALE + MayaCommandEnums.TRANSLATION,
                     'pinky' : MayaCommandEnums.SCALE + MayaCommandEnums.TRANSLATION,
                     'big' : MayaCommandEnums.SCALE + MayaCommandEnums.TRANSLATION,
                     'palm' : MayaCommandEnums.SCALE + MayaCommandEnums.TRANSLATION
                              + MayaCommandEnums.ROTATION,
                     'foot' : MayaCommandEnums.SCALE + MayaCommandEnums.TRANSLATION
                              + MayaCommandEnums.ROTATION,
                     'ball' :  MayaCommandEnums.SCALE + MayaCommandEnums.TRANSLATION,
                     'elbow' : ['rx', 'rz'],
                     'knee' : ['rx', 'ry'],
                     'digits' : ['rx', 'ry'],
                     'PV' : MayaCommandEnums.SCALE + MayaCommandEnums.ROTATION}
    #controls to get extra attributes
    EXTRA_ATTRS = {'palm' : ['indexCurl', 'middleCurl', 'ringCurl', 'pinkyCurl',
                             'fingerSpread', 'thumbCurl'],
                   'foot' : ['ballRoll', 'toeRoll', 'heelRoll', 'toePivot', 'heelPivot',
                             'bank']}
    #the joints that mark the start of the ik and the joint at the end
    IK_JOINTS = {'shoulder' : 'palm', 'hip' : 'ball'}



