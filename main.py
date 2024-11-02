from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QComboBox, QPlainTextEdit, QDialog, QSystemTrayIcon, QMenu, QAction, QMessageBox
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt, QTimer, QSize
import subprocess
import os
import requests
import sys
from ipaddress import ip_address
class AboutDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('DNS Changer')
        self.setGeometry(600, 600, 400, 100)

        about_label = QLabel(
            "DNS Changer is a Python program that allows you to easily switch between different DNS servers on your Windows PC.\n"
            "You can easily delete the DNS on your system.\n"
            "You can also minimize the app in the system tray and access it from the notification icon.\n"
            "This project is open source and developed by 2xAm1r.\n"
            "If supported and used, a better version will be released.",
            self
        )
        about_label.setWordWrap(True)

        layout = QVBoxLayout(self)
        layout.addWidget(about_label)


class NetworkChangerApp(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Dns Changer By 2xAm1r')
        self.setGeometry(600, 250, 400, 300)
        self.setMinimumSize(QSize(400, 400))  
        self.setMaximumSize(QSize(400, 400))  
        self.setWindowIcon(QIcon('image\dns.png'))

        
        self.icon_label = QLabel(self)
        self.icon_label.setGeometry(10, 10, 50, 50)
        self.label_interface = QLabel('Select Network Interface:', self)
        self.interface_combobox = QComboBox(self)
        self.interface_combobox.addItems(['Wi-Fi', 'Ethernet'])
        self.label_dns1 = QLabel('DNS 1', self)
        self.dns1_input = QLineEdit(self)
        self.label_dns2 = QLabel('DNS 2', self)
        self.dns2_input = QLineEdit(self)
        self.change_button = QPushButton('Change Network Settings', self)
        self.clear_button = QPushButton('Clear DNS', self)
        self.result_label = QLabel('', self)
        self.log_text = QPlainTextEdit(self)
        self.log_text.setReadOnly(True)  

       
        self.set_icon('image\no-wifi.png')

        
        layout = QVBoxLayout(self)
        layout.addWidget(self.icon_label)
        layout.addWidget(self.label_interface)
        layout.addWidget(self.interface_combobox)
        layout.addWidget(self.label_dns1)
        layout.addWidget(self.dns1_input)
        layout.addWidget(self.label_dns2)
        layout.addWidget(self.dns2_input)
        layout.addWidget(self.change_button)
        layout.addWidget(self.clear_button)
        layout.addWidget(self.result_label)
        layout.addWidget(self.log_text)

        
        self.change_button.clicked.connect(self.change_network_settings)
        self.clear_button.clicked.connect(self.clear_dns_settings)

        
        version_label = QLabel('Version App : 1.1.0', self)
        creator_label = QLabel('Created by: 2xAm1r', self)
        github_label = QLabel(
            '<a href="https://github.com/2xAm1r">GitHub</a>', self)
        github_label.setOpenExternalLinks(True)

        layout.addWidget(version_label)
        layout.addWidget(creator_label)
        layout.addWidget(github_label)

        
        about_button = QPushButton('About', self)
        about_button.clicked.connect(self.show_about_dialog)
        layout.addWidget(about_button)

        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon('image\dns.png'))
        show_action = QAction('Show', self)
        quit_action = QAction('Quit', self)
        show_action.triggered.connect(self.show_window)
        quit_action.triggered.connect(self.close)
        tray_menu = QMenu(self)
        tray_menu.addAction(show_action)
        tray_menu.addSeparator()
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)

        
        self.setWindowFlags(Qt.WindowMinimizeButtonHint |
                            Qt.WindowCloseButtonHint)
        self.tray_icon.activated.connect(self.on_tray_icon_activated)

        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_and_update_connection_status)
        self.timer.start(1000)  

        self.show()

    def set_icon(self, icon_name):
        icon_path = os.path.join('image\dns.png', icon_name)
        pixmap = QPixmap(icon_path)
        self.icon_label.setPixmap(pixmap.scaled(50, 50))  

    def show_window(self):
        self.showNormal()
        self.activateWindow()

    def on_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger or reason == QSystemTrayIcon.DoubleClick:
            self.showNormal()
            self.activateWindow()

    def changeEvent(self, event):
        if event.type() == event.WindowStateChange and self.isMinimized():
            self.hide()
            self.tray_icon.show()

    def check_internet_connection(self):
        try:
            response = requests.get('https://www.google.com', timeout=5)
            return True
        except (requests.ConnectionError, requests.Timeout):
            return False

    def change_network_settings(self):
        
        if not self.check_internet_connection():
            self.result_label.setText('Check your internet connection!')
            return

        selected_interface = self.interface_combobox.currentText()
        dns1 = self.dns1_input.text()
        dns2 = self.dns2_input.text()

      
        if not self.is_valid_dns(dns1) or (dns2 and not self.is_valid_dns(dns2)):
            self.result_label.setText('Invalid DNS address entered.')
            return

        try:
            if selected_interface in ['Wi-Fi', 'Ethernet']:
               
                cmd_set_dns1 = f'netsh interface ipv4 set dns name="{
                    selected_interface}" source=static address={dns1} validate=no'
                subprocess.run(cmd_set_dns1, check=True)

               
                if dns2:
                    cmd_set_dns2 = f'netsh interface ipv4 add dns name="{
                        selected_interface}" address={dns2} index=2 validate=no'
                    subprocess.run(cmd_set_dns2, check=True)

                self.result_label.setText(f'The DNS settings for {
                                          selected_interface} changed to DNS1: {dns1}, DNS2: {dns2}')

                
                self.set_icon('image\wifi.png')
            else:
                raise ValueError('Invalid network interface selected.')
        except subprocess.CalledProcessError as e:
            self.result_label.setText(f'Error: {e}')

            
            self.set_icon('image\no-wifi.png')

     
        self.log_text.appendPlainText(f'The DNS settings for {
                                      selected_interface} changed to DNS1: {dns1}, DNS2: {dns2}')

    def clear_dns_settings(self):
        
        if not self.check_internet_connection():
            self.result_label.setText('Check your internet connection!')
            return

        selected_interface = self.interface_combobox.currentText()

        try:
            if selected_interface in ['Wi-Fi', 'Ethernet']:
              
                cmd_clear_dns = f'netsh interface ipv4 set dns name="{
                    selected_interface}" source=dhcp'
                subprocess.run(cmd_clear_dns, check=True)

                self.result_label.setText(
                    f'DNS settings for {selected_interface} cleared.')

                
                self.set_icon('image\no-wifi.png')
            else:
                raise ValueError('Invalid network interface selected.')
        except subprocess.CalledProcessError as e:
            self.result_label.setText(f'Error: {e}')

         
            self.set_icon('image\wifi.png')

     
        self.log_text.appendPlainText(
            f'DNS settings for {selected_interface} cleared.')

    def show_about_dialog(self):
        about_dialog = AboutDialog()
        about_dialog.exec_()

    def handle_connection_status(self, is_connected):
        if is_connected:
            self.result_label.setText('Connected to the internet')
        else:
            self.result_label.setText('Disconnected from the internet')

    def check_and_update_connection_status(self):
        is_connected = self.check_internet_connection()
        self.handle_connection_status(is_connected)

    def is_valid_dns(self, dns_address):
        try:
            ip_address(dns_address)
            return True
        except ValueError:
            return False


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = NetworkChangerApp()
    sys.exit(app.exec_())
