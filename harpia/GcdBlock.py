# -*- coding: utf-8 -*-
# [HARPIA PROJECT]
#
#
# S2i - Intelligent Industrial Systems
# DAS - Automation and Systems Department
# UFSC - Federal University of Santa Catarina
# Copyright: 2007 - 2009 Clovis Peruchi Scotti (scotti@ieee.org), S2i (www.s2i.das.ufsc.br)
#
#
#    This program is free software: you can redistribute it and/or modify it
#    under the terms of the GNU General Public License version 3, as published
#    by the Free Software Foundation.
#
#    This program is distributed in the hope that it will be useful, but
#    WITHOUT ANY WARRANTY; without even the implied warranties of
#    MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR
#    PURPOSE.  See the GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#    For further information, check the COPYING file distributed with this software.
#
#----------------------------------------------------------------------

import pango
import gtk
import math
import gnomecanvas
import os

from GcdBlockMenu import GcdBlockMenu
import s2idirectory
import s2iblockpropertiesgui
from utils.XMLUtils import XMLParser
from utils.graphicfunctions import *

import copy

WIDTH_2_TEXT_OFFSET = 22
WIDTH_DEFAULT = 112
HEIGHT_DEFAULT = 56
PORT_SENSITIVITY = 12
RADIUS = 15
INPUT_WIDTH = 24
INPUT_HEIGHT = 24
OUTPUT_HEIGHT = 24
OUTPUT_WIDTH = 24


class GcdBlock( gnomecanvas.CanvasGroup):

#----------------------------------------------------------------------
    def __init__( self, diagram, block_type, block_id=1):

        self.block_type = block_type
        self.diagram = diagram
        self.data_dir = os.environ['HARPIA_DATA_DIR']
        if s2idirectory.block.has_key(block_type):
            self.block_description = s2idirectory.block[block_type]
        else:
            self.block_description = s2idirectory.block[0]
            print "Bad block type.. assuming 00"

        self.block_id = block_id
        self.widgets = {}
        self.focus = False
        self.has_flow = False
        self.time_shifts = False
        self.is_source = False

        if self.block_description.has_key("IsSource"): #all data sources
            self.is_source = self.block_description["IsSource"]

        if self.block_description.has_key("TimeShifts"): #delay block
            self.time_shifts = self.block_description["TimeShifts"]

        self.m_oPropertiesXML = XMLParser(self.data_dir +
                    str(self.block_description["Path"]["Xml"]))
        self.m_oPropertiesXML.getTag("properties").getTag("block").setAttr("id",str(self.block_id))

        self.m_oBorderColor = [ 0, 0, 0, 255 ]
        self.m_oBackColor = [0,0,0,150]
        self.input_port_centers = []
        self.output_port_centers = []
        self.width = WIDTH_DEFAULT

        t_nMaxIO = max(len(self.block_description["InTypes"]), len(self.block_description["OutTypes"]))

        ## Generates the block size, based on the number of inputs,outputs
        # Comment block is too small...
        if not t_nMaxIO:
            t_nMaxIO = 1

        self.height = max( ((t_nMaxIO-1)* 5 ) #espacamento entre ports = 5
                          +(RADIUS*2 ) #tirando a margem superior e inferior
                          +(t_nMaxIO * INPUT_HEIGHT),#adicionando a altura de cada port
                          HEIGHT_DEFAULT)

        self.__gobject_init__()
        self.group = self.diagram.root().add(self,x=0,y=0)
        self.group.connect("event", self.__group_event)
        self.group.set_flags(gtk.CAN_FOCUS)
        self.build()

#----------------------------------------------------------------------
    def __is_input(self,event):
        clicked_point = (event.x - self.group.get_property('x'),
                    event.y - self.group.get_property('y'))
        input_port_centers = []
        #compute portCenters if they don't exist
        if len(self.input_port_centers) == 0:
            self.__compute_input_ports()
        for point_index in range(len(self.input_port_centers)):
            if Dist(self.input_port_centers[point_index],clicked_point) < PORT_SENSITIVITY:
                return point_index
        return -1

#----------------------------------------------------------------------
    def __is_output(self,event):
        clicked_point = (event.x - self.group.get_property('x'),
                    event.y - self.group.get_property('y'))
        if len(self.output_port_centers) == 0: #compute portCenters if they don't exist
            self.__compute_output_ports()
        for point_index in range(len(self.output_port_centers)):
            if Dist(self.output_port_centers[point_index],clicked_point) < PORT_SENSITIVITY:
                return point_index
        return -1

#----------------------------------------------------------------------
    def __compute_output_ports(self):
        for outputPort in range(len(self.block_description["OutTypes"])):
            self.output_port_centers.append((self.width-(INPUT_WIDTH/2),
                     (RADIUS # upper border
                     + (outputPort*5) # spacing betwen ports
                     + outputPort*INPUT_HEIGHT #previous ports
                     + INPUT_HEIGHT/2)))#going to the port's center

#----------------------------------------------------------------------
    def __compute_input_ports(self):
        for inputPort in range(len(self.block_description["InTypes"])):
            self.input_port_centers.append((INPUT_WIDTH/2,
                     (RADIUS # upper border
                     + (inputPort*5) # spacing betwen ports
                     + inputPort*INPUT_HEIGHT #previous ports
                     + INPUT_HEIGHT/2)))#going to the port's center

#----------------------------------------------------------------------
    def __group_event(self, widget, event=None):
        if event.type == gtk.gdk.BUTTON_PRESS:
                if event.button == 1:
                    # Remember starting position.
                    # if event resolution got here, the diagram event resolution routine didn't matched with any ports.. so..
                    self.remember_x = event.x
                    self.remember_y = event.y

                    #Cascading event resolution:
                    input_event = self.__is_input(event)
                    if input_event != -1:
                        self.diagram.clicked_input(self.block_id,input_event)
                        return True
                    else:
                        output_event = self.__is_output(event)
                        if output_event != -1:
                            self.diagram.clicked_output(self.block_id,output_event)
                            return True
                        else:
                            self.group.grab_focus()
                            self.update_focus()
                            return False
                    return False
                elif event.button == 3:
                    self.__right_click(event)
                    return True #explicitly returns true so that diagram won't catch this event
        elif event.type == gtk.gdk.MOTION_NOTIFY:
                if event.state & gtk.gdk.BUTTON1_MASK:
                    if self.diagram.curr_connector == None:
                        if(widget == self.group):#make sure we're not moving somebody else!
                            # Get the new position and move by the difference
                            new_x = event.x
                            new_y = event.y
                            widget.move(new_x - self.remember_x, new_y - self.remember_y)
                            self.diagram.update_scrolling()
                            self.remember_x = new_x
                            self.remember_y = new_y
                            return False

        elif event.type == gtk.gdk._2BUTTON_PRESS:
            GcdBlockMenu(self, event)
            return True

        elif event.type == gtk.gdk.ENTER_NOTIFY:
                # Make the outline wide.
                self.__mouse_over_state(True)
                return False #pode propagar p/ cima

        elif event.type == gtk.gdk.LEAVE_NOTIFY:
                # Make the outline thin.
                if not self.focus:
                    self.__mouse_over_state(False)
                return False #pode passar p/ cima

#----------------------------------------------------------------------
    def __del__(self):
        print "GC: deleting GcdBlock:",self.block_id

#----------------------------------------------------------------------
    def _BbRect(self):
        p = []

        arc0 = MakeArc(radius=RADIUS, edges=5, q=0)
        arc1 = MakeArc(radius=RADIUS, edges=5, q=1)
        arc2 = MakeArc(radius=RADIUS, edges=5, q=2)
        arc3 = MakeArc(radius=RADIUS, edges=5, q=3)

        pf = []
        #cw

        #linha superior.. p/ referencia
        pf.append((RADIUS,0))
        pf.append((self.width-RADIUS,0))
        pf.extend(AlterArc(arc3,self.width-RADIUS,RADIUS))##canto superior direito
        pf.extend(AlterArc(arc0,self.width-RADIUS,self.height-RADIUS))##canto inferior direito
        pf.extend(AlterArc(arc1,RADIUS,self.height-RADIUS))##canto inferior esquerdo
        pf.extend(AlterArc(arc2,RADIUS,RADIUS))##canto superior esquerdo

        p = []

        #takes a list of points(tuples)(pf) to produce a list of points in form [x1,y1,x2,y2,x3,y3....,xn,yn] (p)
        for n in pf:
            for e in n:
                p.append(e)

        self.SetBackColor()
        w1 = self.group.add(gnomecanvas.CanvasPolygon,
                    points=p,# y1=y1, x2=x2, y2=y2,
                    fill_color_rgba=ColorFromList(self.m_oBackColor),
                    outline_color='black',
                    width_units=1.0)
        self.widgets["Rect"] = w1

#----------------------------------------------------------------------
    def _BIcon(self):
        pb = gtk.gdk.pixbuf_new_from_file(self.data_dir +
                    self.block_description["Icon"])
        icon = self.group.add(gnomecanvas.CanvasPixbuf,
                    pixbuf=pb,
                    x=(self.width/2),
                    y=(self.height/2),
                    anchor=gtk.ANCHOR_CENTER)
        self.widgets["pb"] = icon

#----------------------------------------------------------------------
    def _BInputs(self):
        inPWids = []
        for x in range(len(self.block_description["InTypes"])):
            try:
                pb = gtk.gdk.pixbuf_new_from_file(self.data_dir +
                            s2idirectory.typeIconsIn[self.block_description["InTypes"][x]])
            except:
                pb = gtk.gdk.pixbuf_new_from_file(self.data_dir + 
                            s2idirectory.icons["IconInput"])

            t_Wid = self.group.add(gnomecanvas.CanvasPixbuf, pixbuf=pb,x=0,y=(RADIUS # upper border
                              + (x*5) # spacing betwen ports
                              + x*INPUT_HEIGHT), #previous ports
                              anchor=gtk.ANCHOR_NORTH_WEST)
            inPWids.append(t_Wid)
        self.widgets["Inputs"] = inPWids

#----------------------------------------------------------------------
    def _BOutputs(self):
        outPWids = []
        for x in range(len(self.block_description["OutTypes"])):
            try:
                pb = gtk.gdk.pixbuf_new_from_file(self.data_dir + 
                            s2idirectory.typeIconsOut[
                            self.block_description["OutTypes"][x]])
            except:
                pb = gtk.gdk.pixbuf_new_from_file(self.data_dir +
                            s2idirectory.icons["IconOutput"])
            t_Wid = self.group.add(gnomecanvas.CanvasPixbuf,
                            pixbuf=pb,
                            x=(self.width-OUTPUT_WIDTH),
                            y=(RADIUS # upper border
                            + (x*5) # spacing betwen ports
                            + x*OUTPUT_HEIGHT), #previous ports
                      anchor=gtk.ANCHOR_NORTH_WEST)
            outPWids.append(t_Wid)
        self.widgets["Outputs"] = outPWids

#----------------------------------------------------------------------
    def _BLabels(self):
        label = self.group.add(gnomecanvas.CanvasText,
                            text=self.block_description["Label"],
                            fill_color='black',
                            anchor=gtk.ANCHOR_CENTER,
                            weight=pango.WEIGHT_BOLD,
                            size_points=9,
                            x=(self.width/2),
                            y=(self.height-10))
        text_width = label.get_property('text-width')
        oldX,oldY = ((self.width/2),(self.height-10))
        self.width = max(text_width + WIDTH_2_TEXT_OFFSET,self.width)
        label.move((self.width/2)-oldX, (self.height-10)-oldY)
        self.widgets["Label"] = label

#----------------------------------------------------------------------
    def build(self):
        self._BLabels()#must be called in this order! otherwise the box rect won't have the propper width
        self._BbRect()
        self._BInputs()
        self._BOutputs()
        self._BIcon()
        self.update_flow()
        self.__update_flow_display()

#----------------------------------------------------------------------
    def update_flow(self,a_bCheckTimeShifter=False):
        if self.is_source or (self.time_shifts and (not a_bCheckTimeShifter)):#
            self.has_flow = True
        else:
            sourceConnectors = self.diagram.get_connectors_to(self.block_id)
            if len(sourceConnectors) != len(self.block_description["InTypes"]):
                self.has_flow = False
            else:
                for connIdx in reversed(range(len(sourceConnectors))):
                    if sourceConnectors[connIdx].has_flow:
                        sourceConnectors.pop(connIdx)
                if len(sourceConnectors) != 0:
                    self.has_flow = False
                else:
                    self.has_flow = True
        self.__update_flow_display()
        return self.has_flow

#----------------------------------------------------------------------
    def __update_flow_display(self):
        t_oFocusCorrectedColor = [self.m_oBackColor[0],
                                  self.m_oBackColor[1],
                                  self.m_oBackColor[2],
                                  self.m_oBackColor[3]]
        if self.has_flow:
            #with focus: original colors
            t_oFocusCorrectedColor[3] = self.m_oBackColor[3]
            self.widgets["Rect"].set(outline_color='black',
                        fill_color_rgba=ColorFromList(t_oFocusCorrectedColor))
        else:
            #without focus the block background will be much more transparent
            t_oFocusCorrectedColor[3] = 50
            self.widgets["Rect"].set(outline_color='red',
                        fill_color_rgba=ColorFromList(t_oFocusCorrectedColor))

#----------------------------------------------------------------------
    def get_input_pos(self, a_nInputID):
        if len(self.input_port_centers) == 0: #compute portCenters if they don't exist
            self.__compute_input_ports()
        x = 0 + self.group.get_property('x')
        y = self.input_port_centers[a_nInputID][1]+self.group.get_property('y')
        point = self.i2w(x,y)
        return (point[0],point[1])

#----------------------------------------------------------------------
    def get_output_pos(self, output_id):
        #compute portCenters if they don't exist
        if len(self.output_port_centers) == 0:
            self.__compute_output_ports()
        x = self.width + self.group.get_property('x')
        y = self.output_port_centers[output_id][1] + self.group.get_property('y')
        point = self.i2w(x,y)
        return (point[0],point[1])

#----------------------------------------------------------------------
    def get_block_pos(self):
        return (self.group.get_property('x'),self.group.get_property('y'))

#----------------------------------------------------------------------
    def update_focus(self):
        if self.diagram.get_property('focused-item') == self.group:
            self.__mouse_over_state(True)
            self.focus = True
        else:
            self.__mouse_over_state(False)
            self.focus = False

#----------------------------------------------------------------------
    def __mouse_over_state(self, state):
        if state:
            self.widgets["Rect"].set(width_units=3)
        else:
            self.widgets["Rect"].set(width_units=1)

#----------------------------------------------------------------------
    def __right_click(self, a_oEvent):
       GcdBlockMenu(self, a_oEvent)

#----------------------------------------------------------------------
    def get_state(self):
        return self.has_flow

#----------------------------------------------------------------------
    def move(self, x, y):
        self.group.move(x,y)

#----------------------------------------------------------------------
    def redraw(self):
        self.group.move(0,0)

#----------------------------------------------------------------------
    def get_id(self):
        return self.block_id

#----------------------------------------------------------------------
    def get_type(self):
        return self.block_type

#----------------------------------------------------------------------
    def get_position(self):
        return self.group.get_property('x'),self.group.get_property('y')

# ---------------------------------------
    def SetBorderColor(self, a_nColor=None):
        print "SetBorderColor is deprecated, fix this"
        self.m_oBackColor = a_nColor

#----------------------------------------------------------------------
    def GetPropertiesXML(self):
        return self.m_oPropertiesXML

#----------------------------------------------------------------------
    def SetPropertiesXML(self, outerProps):
        self.m_oPropertiesXML = outerProps

#----------------------------------------------------------------------
    def SetPropertiesXML_nID( self, a_oPropertiesXML ):
        myBlockId = self.m_oPropertiesXML.getTag("properties").getTag("block").getAttr("id")
        #storing this block's Block.Id
        self.m_oPropertiesXML = copy.deepcopy(a_oPropertiesXML)
        self.m_oPropertiesXML.getTag("properties").getTag("block").setAttr("id",myBlockId)

#----------------------------------------------------------------------
    def GetBorderColor(self,*args):
        return self.m_oBorderColor

#----------------------------------------------------------------------
    def GetBackColor(self,*args):
        return self.m_oBackColor

#----------------------------------------------------------------------
    def SetBackColor( self, a_nColors=None ):#RGBA
        if a_nColors == None:
            a_nColors = self.block_description["Color"].split(":")
        t_nRed = int(a_nColors[0])
        t_nGreen = int(a_nColors[1])
        t_nBlue = int(a_nColors[2])
        t_nAlpha = int(a_nColors[3])
        self.m_oBackColor = [t_nRed, t_nGreen, t_nBlue, t_nAlpha]

        if self.widgets.has_key("Rect"): #rect already drawn
            self.widgets["Rect"].set(fill_color_rgba=ColorFromList(self.m_oBackColor))

