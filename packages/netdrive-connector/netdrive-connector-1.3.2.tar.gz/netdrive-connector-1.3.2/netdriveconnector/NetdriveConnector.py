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

import sys, os, subprocess
from PyQt4 import QtCore, QtGui, uic
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from LoginDialog import LoginDialog
from RootPasswordDialog import RootPasswordDialog

try:
    _fromUtf8 = QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

( Ui_NetdriveConnector, QWidget ) = uic.loadUiType( os.path.join(os.path.dirname( __file__ ), 'NetdriveConnector.ui' ))

TOOLTIP_PREFIX = "Full fstab entry:  "
SSHFS_INVALID_OPTIONS = ['users','noauto']

class NetdriveConnector ( QWidget ):

    
    def __init__ ( self, parent = None ):
        QWidget.__init__( self, parent )
        self.ui = Ui_NetdriveConnector()
        self.ui.setupUi( self )
        
        self.getHomeFolder()

        self.dependencyCheck()

        self.loadConnectionsTable()

    def __del__ ( self ):
        self.ui = None

    def dependencyCheck(self):
        shellCommand = str("groups | egrep 'davfs2 | davfs2'")
        if subprocess.call(shellCommand,shell=True) != 0:
            warningMessage = QtGui.QMessageBox(self)
            warningMessage.setWindowTitle("Netdrive Connector - Warning")
            message =\
"""
WARNING: The currently logged in user is not a member of the davfs2 group.

This will likely cause the mounting of WebDAV connections to fail.

Consider adding this user account to the davfs2 group. Consult your OS/distributions guide for how to add a user to a group.
"""
            warningMessage.setText(message)
            warningMessage.setIcon(QtGui.QMessageBox.Warning)
            warningMessage.show()
 
    def loadConnectionsTable(self):
        
        self.ui.connectionsTableWidget.clear()
        
        allConnections = []
        
        if self.ui.currentUserCheckBox.isChecked():
            grepForCurrentUser = " | grep " + self.homeFolder
        else:
            grepForCurrentUser = ""
        
        shellCommand = str("cat /etc/fstab | grep -v '^#' | grep ' davfs '" + grepForCurrentUser)
        if subprocess.call(shellCommand,shell=True) == 0:
            davfsConnections = str (subprocess.check_output(shellCommand,shell=True)).splitlines()
            allConnections = allConnections + davfsConnections
        else:
            davfsConnections = None
        
        shellCommand = str("cat /etc/fstab | grep -v '^#' | grep ' fuse.sshfs '" + grepForCurrentUser)
        if subprocess.call(shellCommand,shell=True) == 0:
            sftpConnections = str (subprocess.check_output(shellCommand,shell=True)).splitlines()
            allConnections = allConnections + sftpConnections
        else:
            sftpConnections = None
        

        self.ui.connectionsTableWidget.setColumnCount(2)
        self.ui.connectionsTableWidget.setHorizontalHeaderLabels(('URL','Mount Point'))
        self.ui.connectionsTableWidget.setRowCount(len(allConnections))
        
        row = 0
        for rowData in allConnections:
            url = rowData.split(' ')[0]
            mountPoint = rowData.split(' ')[1]
            
            shellCommand = str("mount | grep ' " + str(mountPoint) + " '")
            if subprocess.call(shellCommand,shell=True) == 0:
                bgColour = QColor(100,200,100,80)
            else:
                bgColour = QColor(250,120,10,80)
            
            tableItem = QtGui.QTableWidgetItem(url)
            self.ui.connectionsTableWidget.setItem(row, 0, tableItem)
            tableItem.setBackgroundColor(bgColour)
            tableItem.setToolTip(TOOLTIP_PREFIX + rowData)
            
            tableItem = QtGui.QTableWidgetItem(mountPoint)
            self.ui.connectionsTableWidget.setItem(row, 1, tableItem)
            tableItem.setBackgroundColor(bgColour)
            tableItem.setToolTip(TOOLTIP_PREFIX + rowData)
            
            row += 1
            
        self.ui.connectionsTableWidget.resizeColumnsToContents()
        self.ui.connectionsTableWidget.resizeRowsToContents()
	header = self.ui.connectionsTableWidget.horizontalHeader()
	header.setStretchLastSection(True)
  

    def clearSftpFields(self):
        self.ui.sftpUsernameLineEdit.clear()
        self.ui.sftpHostnameLineEdit.clear()
        self.ui.sftpPortSpinBox.setValue(22)
        self.ui.sftpPathLineEdit.clear()
        self.ui.sftpMountpointLineEdit.clear()
        self.ui.sftpPasswordlessCheckBox.setChecked(True)
        self.ui.sftpPasswordLineEdit.clear()
        self.ui.sftpAutoMountCheckBox.setCheckable(True)
        self.ui.sftpAutoMountCheckBox.setChecked(False)


    def clearWebdavFields(self):
        self.ui.webdavServerUrlLineEdit.clear()
        self.ui.webdavUriLineEdit.clear()
        self.ui.webdavMountpointLineEdit.clear()
        self.ui.httpRadioButton.setChecked(True)
        self.ui.webdavProtocolLbl.setText("http://")
        self.ui.webdavPortSpinBox.setValue(80)
        self.ui.webdavUsernameLineEdit.clear()
        self.ui.webdavPasswordLineEdit.clear()
        self.ui.webdavAutoMountCheckBox.setCheckable(True)
        self.ui.webdavAutoMountCheckBox.setChecked(False)

    def currentUserCheckBoxClicked(self):
        self.loadConnectionsTable()
        
    def sftpPasswordlessCheckBoxClicked(self):
        
        if self.ui.sftpPasswordlessCheckBox.isChecked():
            self.ui.sftpAutoMountCheckBox.setCheckable(True)
        else:
            self.ui.sftpAutoMountCheckBox.setChecked(False)
            self.ui.sftpAutoMountCheckBox.setCheckable(False)
            
    def webdavSavePasswordCheckBoxClicked(self):
        
        if self.ui.webdavSavePasswordCheckBox.isChecked():
            self.ui.webdavAutoMountCheckBox.setCheckable(True)
        else:
            self.ui.webdavAutoMountCheckBox.setChecked(False)
            self.ui.webdavAutoMountCheckBox.setCheckable(False)
            
        
    
    def connectBtnClicked(self):

        
        if len(self.ui.connectionsTableWidget.selectedItems()) < 1:
            warningMessage = QtGui.QMessageBox(self)
            warningMessage.setWindowTitle("Netdrive Connector - Error")
            warningMessage.setText("No connection selected. Please select a filesystem to connect.")
            warningMessage.setIcon(QtGui.QMessageBox.Warning)
            warningMessage.show()
            return False
            
        toolTipText = str ( self.ui.connectionsTableWidget.selectedItems()[0].toolTip() )
        toConnect = toolTipText[toolTipText.find(TOOLTIP_PREFIX)+len(TOOLTIP_PREFIX):]
        filesystem = toConnect.split(' ')[0]
        mountpoint =  toConnect.split(' ')[1]
        fsType = toConnect.split(' ')[2]
        fstabMountOptions = toConnect.split(' ')[3].split(',')
        mountOptions = ""
        for option in fstabMountOptions:
            if option not in SSHFS_INVALID_OPTIONS:
                mountOptions = mountOptions + option + ","
        if mountOptions is not "":
            mountOptions = mountOptions[:-1]
        
        shellCommand = str("mount | grep ' " + mountpoint + " '")
        if subprocess.call(shellCommand,shell=True) == 0:
            warningMessage = QtGui.QMessageBox(self)
            warningMessage.setWindowTitle("Netdrive Connector - Error")
            warningMessage.setText("The selected filesystem is already mounted.")
            warningMessage.setIcon(QtGui.QMessageBox.Warning)
            warningMessage.show()
            return False

        if fsType == "davfs":
            shellCommand = str("cat '" + self.homeFolder + "/.davfs2/secrets' | grep '^" + filesystem +" '")
            if subprocess.call(shellCommand,shell=True) != 0:
                isWebdavPasswordSaved = False
                loginDialog = LoginDialog("")
                loginDialog.exec_()
                if not loginDialog.isOK:
                    return False
                else:
                    username,password = loginDialog.getLoginCredentials()
                    shellCommand = str("echo '" + filesystem + " " + username + " " + password + "' >> '" + self.homeFolder + "/.davfs2/secrets'")
                    if subprocess.call(shellCommand,shell=True) != 0:
                        warningMessage = QtGui.QMessageBox(self)
                        warningMessage.setWindowTitle("Netdrive Connector - Error")
                        warningMessage.setText("ERROR: Failed to add username/password to secrets file.")
                        warningMessage.setIcon(QtGui.QMessageBox.Warning)
                        warningMessage.show()
            else:
                isWebdavPasswordSaved = True
                
            shellCommand = str("mount " + mountpoint)
            if subprocess.call(shellCommand,shell=True) != 0:
                warningMessage = QtGui.QMessageBox(self)
                warningMessage.setWindowTitle("Netdrive Connector - Error")
                warningMessage.setText("Failed to connect filesystem: " + filesystem)
                warningMessage.setIcon(QtGui.QMessageBox.Warning)
                warningMessage.show()
            else:
                successMessage = QtGui.QMessageBox(self)
                successMessage.setWindowTitle("Netdrive Connector - Success")
                successMessage.setText("Successfully connected the remote filesystem: " + filesystem )
                successMessage.setIcon(QtGui.QMessageBox.Information)
                successMessage.show()
                
            if not isWebdavPasswordSaved:
                # TODO: check for GNU/LInux or *BSD and use specific sed in-place command
                shellCommand =  str('sed -i "\|^' + filesystem + ' .*|d" "' + self.homeFolder + '/.davfs2/secrets"')
                if subprocess.call(shellCommand,shell=True) != 0:
                    warningMessage = QtGui.QMessageBox(self)
                    warningMessage.setWindowTitle("Netdrive Connector - Error")
                    warningMessage.setText("ERROR: Failed to remove username/password from secrets file.")
                    warningMessage.setIcon(QtGui.QMessageBox.Warning)
                    warningMessage.show()

        if fsType == "fuse.sshfs":
            
            # NOTE: since we rely on a ssh-askpass to graphically prompt for password (no tty),
            #       we need to use sshfs instead of mount. At least on Slackware, mount does not initiate the ssh-askpass. 
            
            shellCommand = str("sshfs " + filesystem + " " + mountpoint + " -o " + mountOptions)
            print shellCommand
            if subprocess.call(shellCommand, shell=True) != 0:
                warningMessage = QtGui.QMessageBox(self)
                warningMessage.setWindowTitle("Netdrive Connector - Error")
                warningMessage.setText("Failed to connect filesystem: " + filesystem)
                warningMessage.setIcon(QtGui.QMessageBox.Warning)
                warningMessage.show()
            else:
                successMessage = QtGui.QMessageBox(self)
                successMessage.setWindowTitle("Netdrive Connector - Success")
                successMessage.setText("Successfully connected the remote filesystem: " + filesystem )
                successMessage.setIcon(QtGui.QMessageBox.Information)
                successMessage.show()


        self.loadConnectionsTable()

    def disconnectBtnClicked(self):
 
        if len(self.ui.connectionsTableWidget.selectedItems()) < 1:
            warningMessage = QtGui.QMessageBox(self)
            warningMessage.setWindowTitle("Netdrive Connector - Error")
            warningMessage.setText("No connection selected. Please select a filesystem to disconnect.")
            warningMessage.setIcon(QtGui.QMessageBox.Warning)
            warningMessage.show()
            return False

        toolTipText = str ( self.ui.connectionsTableWidget.selectedItems()[0].toolTip() )
        toDisconnect = toolTipText[toolTipText.find(TOOLTIP_PREFIX)+len(TOOLTIP_PREFIX):]
        mountpoint =  toDisconnect.split(' ')[1]
        fs_type =  toDisconnect.split(' ')[2]
 
        shellCommand = str("mount | grep ' " + mountpoint + " '")
        if subprocess.call(shellCommand,shell=True) != 0:
            warningMessage = QtGui.QMessageBox(self)
            warningMessage.setWindowTitle("Netdrive Connector - Error")
            warningMessage.setText("The selected filesystem is not currently mounted.")
            warningMessage.setIcon(QtGui.QMessageBox.Warning)
            warningMessage.show()
            return False

        if fs_type == "fuse.sshfs":
            shellCommand = str("fusermount -u " + mountpoint)
        else:
            shellCommand = str("umount " + mountpoint)
        if subprocess.call(shellCommand,shell=True) != 0:
            warningMessage = QtGui.QMessageBox(self)
            warningMessage.setWindowTitle("Netdrive Connector - Error")
            warningMessage.setText("Failed to disconnect mount point: " + mountpoint + " . Try to save and close all open files, exit the folder and try again." )
            warningMessage.setIcon(QtGui.QMessageBox.Warning)
            warningMessage.show()
        else:
            successMessage = QtGui.QMessageBox(self)
            successMessage.setWindowTitle("Netdrive Connector - Success")
            successMessage.setText("Successfully disconnected the remote filesystem mounted at: " + mountpoint)
            successMessage.setIcon(QtGui.QMessageBox.Information)
            successMessage.show()

        self.loadConnectionsTable()

    def removeBtnClicked(self):

        if len(self.ui.connectionsTableWidget.selectedItems()) < 1:
            warningMessage = QtGui.QMessageBox(self)
            warningMessage.setWindowTitle("Netdrive Connector - Error")
            warningMessage.setText("No connection selected. Please select a filesystem to remove.")
            warningMessage.setIcon(QtGui.QMessageBox.Warning)
            warningMessage.show()
            return False

        toolTipText = str ( self.ui.connectionsTableWidget.selectedItems()[0].toolTip() )
        connection = toolTipText[toolTipText.find(TOOLTIP_PREFIX)+len(TOOLTIP_PREFIX):]
        filesystem = connection.split(' ')[0]
        mountpoint =  connection.split(' ')[1]
        fsType = connection.split(' ')[2]

        shellCommand = str("mount | grep ' " + mountpoint + " '")
        if subprocess.call(shellCommand,shell=True) == 0:
            warningMessage = QtGui.QMessageBox(self)
            warningMessage.setWindowTitle("Netdrive Connector - Error")
            warningMessage.setText("The selected filesystem is currently mounted. Disconnect before trying to remove the connection.")
            warningMessage.setIcon(QtGui.QMessageBox.Warning)
            warningMessage.show()
            return False

        reply = QtGui.QMessageBox.question(self, 'Netdrive Connector',"Are you sure that you want to remove this connection?", \
                QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.No:
            return False

        if fsType == "davfs":
            removeCmd = "remove-webdav-connector"
        elif fsType == "fuse.sshfs":
            removeCmd = "remove-sftp-connector"

        rootPasswordDialog = RootPasswordDialog()
        rootPasswordDialog.exec_()
        if not rootPasswordDialog.isOK:
            return False

        password = rootPasswordDialog.getRootPassword()

        removeConnectorParms = filesystem + " "  + mountpoint
        if subprocess.call(['unbuffer','netdrive-connector_run-as-root', str(password), removeCmd, removeConnectorParms]) !=0:
            warningMessage = QtGui.QMessageBox(self)
            warningMessage.setWindowTitle("Netdrive Connector - Error")
            warningMessage.setText("Failed to remove the connection to : " + filesystem )
            warningMessage.setIcon(QtGui.QMessageBox.Warning)
            warningMessage.show()
        

        mountpointNoSlashes = str(mountpoint).replace("/","_")

        shellCommand = str("rm " + self.homeFolder + "/.config/autostart/netdrive_connector" + mountpointNoSlashes + ".desktop" )
        if subprocess.call(shellCommand,shell=True) != 0:
            print "WARNING: problem whilst removing autostart file."

        self.loadConnectionsTable()

    def refreshBtnClicked(self):
        
        self.loadConnectionsTable()

    def addSftpBtnClicked(self):
        
        sftpUsername= self.ui.sftpUsernameLineEdit.text()
        sftpHostname= self.ui.sftpHostnameLineEdit.text()
        sftpPort = str(self.ui.sftpPortSpinBox.value())
        sftpMountpoint = self.ui.sftpMountpointLineEdit.text()
        sftpPath = self.ui.sftpPathLineEdit.text()
        sftpPassword = self.ui.sftpPasswordLineEdit.text()
        
        if len(str(sftpUsername).replace(" ","")) < 1:
            warningMessage = QtGui.QMessageBox(self)
            warningMessage.setWindowTitle("Netdrive Connector - Error")
            warningMessage.setText("No valid username. Please enter a valid username.")
            warningMessage.setIcon(QtGui.QMessageBox.Warning)
            warningMessage.show()
            return False

        if len(str(sftpHostname).replace(" ","")) < 1:
            warningMessage = QtGui.QMessageBox(self)
            warningMessage.setWindowTitle("Netdrive Connector - Error")
            warningMessage.setText("No valid hostname. Please enter a valid hostname.")
            warningMessage.setIcon(QtGui.QMessageBox.Warning)
            warningMessage.show()
            return False

        if len(str(sftpPath).replace(" ","")) < 1:
            warningMessage = QtGui.QMessageBox(self)
            warningMessage.setWindowTitle("Netdrive Connector - Error")
            warningMessage.setText("No valid path. Please enter a valid path.")
            warningMessage.setIcon(QtGui.QMessageBox.Warning)
            warningMessage.show()
            return False

        if len(str(sftpMountpoint).replace(" ","")) < 1:
            warningMessage = QtGui.QMessageBox(self)
            warningMessage.setWindowTitle("Netdrive Connector - Error")
            warningMessage.setText("No mount point (folder) selected. Please select a folder to use as a mount point.")
            warningMessage.setIcon(QtGui.QMessageBox.Warning)
            warningMessage.show()
            return False

        if self.ui.sftpPasswordlessCheckBox.isChecked() and len(str(sftpPassword).replace(" ","")) < 1:
            warningMessage = QtGui.QMessageBox(self)
            warningMessage.setWindowTitle("Netdrive Connector - Error")
            warningMessage.setText("No SFTP password supplied. Please enter the password for the user on the server.")
            warningMessage.setIcon(QtGui.QMessageBox.Warning)
            warningMessage.show()
            return False

        rootPasswordDialog = RootPasswordDialog()
        rootPasswordDialog.exec_()
        if not rootPasswordDialog.isOK:
            return False

        password = rootPasswordDialog.getRootPassword()
        
        if self.ui.sftpPasswordlessCheckBox.isChecked():
            connectorParms = sftpUsername + "@" + sftpHostname + ":" + sftpPort + "/" + sftpPath + " " + sftpMountpoint + " key " + sftpPassword
        else:
            connectorParms = sftpUsername + "@" + sftpHostname + ":" + sftpPort + "/" + sftpPath + " " + sftpMountpoint

        if subprocess.call(['unbuffer','netdrive-connector_run-as-root', str(password), 'add-sftp-connector', connectorParms]) !=0:
            warningMessage = QtGui.QMessageBox(self)
            warningMessage.setWindowTitle("Netdrive Connector - Error")
            warningMessage.setText("Failed to add the connection. ")
            warningMessage.setIcon(QtGui.QMessageBox.Warning)
            warningMessage.show()
        else:
            if self.ui.sftpAutoMountCheckBox.isChecked():
                self.addAutoMount(sftpMountpoint, "fuse.sshfs")
            self.clearSftpFields()
            self.loadConnectionsTable()
    
    def addWebdavBtnClicked(self):
        
        webdavProtocol = self.ui.webdavProtocolLbl.text()
        webdavURL = self.ui.webdavServerUrlLineEdit.text()
        webdavPort = str(self.ui.webdavPortSpinBox.value())
        webdavMountpoint = self.ui.webdavMountpointLineEdit.text()
        webdavURI = self.ui.webdavUriLineEdit.text()
        webdavUsername = self.ui.webdavUsernameLineEdit.text()
        webdavPassword = self.ui.webdavPasswordLineEdit.text()
        
        
        if len(str(webdavURL).replace(" ","")) < 1:
            warningMessage = QtGui.QMessageBox(self)
            warningMessage.setWindowTitle("Netdrive Connector - Error")
            warningMessage.setText("No valid server URL. Please enter a valid server URL.")
            warningMessage.setIcon(QtGui.QMessageBox.Warning)
            warningMessage.show()
            return False
            
        if len(str(webdavURI).replace(" ","")) < 1:
            warningMessage = QtGui.QMessageBox(self)
            warningMessage.setWindowTitle("Netdrive Connector - Error")
            warningMessage.setText("No valid WebDAV URI. Please enter a valid WebDAV URI.")
            warningMessage.setIcon(QtGui.QMessageBox.Warning)
            warningMessage.show()
            return False
            
        if len(str(webdavMountpoint).replace(" ","")) < 1:
            warningMessage = QtGui.QMessageBox(self)
            warningMessage.setWindowTitle("Netdrive Connector - Error")
            warningMessage.setText("No mount point (folder) selected. Please select a folder to use as a mount point.")
            warningMessage.setIcon(QtGui.QMessageBox.Warning)
            warningMessage.show()
            return False
            
        if self.ui.webdavSavePasswordCheckBox.isChecked() and len(str(webdavUsername).replace(" ","")) < 1:
            warningMessage = QtGui.QMessageBox(self)
            warningMessage.setWindowTitle("Netdrive Connector - Error")
            warningMessage.setText("No valid WebDAV username supplied. Please enter a valid WebDAV username.")
            warningMessage.setIcon(QtGui.QMessageBox.Warning)
            warningMessage.show()
            return False
            
        if self.ui.webdavSavePasswordCheckBox.isChecked() and len(str(webdavPassword).replace(" ","")) < 1:
            warningMessage = QtGui.QMessageBox(self)
            warningMessage.setWindowTitle("Netdrive Connector - Error")
            warningMessage.setText("No WebDAV password supplied. Please enter the WebDAV password.")
            warningMessage.setIcon(QtGui.QMessageBox.Warning)
            warningMessage.show()
            return False

        rootPasswordDialog = RootPasswordDialog()
        rootPasswordDialog.exec_()
        if not rootPasswordDialog.isOK:
            return False

        password = rootPasswordDialog.getRootPassword()
        
        if self.ui.webdavSavePasswordCheckBox.isChecked():
            connectorParms = webdavProtocol + webdavURL + ":" + webdavPort + "/" + webdavURI + " " + webdavMountpoint + " " + webdavUsername + " " + webdavPassword
        else:
            connectorParms = webdavProtocol + webdavURL + ":" + webdavPort + "/" + webdavURI + " " + webdavMountpoint
        if subprocess.call(['unbuffer','netdrive-connector_run-as-root', str(password), 'add-webdav-connector', connectorParms]) !=0:
            warningMessage = QtGui.QMessageBox(self)
            warningMessage.setWindowTitle("Netdrive Connector - Error")
            warningMessage.setText("Failed to add the connection. ")
            warningMessage.setIcon(QtGui.QMessageBox.Warning)
            warningMessage.show()
        else:
            if self.ui.webdavAutoMountCheckBox.isChecked():
                self.addAutoMount(webdavMountpoint, "davfs")
            self.clearWebdavFields()
            self.loadConnectionsTable()

    def sftpMountpointBtnClicked(self):
        
        mountpoint = QtGui.QFileDialog.getExistingDirectory(self, 'Select mount point',self.homeFolder)
        
        if mountpoint == self.homeFolder:
            warningMessage = QtGui.QMessageBox(self)
            warningMessage.setWindowTitle("Netdrive Connector - Warning")
            warningMessage.setText("WARNING: The selected folder is your home folder. Mounting a remote filesystem to your home folder is not recommended.")
            warningMessage.setIcon(QtGui.QMessageBox.Warning)
            warningMessage.show()
            
        if self.isMountpointOwnedByCurrentUser(mountpoint):
            self.ui.sftpMountpointLineEdit.setText(mountpoint)
        else:
            errorMessage = QtGui.QErrorMessage(self)
            errorMessage.setWindowTitle("Netdrive Connector - Error")
            errorMessage.showMessage("ERROR: you are not the owner of the selected folder. Please change ownership of the folder or select a different mount point.")
    
    def webdavMountpointBtnClicked(self):
        
        mountpoint = QtGui.QFileDialog.getExistingDirectory(self, 'Select mount point',self.homeFolder)
        
        if mountpoint == self.homeFolder:
            warningMessage = QtGui.QMessageBox(self)
            warningMessage.setWindowTitle("Netdrive Connector - Warning")
            warningMessage.setText("WARNING: The selected folder is your home folder. Mounting a remote filesystem to your home folder is not recommended.")
            warningMessage.setIcon(QtGui.QMessageBox.Warning)
            warningMessage.show()
            
        if self.isMountpointOwnedByCurrentUser(mountpoint):
            self.ui.webdavMountpointLineEdit.setText(mountpoint)
        else:
            errorMessage = QtGui.QErrorMessage(self)
            errorMessage.setWindowTitle("Netdrive Connector - Error")
            errorMessage.showMessage("ERROR: you are not the owner of the selected folder. Please change ownership of the folder or select a different mount point.")
    
    def httpRadioBtnClicked(self):
        
        self.ui.webdavProtocolLbl.setText("http://")
        
        if self.ui.webdavPortSpinBox.value() == 443:
            self.ui.webdavPortSpinBox.setValue(80)
    
    def httpsRadioBtnClicked(self):
        
        self.ui.webdavProtocolLbl.setText("https://")
        
        if self.ui.webdavPortSpinBox.value() == 80:
            self.ui.webdavPortSpinBox.setValue(443)
            
    def getHomeFolder(self):
        
        self.homeFolder = str (subprocess.check_output("echo $HOME",shell=True)).splitlines()[0]
            
    def isMountpointOwnedByCurrentUser(self, mountpoint):
        
        currentUser = str (subprocess.check_output("whoami",shell=True)).splitlines()[0]
        
        shellCommand = str ("ls -ld " + mountpoint + " | awk '{print $3}'")
        
        folderOwner = str (subprocess.check_output(shellCommand,shell=True)).splitlines()[0]
        
        if folderOwner != currentUser:
            return False
        else:
            return True
            
    def addAutoMount(self, mountpoint, fs_type):
        
        mountpointNoSlashes = str(mountpoint).replace("/","_")
        
        fileContents =\
"""
[Desktop Entry]
Name=Netdrive AutoMounter
Hidden=false
StartupNotify=false
Terminal=false
TerminalOptions=
Type=Application
"""
        fileContents = str(fileContents + "Exec=netdrive-connector_automountd " + mountpoint + " " + fs_type)
        shellCommand = str("if [ ! -d " + self.homeFolder + "/.config/autostart ]; then mkdir " + self.homeFolder + "/.config/autostart ; fi ; echo '" + fileContents + "' > " + self.homeFolder + "/.config/autostart/netdrive_connector" + mountpointNoSlashes + ".desktop" )
        if subprocess.call(shellCommand,shell=True) != 0:
            warningMessage = QtGui.QMessageBox(self)
            warningMessage.setWindowTitle("Netdrive Connector - Error")
            warningMessage.setText("An error occured whilst creating the autostart file in " + self.homeFolder + "/.config/autostart .")
            warningMessage.setIcon(QtGui.QMessageBox.Warning)
            warningMessage.show()
            return False

