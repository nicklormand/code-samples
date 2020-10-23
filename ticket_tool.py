#!/usr/bin/env python
#SETMODE 777

#----------------------------------------------------------------------------------------#
#------------------------------------------------------------------------------ HEADER --#

"""
:author:
    njl160030 Nick Lormand

:synopsis:
    Makes a GUI to submit a ticket in shotgun

:description:

:applications:
   Maya

:see_also:
"""
#----------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------- IMPORTS --#

# Default Python Imports
from PySide2 import QtGui, QtWidgets, QtCore
from maya import OpenMayaUI as omui
from shiboken2 import wrapInstance
import maya.cmds as cmds
import os

# Imports That You Wrote
import shotgun_tools.sg_pipe_objects as spo
from shotgun_tools.sg_utils import get_sg_user_projects
from shotgun_tools.sg_pipe_objects import SGTicketObject, get_project_object
from shotgun_tools.sg_enums import SG_TICKET_PRIORITY, SG_TICKET_STATUS,SG_TICKET_TYPES
#----------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------- FUNCTIONS --#

def get_maya_window():
    """
    This gets a pointer to the Maya window.
    """
    maya_main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(maya_main_window_ptr), QtWidgets.QWidget)

#----------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------- CLASSES --#
class HLine(QtWidgets.QFrame):
    """
    creates an instance of a horizontal line
    """
    def __init__(self):
        QtWidgets.QFrame.__init__(self)
        """
        creates an instance of a horizontal line
        """
    def make_line(self):
        """
        Takes no arguments
	    Runs all the necessary commands to create a horizontal line that can be displayed
	    on a GUI.
        :return: HLine widget object
        """
        line = QtWidgets.QLabel()
        line.setFrameStyle(QtWidgets.QFrame.HLine | QtWidgets.QFrame.Plain)
        return line

class VLine(QtWidgets.QFrame):
    """
    creates an instance of a vertical line
    """
    def __init__(self):
        QtWidgets.QFrame.__init__(self)
        """
        creates an instance of a vertical line
        """
    def make_line(self):
        """
        Takes no arguments
       Runs all the necessary commands to create a vertical line that can be displayed
       on a GUI.
        :return: VLine widget object
        """
        line = QtWidgets.QLabel()
        line.setFrameStyle(QtWidgets.QFrame.VLine | QtWidgets.QFrame.Plain)
        return line

class TicketGui(QtWidgets.QDialog):
    """
    Creates the GUI for the ticket tool and has functions to send information to shotgun
    """

    def __init__(self):
        QtWidgets.QDialog.__init__(self, parent=get_maya_window())
        """
        """

        # widgets in step one
        self.feature_button = None
        self.bug_button = None
        self.note_button = None
        self.problem_type = None
        self.line1 = None
        self.step_one_button = None

        # widgets in step two
        self.priority_cb = None
        self.project_cb = None
        self.description_te = None
        self.line3 = None
        self.line4 = None
        self.error_te = None
        self.steps_te = None
        self.title_le = None
        self.line2 = None
        self.project_objs = []
        self.project_names = []
        self.current_project = None
        self.step_two_button = None

        # widgets in step three
        self.tree_view = None
        self.asset_list_view = None
        self.sequences = []
        self.assets = []
        self.asset_names = []
        self.related_sequences = []
        self.related_shots = {}
        self.related_assets = []
        self.step_three_button = None

        self.main_vb = None
        self.step_one_layout = None
        self.step_two_layout = None
        self.step_three_layout = None

    def init_gui(self):
        """
        Accepts no arguments.
        Calls create_step_one() create_step_two() and create_step_three() to get the
        layouts for the gui.
        Makes the horizontal lines to seperate sections of the tool.
        Makes the Cancel button to close the window.
        :return: success of the function
        """

        # creats the main layout
        self.main_vb = QtWidgets.QVBoxLayout(self)

        self.step_one_layout = self.create_step_one()
        line = HLine()
        self.line1 = line.make_line()

        self.step_two_layout = self.create_step_two()
        line = HLine()
        self.line2 = line.make_line()
        self.disable_layout(self.step_two_layout)

        self.step_three_layout = self.create_step_three()
        self.disable_layout(self.step_three_layout)

        # creates the extra buttons
        cancel_btn = QtWidgets.QPushButton('Cancel')
        cancel_btn.setStyleSheet('background-color: red')
        cancel_btn.clicked.connect(self.close)

        # creates the layout main
        self.main_vb.addLayout(self.step_one_layout)
        self.main_vb.addWidget(self.line1)
        self.main_vb.addLayout(self.step_two_layout)
        self.main_vb.addWidget(self.line2)
        self.main_vb.addLayout(self.step_three_layout)
        self.main_vb.addWidget(cancel_btn)

        self.setGeometry(300, 300, 350, 150)
        self.setFixedSize(450, 750)
        self.setWindowTitle('New Ticket')
        self.show()

    def create_step_one(self):
        """
        This creates a QVBoxLayout for the first step of the Ticket tool
        This step gets the type of ticket thats being filled out.
        :return: QVBoxLayout with all of step one
        :type: QVBoxLayout
        """
        # first step layout
        # create buttons
        self.ticket_types = SG_TICKET_TYPES.ALL
        step_one_lbl = QtWidgets.QLabel('Ticket Type: ')
        self.bug_button = QtWidgets.QRadioButton(self.ticket_types[0])
        self.feature_button = QtWidgets.QRadioButton(self.ticket_types[1])
        self.note_button = QtWidgets.QRadioButton(self.ticket_types[2])


        # button group and connections
        button_grp = QtWidgets.QButtonGroup()
        button_grp.addButton(self.bug_button)
        self.bug_button.clicked.connect(self.update_ticket_type)
        button_grp.addButton(self.feature_button)
        self.feature_button.clicked.connect(self.update_ticket_type)
        button_grp.addButton(self.note_button)
        self.note_button.clicked.connect(self.update_ticket_type)

        # create and add widgets to layout
        button_hb = QtWidgets.QHBoxLayout()
        button_hb.addWidget(self.bug_button)
        button_hb.addWidget(self.feature_button)
        button_hb.addWidget(self.note_button)

        # continue button
        self.step_one_button = QtWidgets.QPushButton('Continue')
        self.step_one_button.setObjectName('stepOne')
        self.step_one_button.clicked.connect(self.run_step)

        step_one_vb = QtWidgets.QVBoxLayout()
        step_one_vb.addWidget(step_one_lbl)
        step_one_vb.addLayout(button_hb)
        step_one_vb.addWidget(self.step_one_button)
        step_one_vb.addSpacing(15)

        return step_one_vb

    def create_step_two(self):
        """
        This creates a QVBoxLayout for the second step of the Ticket tool
        This step asks for the title of the ticket, the description of the problem,
        how to recreate the problem, and any error messages.
        :return: QVBoxLayout with all of step one
        :type: QVBoxLayout
        """
        # depening on the problem type from step one
        # create an v box for the form
        info_vb = QtWidgets.QVBoxLayout()
        info_lbl = QtWidgets.QLabel('Enter some info about the ticket: ')
        section1_hb = QtWidgets.QHBoxLayout()
        section2_hb = QtWidgets.QHBoxLayout()

        # creates the name  and description line edits
        title_lbl = QtWidgets.QLabel('Title: ')
        self.title_le = QtWidgets.QLineEdit('')
        self.title_le.setFixedSize(200, 20)
        title_vb = QtWidgets.QVBoxLayout()
        title_vb.addWidget(title_lbl)
        title_vb.addWidget(self.title_le)

        description_lbl = QtWidgets.QLabel('Description: ')
        self.description_te = QtWidgets.QTextEdit('')
        self.description_te.setFixedSize(200, 100)
        #description_vb = QtWidgets.QVBoxLayout()
        title_vb.addWidget(description_lbl)
        title_vb.addWidget(self.description_te)

        # get project
        project_lbl = QtWidgets.QLabel('Project: ')
        self.project_cb = QtWidgets.QComboBox()
        shotgun_projects = spo.ProjectFetcher.get_project_objects(spo.ProjectFetcher())
        self.project_names = get_sg_user_projects()
        for proj in shotgun_projects:
            for name in self.project_names:
                if proj.name == name:
                    self.project_objs.append(proj)

        self.project_names.sort()
        self.project_cb.addItem('None')
        self.project_cb.addItems(self.project_names)
        self.project_cb.setFixedSize(200, 20)
        project_vb = QtWidgets.QVBoxLayout()
        project_vb.addWidget(project_lbl)
        project_vb.addWidget(self.project_cb)

        # priority
        # get priority list from shotgun
        priority_lbl = QtWidgets.QLabel('Priority: ')
        self.priority_cb = QtWidgets.QComboBox()
        self.priority_cb.addItems(SG_TICKET_PRIORITY.ALL)
        self.priority_cb.setCurrentText(SG_TICKET_PRIORITY.ALL[0])
        self.priority_cb.setFixedSize(200, 20)
        #priority_vb = QtWidgets.QVBoxLayout()
        project_vb.addWidget(priority_lbl)
        project_vb.addWidget(self.priority_cb)
        line = QtWidgets.QLabel()
        line.setFrameStyle(QtWidgets.QFrame.Plain)
        line.setFixedSize(200, 50)
        project_vb.addWidget(line)

        # make V Line
        vline1 = VLine()
        self.line3 = vline1
        # make V Line
        vline2 = VLine()
        self.line4 = vline1

        # add vb's to section1_hb
        section1_hb.addLayout(title_vb)
        #section1_hb.addLayout(description_vb)
        section1_hb.addWidget(self.line3)
        section1_hb.addLayout(project_vb)
        #section1_hb.addLayout(priority_vb)

        # widgets for section 2
        steps_lbl = QtWidgets.QLabel('How to re-create the issue: ')
        self.steps_te = QtWidgets.QTextEdit('')
        self.steps_te.setFixedSize(200, 100)
        steps_vb = QtWidgets.QVBoxLayout()
        steps_vb.addWidget(steps_lbl)
        steps_vb.addWidget(self.steps_te)

        error_lbl = QtWidgets.QLabel('Paste any errors here: ')
        self.error_te = QtWidgets.QTextEdit('')
        self.error_te.setFixedSize(200, 100)
        error_vb = QtWidgets.QVBoxLayout()
        error_vb.addWidget(error_lbl)
        error_vb.addWidget(self.error_te)

        # add vb's to section2_hb
        section2_hb.addLayout(steps_vb)
        section2_hb.addWidget(self.line4)
        section2_hb.addLayout(error_vb)

        # add layouts to info layout
        #info_vb.addWidget(info_lbl)
        info_vb.addLayout(section1_hb)
        info_vb.addLayout(section2_hb)



        # continue button
        self.step_two_button = QtWidgets.QPushButton('Continue')
        self.step_two_button.setObjectName('stepTwo')
        self.step_two_button.clicked.connect(self.run_step)

        step_two_vb = QtWidgets.QVBoxLayout()
        step_two_vb.addLayout(info_vb)
        step_two_vb.addWidget(self.step_two_button)
        step_two_vb.addSpacing(15)

        return step_two_vb

    def create_step_three(self):
        """
        This creates a QVBoxLayout for the third step of the Ticket tool
        This step asks for any related sequences, shots, and assets to the ticket.
        There is a button at the end of the layout to submit the ticket.
        Before submitting it will send a message to the user asking if
        they are sure they want to submit.
        :return: QVBoxLayout with all of step one
        :type: QVBoxLayout
        """
        # create an v box for the form
        input_hb = QtWidgets.QHBoxLayout()

        # Get sequences related to the project from shotgun
        self.tree_view = QtWidgets.QTreeWidget()
        self.tree_view.setHeaderLabel('Related Sequences and Shots: ')
        self.tree_view.setFixedSize(200, 150)
        ss_vb = QtWidgets.QVBoxLayout()
        ss_vb.addWidget(self.tree_view)

        # Get assets related to the project from shotgun
        asset_lbl = QtWidgets.QLabel('Related Assets: ')
        asset_lbl.setFixedSize(100, 20)
        self.asset_list_view = QtWidgets.QListWidget()
        self.asset_list_view.setFixedSize(200, 125)
        asset_vb = QtWidgets.QVBoxLayout()

        asset_vb.addWidget(asset_lbl)
        asset_vb.addWidget(self.asset_list_view)


        input_hb.addLayout(ss_vb)
        input_hb.addLayout(asset_vb)

        # continue button
        self.step_three_button = QtWidgets.QPushButton('Submit')
        self.step_three_button.setObjectName('stepThree')
        self.step_three_button.clicked.connect(self.run_step)

        step_three_vb = QtWidgets.QVBoxLayout()
        step_three_vb.addLayout(input_hb)
        step_three_vb.addWidget(self.step_three_button)
        step_three_vb.addSpacing(15)

        return step_three_vb

    def run_step(self):
        """
        This function sets up the next layout after the user clicks
        the continue and submit buttons
        :return: Nothing
        """

        #check to see if sender exist
        sender = self.sender()
        if sender:
            #check the name of sender and add the string to the correct line edit
            obj_name = str(sender.objectName())
            if obj_name == 'stepOne':
                if self.problem_type != None:
                    #disables step one and enables step 2
                    self.disable_layout(self.step_one_layout)
                    self.enable_layout(self.step_two_layout)
                print "Error: select a ticket type"

            elif obj_name == 'stepTwo':
                if self.title_le.text() is not '' and len(self.description_te.toPlainText()) is not 0 \
                    and len(self.error_te.toPlainText()) is not 0 and len(self.steps_te.toPlainText()) is not 0:
                    for proj_obj in self.project_objs:
                        if proj_obj.name == self.project_cb.currentText():
                            self.current_project = proj_obj
                            self.sequences = proj_obj.get_sequences()
                            self.assets = proj_obj.get_assets()
                            if len(self.sequences) >0:
                                self.update_sequences_and_shots()
                            if self.assets:
                                self.update_assets()

                            # disables step 2 and enables step 3
                            self.disable_layout(self.step_two_layout)
                            self.enable_layout(self.step_three_layout)
                        elif self.project_cb.currentText() == 'None':
                            # disables step 2 and enables step 3
                            self.current_project = 'None'
                            self.disable_layout(self.step_two_layout)
                            self.enable_layout(self.step_three_layout)
                else:
                    print "Error: Make sure to fill out all fields"


            elif obj_name == 'stepThree':
                self.get_assets()
                self.get_sequences_and_shots()
                reg_description = "DESCRIPTION: " + self.description_te.toPlainText()+ "\n"
                step_description = "STEPS: " +self.steps_te.toPlainText()+ "\n"
                error_description = "ERRORS: " +self.error_te.toPlainText()+ "\n"
                tagged_items = "TAGED ITEMS: "
                tagged_assets = 'assets:('
                tagged_shots = 'shots:('
                tagged_sequences = 'sequences:('

                # format tagged_assets
                asset_count = 0
                for asset in self.related_assets:
                    if asset_count < len(self.related_assets)-1:
                        tagged_assets = tagged_assets + asset + ", "
                    else:
                        tagged_assets = tagged_assets + asset
                    asset_count +=1
                tagged_assets = tagged_assets + ") "

                # format tagged_shots
                shot_count = 0
                for shot in self.related_shots.items():
                    if shot_count < len(self.related_shots)-1:
                        tagged_shots = tagged_shots + shot[0][0]+shot[1][1:4] + ", "
                    else:
                        tagged_shots = tagged_shots + shot[0][0] + shot[1][1:4]
                    shot_count += 1
                tagged_shots = tagged_shots + ") "

                # format tagged_sequences
                sequence_count = 0
                for sequence in self.related_sequences:
                    if sequence_count < len(self.related_sequences)-1:
                        tagged_sequences = tagged_sequences + sequence + ", "
                    else:
                        tagged_sequences = tagged_sequences + sequence
                    sequence_count += 1
                tagged_sequences = tagged_sequences + ") "

                # format description argument for ticket object
                tagged_items = tagged_items + tagged_sequences + tagged_shots + tagged_assets
                combined_description = reg_description + step_description + error_description + tagged_items
                print(combined_description)
                self.warn_user("Ticket Tool", "Are you sure you want to submit this ticket?")
                new_ticket = SGTicketObject(description=combined_description,
                                            title=self.title_le.text(),
                                            proj_obj=self.current_project,
                                            priority=self.priority_cb.currentText(),
                                            status=SG_TICKET_STATUS.ALL[0],
                                            ticket_type=self.problem_type)
                new_ticket.create_new_ticket()

                self.close()

                """new_ticket = SGTicketObject(description=self.description_te.toPlainText(),
                                            title=self.title_le.text(),
                                            proj_obj=self.current_project,
                                            priority=self.priority_cb.currentText(),
                                            status=SG_TICKET_STATUS.ALL[0],
                                            ticket_type=self.problem_type,
                                            related_shots = self.shot_cb.currentText(),
                                            related_assets = self.related_assets)
                new_ticket.create_new_ticket()

                self.close()"""

    def update_assets(self):
        """
        creates a QTreeWidgetItem for every asset
        :return: Nothing
        """
        if len(self.assets)>0:
            for asset in self.assets:
                self.asset_names.append(asset.get_name())
            self.asset_names.sort()
            for asset in self.asset_names:
                # print asset.get_name()
                list_item = QtWidgets.QListWidgetItem(asset.get_name())
                list_item.setCheckState(QtCore.Qt.Unchecked)
                self.asset_list_view.addItem(list_item)

    def get_assets(self):
        """
        Searches for all of the the checked assets in the QTreeWidget
        """
        num_assets = self.asset_list_view.count()
        count = 0
        while count < num_assets:
            if self.asset_list_view.item(count).checkState() == QtCore.Qt.Checked:
                #print self.asset_list_view.item(count).text()
                self.related_assets.append(self.asset_list_view.item(count).text())
            count+=1

    def get_sequences_and_shots(self):
        """
        Searches for all of the checked shots in the tree_view
        """
        num_sequences = len(self.sequences)
        sequence_count = 0
        while sequence_count < num_sequences:
            if self.tree_view.topLevelItem(sequence_count).checkState(0) == QtCore.Qt.Checked:
                #print(self.tree_view.topLevelItem(sequence_count).text(0))
                self.related_sequences.append(self.tree_view.topLevelItem(sequence_count).text(0))

            num_shots = self.tree_view.topLevelItem(sequence_count).childCount()
            shot_count = 0
            while shot_count < num_shots:
                if self.tree_view.topLevelItem(sequence_count).child(shot_count).checkState(0) == QtCore.Qt.Checked:
                    #print(self.tree_view.topLevelItem(sequence_count).child(shot_count).text(0))
                    self.related_shots[self.tree_view.topLevelItem(sequence_count).text(0)] =\
                        self.tree_view.topLevelItem(sequence_count).child(shot_count).text(0)
                shot_count += 1
            sequence_count += 1




    def update_sequences_and_shots(self):
        """
        Adds a QTreeWidgetItem for every sequence in the selected shotgun project.
        Adds a QTreeWidgetItem as a child to the sequence for each shot.
        :return: Nothing
        """
        for sequence in self.sequences:
            sequence_item = QtWidgets.QTreeWidgetItem()
            sequence_item.setCheckState(0, QtCore.Qt.Unchecked)
            sequence_item.setText(0, sequence.get_name())
            for shot in sequence.get_shot_objs():
                shot_item = QtWidgets.QTreeWidgetItem()
                shot_item.setCheckState(0, QtCore.Qt.Unchecked)
                shot_item.setText(0, shot.get_name())
                sequence_item.addChild(shot_item)
            self.tree_view.addTopLevelItem(sequence_item)

    def update_ticket_type(self):
        """
        This function updates the problem type when a radio button in step one is clicked
        :return: Nothing
        """
        btn = self.sender()
        if btn.text() == 'Bug':
            self.problem_type = btn.text()
            #print btn.text()
        elif btn.text() == 'Feature':
            self.problem_type = btn.text()
            #print btn.text()
        elif btn.text() == 'Notes':
            self.problem_type = btn.text()
            #print btn.text()


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
        # loops through each item in the given layout
        for index in range(layout.count()):
            # doesnt know the type so gets both as widget and layout
            widget = layout.itemAt(index).widget()
            new_layout = layout.itemAt(index).layout()
            # disables it if widget or recursively calls this if layout
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
        # loops through each item in the given layout
        for index in range(layout.count()):
            # doesnt know the type so gets both as widget and layout
            widget = layout.itemAt(index).widget()
            new_layout = layout.itemAt(index).layout()
            # disables it if widget or recursively calls this if layout
            if widget:
                widget.setEnabled(True)
            if new_layout:
                self.enable_layout(new_layout)



"""
import ticket_tool.ticket_tool as tt;reload(tt)
ticket = tt.TicketGui()
ticket.init_gui()

from shotgun_tools.sg_utils import get_sg_user_projects
get_sg_user_projects()

import shotgun_tools.sg_pipe_objects as spo;reload(spo)
objs = spo.ProjectFetcher.get_project_objects(spo.ProjectFetcher())
obj_names = spo.ProjectFetcher.get_project_names(spo.ProjectFetcher())
count  = 0
for name in obj_names:
    if name =='nightshift':
        print count
    count+=1
            
dir(objs[1867].get_assets()[0])
objs[1867].get_assets()[0].get_name()


dir(objs[1867].get_sequences()[1].get_shot_objs()[0])
objs[1867].get_sequences()[1].get_shot_objs()[0].get_shot_assets()

"""