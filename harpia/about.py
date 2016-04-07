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
#----------------------------------------------------------------------

# Imported class GladeWindow
from harpia.GladeWindow import GladeWindow

import os

## Implements the about window in the Frontend.
class About( GladeWindow ):
    """
        The class implements the functionalities for showing the window and handles the singnals.
        Allow the user to see information about the Harpia Project.
        
    """
    #----------------------------------------------------------------------

    def __init__( self ):
        """
            Sets the Glade file where the about window is defined and Connects the
            signals and its handlers through GladeWindow __init__
        """
            
        ## Get the file with the about window
        self.m_sDataDir = os.environ['HARPIA_DATA_DIR']
        filename = self.m_sDataDir+'glade/about.ui'
        ## The widget list
        widget_list = [
                'about',
                'harpia_name',
                'about_s2i_logo',
                'about_finep_logo'
                ]
        handlers = [            ]
        # The top three widget
        top_window = 'about'
        
        # Starts the Glade Window
        GladeWindow.__init__(self, filename, top_window, widget_list, handlers)
        # Set the Icons and logos
        self.widgets['about'].set_icon_from_file(self.m_sDataDir+"images/harpia_ave.png")
        self.widgets['harpia_name'].set_from_file(self.m_sDataDir+"images/harpia_name.png")
        self.widgets['about_s2i_logo'].set_from_file(self.m_sDataDir+"images/s2ilogo.png")
        self.widgets['about_finep_logo'].set_from_file(self.m_sDataDir+"images/finep_logo.gif")
        #----------------------------------------------------------------------
    def __del__(self):
        pass
    #---------------------------------------------------------------------- 

