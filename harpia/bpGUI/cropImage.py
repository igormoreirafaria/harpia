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
import gettext
from harpia.utils.XMLUtils import XMLParser

_ = gettext.gettext
gettext.bindtextdomain(APP, DIR)
gettext.textdomain(APP)


# ----------------------------------------------------------------------

class Properties(GladeWindow, S2iCommonProperties):
    # ----------------------------------------------------------------------

    def __init__(self, PropertiesXML, S2iBlockProperties):
        self.m_sDataDir = os.environ['HARPIA_DATA_DIR']

        filename = self.m_sDataDir + 'glade/cropImage.ui'
        self.m_oPropertiesXML = PropertiesXML
        self.m_oS2iBlockProperties = S2iBlockProperties

        widget_list = [
            'Properties',
            'BackgroundColor',
            'BorderColor',
            'HelpView'
        ]

        handlers = [
            'on_cancel_clicked',
            'on_prop_confirm_clicked',
            'on_BackColorButton_clicked',
            'on_BorderColorButton_clicked'
        ]

        top_window = 'Properties'

        GladeWindow.__init__(self, filename, top_window, widget_list, handlers)

        self.configure()
        # load help text
        # t_oS2iHelp = XMLParser(self.m_sDataDir + 'help/cropImage' + _('_en.help'))

        # t_oTextBuffer = gtk.TextBuffer()

        # t_oTextBuffer.set_text(unicode(str(t_oS2iHelp.getTag("help").getTag("content").getTagContent())))

        # self.widgets['HelpView'].set_buffer(t_oTextBuffer)

    # ----------------------------------------------------------------------

    def __del__(self):
        pass

    # ----------------------------------------------------------------------


    def getHelp(self):
        return "Corta a Imagem de acordo com o Retangulo\n de entrada."


    #-----------------------------------------------------------------------

    def on_prop_confirm_clicked(self, *args):
        self.m_oS2iBlockProperties.SetPropertiesXML(self.m_oPropertiesXML)

        self.m_oS2iBlockProperties.SetBorderColor(self.m_oBorderColor)
        self.m_oS2iBlockProperties.SetBackColor(self.m_oBackColor)
        self.widgets['Properties'].destroy()

        # ----------------------------------------------------------------------


# propProperties = Properties()()
# propProperties.show( center=0 )

# ------------------------------------------------------------------------------
# Code generation
# ------------------------------------------------------------------------------
def generate(blockTemplate):
    import harpia.gerador
    # for propIter in blockTemplate.properties:
    # if propIter[0] == 'offset_x':
    # offset_x = propIter[1]
    # if propIter[0] == 'offset_y':
    # offset_y = propIter[1]
    blockTemplate.imagesIO = \
        'IplImage * block$$_img_i1 = NULL;\n' + \
        'IplImage * block$$_img_o1 = NULL;\n' + \
        'CvRect  block$$_rect_i2;\n'
    blockTemplate.functionCall = '\nif(block$$_img_i1){\n' + \
                                 '	block$$_rect_i2.x = MAX(0,block$$_rect_i2.x);//Check whether point is negative\n' + \
                                 '	block$$_rect_i2.y = MAX(0,block$$_rect_i2.y);\n' + \
                                 '	block$$_rect_i2.x = MIN(block$$_img_i1->width-1,block$$_rect_i2.x);//Check whether point is out of the image\n' + \
                                 '	block$$_rect_i2.y = MIN(block$$_img_i1->height-1,block$$_rect_i2.y);\n' + \
                                 '	block$$_rect_i2.width = MIN(block$$_img_i1->width-block$$_rect_i2.x,block$$_rect_i2.width);//Check whether rect reaches out of the image\n' + \
                                 '	block$$_rect_i2.height = MIN(block$$_img_i1->height-block$$_rect_i2.y,block$$_rect_i2.height);\n' + \
                                 '	block$$_img_o1 = cvCreateImage(cvSize(block$$_rect_i2.width,block$$_rect_i2.height),' + \
                                 ' block$$_img_i1->depth,block$$_img_i1->nChannels);\n' + \
                                 '	cvSetImageROI(block$$_img_i1,block$$_rect_i2);\n' + \
                                 '	cvCopyImage(block$$_img_i1,block$$_img_o1);\n' + \
                                 '}\n'
    blockTemplate.dealloc = 'cvReleaseImage(&block$$_img_o1);\n' + \
                            'cvReleaseImage(&block$$_img_i1);\n'


# ------------------------------------------------------------------------------
# Block Setup
# ------------------------------------------------------------------------------
def getBlock():
    return {'Label': _('Crop Image'),
            'Path': {'Python': 'cropImage',
                     'Glade': 'glade/cropImage.ui',
                     'Xml': 'xml/cropImage.xml'},
            'Icon': 'images/cropImage.png',
            'Color': '50:50:200:150',
            'InTypes': {0: 'HRP_IMAGE', 1: 'HRP_RECT'},
            'OutTypes': {0: 'HRP_IMAGE'},
            'Description': _('Crops the input image according to input Rectangle'),
            'TreeGroup': _('Experimental')
            }
