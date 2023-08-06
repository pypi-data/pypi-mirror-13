# Copyright (c) 2015, Euan Thoms
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
# 
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import sys, os
from PyQt4 import QtCore, QtGui, uic
from PyQt4.QtCore import *
from PyQt4.QtGui import *

try:
    _fromUtf8 = QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

( Ui_LoginDialog, QDialog ) = uic.loadUiType( os.path.join(os.path.dirname( __file__ ), 'LoginDialog.ui' ))

class LoginDialog(QtGui.QDialog):
    
    

    def __init__(self, username):
        QtGui.QWidget.__init__(self)

        self.ui = Ui_LoginDialog()
        self.ui.setupUi(self)
        
        self.ui.usernameLineEdit.setText(username)
        self.isOK = False
        
    def loginOK(self):
        
        self.username = self.ui.usernameLineEdit.text()
        self.password = self.ui.passwordLineEdit.text()
        
        if len(self.username) < 1:
            warningMessage = QtGui.QMessageBox(self)
            warningMessage.setWindowTitle("Data Entry Error")
            warningMessage.setText("No usernames supplied!")
            warningMessage.setIcon(QtGui.QMessageBox.Warning)
            warningMessage.show()
            return False
            
        if len(self.password) < 1:
            warningMessage = QtGui.QMessageBox(self)
            warningMessage.setWindowTitle("Data Entry Error")
            warningMessage.setText("No password supplied!")
            warningMessage.setIcon(QtGui.QMessageBox.Warning)
            warningMessage.show()
            return False
            
        self.isOK = True
        self.accept()
        
    def loginCancel(self):
        self.isOK = False
        self.reject()
        
    def getLoginCredentials(self):
        return self.username,self.password
