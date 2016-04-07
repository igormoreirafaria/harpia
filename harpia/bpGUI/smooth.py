# -*- coding: utf-8 -*-
# [HARPIA PROJECT]
#
#
# S2i - Intelligent Industrial Systems
# DAS - Automation and Systems Department
# UFSC - Federal University of Santa Catarina
# Copyright: 2006 - 2007 Luis Carlos Dill Junges (lcdjunges@yahoo.com.br), Clovis Peruchi Scotti (scotti@ieee.org),
#                        Guilherme Augusto Rutzen (rutzen@das.ufsc.br), Mathias Erdtmann (erdtmann@gmail.com) and S2i (www.s2i.das.ufsc.br)
#            2007 - 2009 Clovis Peruchi Scotti (scotti@ieee.org), S2i (www.s2i.das.ufsc.br)
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
# ----------------------------------------------------------------------

import gtk

from harpia.GladeWindow import GladeWindow
from harpia.s2icommonproperties import S2iCommonProperties, APP, DIR

# i18n
import os
from harpia.utils.XMLUtils import XMLParser
import gettext

_ = gettext.gettext
gettext.bindtextdomain(APP, DIR)
gettext.textdomain(APP)


# ----------------------------------------------------------------------

class Properties(GladeWindow, S2iCommonProperties):
    # ----------------------------------------------------------------------

    def __init__(self, PropertiesXML, S2iBlockProperties):

        self.m_sDataDir = os.environ['HARPIA_DATA_DIR']

        filename = self.m_sDataDir + 'glade/smooth.ui'
        self.m_oPropertiesXML = PropertiesXML
        self.m_oS2iBlockProperties = S2iBlockProperties

        widget_list = [
            'Properties',
            'SMOOType',
            'SMOOParam1',
            'SMOOParam2',
            'BackgroundColor',
            'BorderColor',
            'HelpView'
        ]

        handlers = [
            'on_cancel_clicked',
            'on_smooth_confirm_clicked',
            'on_BackColorButton_clicked',
            'on_BorderColorButton_clicked'
        ]

        top_window = 'Properties'

        GladeWindow.__init__(self, filename, top_window, widget_list, handlers)

        # load properties values

        self.block_properties = self.m_oPropertiesXML.getTag("properties").getTag("block").getChildTags("property")

        for Property in self.block_properties:
            name = Property.getAttr("name")
            value = Property.getAttr("value")

            if name == "type":
                if value == "CV_BLUR":
                    self.widgets['SMOOType'].set_active(int(0))
                if value == "CV_GAUSSIAN":
                    self.widgets['SMOOType'].set_active(int(1))
                if value == "CV_MEDIAN":
                    self.widgets['SMOOType'].set_active(int(2))
                    #   if Property.value == "CV_BILATERAL":
                    #       self.widgets['SMOOType'].set_active( int(4) )

            if name == "param1":
                self.widgets['SMOOParam1'].set_value(int(value))

            if name == "param2":
                self.widgets['SMOOParam2'].set_value(int(value))

    	self.configure()
        # load help text
        # t_oS2iHelp = XMLParser(self.m_sDataDir + "help/smooth" + _("_en.help"))

        # t_oTextBuffer = gtk.TextBuffer()

        # t_oTextBuffer.set_text(unicode(str(t_oS2iHelp.getTag("help").getTag("content").getTagContent())))

        # self.widgets['HelpView'].set_buffer(t_oTextBuffer)

    #----------------Help Text--------------------------------------

    def getHelp(self):#adicionado help
        return "Aplicação de um filtro de suavização. Suaviza os contornos de objetos na imagem, borrando-os levemente."

    # ----------------------------------------------------------------------
      

    # ----------------------------------------------------------------------

    def __del__(self):

        pass

    # ----------------------------------------------------------------------

    def on_smooth_confirm_clicked(self, *args):

        for Property in self.block_properties:
            name = Property.getAttr("name")
            value = Property.getAttr("value")

            new_value = value
            if name == "type":
                Active = self.widgets['SMOOType'].get_active()
                #  if int(Active) == 0:
                #       Property.value = unicode("CV_BLUR_NO_SCALE")
                if int(Active) == 0:
                    new_value = unicode("CV_BLUR")
                if int(Active) == 1:
                    new_value = unicode("CV_GAUSSIAN")
                if int(Active) == 2:
                    new_value = unicode("CV_MEDIAN")
                    #  if int(Active) == 4:
                    #       Property.value = unicode("CV_BILATERAL")

                    # if Property.name == "param1":
                    # Property.value = unicode( str( int(self.widgets['SMOOParam1'].get_value( ) ) ) )

            if name == "param1":
                Value = self.widgets['SMOOParam1'].get_value()
                if ((Value % 2) <> 0):
                    new_value = unicode(str(int(Value)))
                elif (Value != 0):
                    new_value = unicode(str(int(Value - 1)))
                else:
                    new_value = unicode(str(int(Value)))

            if name == "param2":
                Value = self.widgets['SMOOParam2'].get_value()
                if ((Value % 2) <> 0):
                    new_value = unicode(str(int(Value)))
                elif (Value != 0):
                    new_value = unicode(str(int(Value - 1)))
                else:
                    new_value = unicode(str(int(Value)))

            Property.setAttr("value", new_value)

        self.m_oS2iBlockProperties.SetPropertiesXML(self.m_oPropertiesXML)

        self.m_oS2iBlockProperties.SetBorderColor(self.m_oBorderColor)

        self.m_oS2iBlockProperties.SetBackColor(self.m_oBackColor)

        self.widgets['Properties'].destroy()

        # ----------------------------------------------------------------------


# SmoothProperties = Properties()
# SmoothProperties.show( center=0 )

# ------------------------------------------------------------------------------
# Code generation
# ------------------------------------------------------------------------------
def generate(blockTemplate):
    for propIter in blockTemplate.properties:
        if propIter[0] == 'type':
            typeValue = propIter[1]
        elif propIter[0] == 'param1':
            param1Value = propIter[1]
        elif propIter[0] == 'param2':
            param2Value = propIter[1]
    blockTemplate.imagesIO = \
        'IplImage * block$$_img_i1 = NULL;\n' + \
        'IplImage * block$$_img_o1 = NULL;\n' + \
        'IplImage * block$$_img_t = NULL;\n'
    blockTemplate.functionCall = '\nif(block$$_img_i1){\n' + \
                                 'block$$_img_o1 = cvCreateImage(cvSize(block$$_img_i1->width,block$$_img_i1->height), block$$_img_i1->depth,block$$' + \
                                 '_img_i1->nChannels);\n' + \
                                 'cvSmooth(block$$_img_i1, block$$_img_o1 ,' + typeValue + ',' + param1Value + ',' + param2Value + ',0,0);}\n'
    blockTemplate.dealloc = 'cvReleaseImage(&block$$_img_o1);\n' + \
                            'cvReleaseImage(&block$$_img_i1);\n' + \
                            'cvReleaseImage(&block$$_img_t);\n'


# ------------------------------------------------------------------------------
# Block Setup
# ------------------------------------------------------------------------------
def getBlock():
    return {"Label": _("Smooth"),
            "Path": {"Python": "smooth",
                     "Glade": "glade/smooth.ui",
                     "Xml": "xml/smooth.xml"},
            "Icon": "images/smooth.png",
            "Color": "50:125:50:150",
            "InTypes": {0: "HRP_IMAGE"},
            "OutTypes": {0: "HRP_IMAGE"},
            "Description": _("Operação de filtragem destinada suavizar uma imagem"),
            "TreeGroup": _("Filters and Color Conversion")
            }
