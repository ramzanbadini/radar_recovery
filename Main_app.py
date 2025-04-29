import sys
import os
from Database import DatabaseManager
from Multimedia import VideoPlayerWidget
from Multimedia import CustomVideoWidget
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import QSize
from PyQt6 import QtWidgets, QtCore, QtGui, QtMultimedia, QtMultimediaWidgets
from PyQt6.QtCore import Qt

VALID_USERNAME = "admin"
VALID_PASSWORD = "1234"

class LoginDialog(QtWidgets.QDialog):
    def __init__(self, radar_type, db_manager, parent=None):
        super().__init__(parent)
        self.radar_type = radar_type
        self.db_manager = db_manager
        self.setWindowTitle("Only Admin Authorized")
        self.setFixedSize(300, 120)

        self.init_ui()
        
    def init_ui(self):
        layout = QtWidgets.QFormLayout(self)

        self.username_input = QtWidgets.QLineEdit()
        self.password_input = QtWidgets.QLineEdit()
        self.password_input.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)

        layout.addRow("Username:", self.username_input)
        layout.addRow("Password:", self.password_input)

        self.login_button = QtWidgets.QPushButton("Login")
        self.login_button.clicked.connect(self.check_credentials)
        layout.addWidget(self.login_button)

        self.setLayout(layout)
        self.access_granted = False

    def check_credentials(self):
        username = "admin"#self.username_input.text()
        password = "1234"#self.password_input.text()
        if username == VALID_USERNAME and password == VALID_PASSWORD:
            self.access_granted = True
            self.accept()
        else:
            QMessageBox.warning(self, "Access Denied", "Invalid username or password")


## uploading data diaglloge
class UploadDialog(QtWidgets.QDialog):
    def __init__(self, radar_type, db_manager, parent=None):
        super().__init__(parent)
        self.radar_type = radar_type
        self.db_manager = db_manager
        self.setWindowTitle("Upload New System")
        self.resize(600, 400)

        self.init_ui()

    def init_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        # System name
        self.system_name_edit = QtWidgets.QLineEdit(self)
        self.system_name_edit.setPlaceholderText("System Name")
        layout.addWidget(self.system_name_edit)

        # Parent system selection
        self.parent_combo = QtWidgets.QComboBox(self)
        self.parent_combo.addItem("None", userData=None)
        
        # Populate with top-level systems of this radar type
        for sys_id, name in self.db_manager.get_top_level_systems(self.radar_type):
            self.parent_combo.addItem(name, userData=sys_id)
        layout.addWidget(QtWidgets.QLabel("Parent System (optional):"))
        layout.addWidget(self.parent_combo)

        # Description
        self.description_edit = QtWidgets.QTextEdit(self)
        self.description_edit.setPlaceholderText("Description/Rectification Steps")
        layout.addWidget(self.description_edit)

        # Upload date
        self.upload_date_edit = QtWidgets.QDateEdit(self)
        self.upload_date_edit.setCalendarPopup(True)
        self.upload_date_edit.setDate(QtCore.QDate.currentDate())
        layout.addWidget(QtWidgets.QLabel("Upload Date:"))
        layout.addWidget(self.upload_date_edit)

        # Uploader name
        self.uploader_name_edit = QtWidgets.QLineEdit(self)
        self.uploader_name_edit.setPlaceholderText("Uploader Name")
        layout.addWidget(self.uploader_name_edit)

        # Video file selection
        file_layout = QtWidgets.QHBoxLayout()
        self.video_path_edit = QtWidgets.QLineEdit(self)
        self.video_path_edit.setPlaceholderText("Select MP4 Video")
        file_layout.addWidget(self.video_path_edit)
        self.browse_btn = QtWidgets.QPushButton("Browse", self)
        self.browse_btn.clicked.connect(self.browse_video)
        file_layout.addWidget(self.browse_btn)
        layout.addLayout(file_layout)

        # Dialog buttons: Submit and Cancel
        btn_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Ok |
                                             QtWidgets.QDialogButtonBox.StandardButton.Cancel)
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

    def browse_video(self):
        file_dialog = QtWidgets.QFileDialog(self)
        file_dialog.setNameFilter("MP4 files (*.mp4)")
        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                self.video_path_edit.setText(selected_files[0])

    def get_upload_data(self):
        parent_id = self.parent_combo.currentData()  # Eacg sub_sys will have a parent ID and for top level that would be none
        return {
            "parent_id": parent_id,
            "system_name": self.system_name_edit.text(),
            "description": self.description_edit.toPlainText(),
            "upload_date": self.upload_date_edit.date().toString(QtCore.Qt.DateFormat.ISODate),
            "uploader_name": self.uploader_name_edit.text(),
            "video_path": self.video_path_edit.text(),
            "radar_type": self.radar_type
        }

class RemoveDialog(QtWidgets.QDialog):
    def __init__(self, radar_type, db_manager, parent=None):
        super().__init__(parent)
        self.radar_type = radar_type
        self.db_manager = db_manager
        self.setWindowTitle("Delete System")
        self.resize(600, 400)

        self.init_ui()

    def init_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
##
        # Delete Section
        layout.addWidget(QtWidgets.QLabel("Delete System/Sub-System"))
        self.combo = QtWidgets.QComboBox()
        self.refresh_combo()
        
        self.delete_button = QtWidgets.QPushButton("Delete Selected")
        self.delete_button.clicked.connect(self.delete_system)

        layout.addWidget(self.combo)
        layout.addWidget(self.delete_button)

        self.setLayout(layout)

    def refresh_combo(self):
        self.combo.clear()
##        cursor = conn.cursor()
##        cursor.execute("SELECT id, system_name, sub_system_name FROM systems")
##        self.entries = cursor.fetchall()

        sys_name = self.db_manager.combo_data(self.radar_type)

        for entry in sys_name:
            self.combo.addItem(f"{entry[1]} -> entry[2]", entry[0])


    def delete_system(self):
        if self.combo.count() == 0:
            QtWidgets.QMessageBox.warning(self, "Error", "No systems to delete.")
            return

        selected_id = self.combo.currentData()
        selected_text = self.combo.currentText()
        print(selected_id)
        print(selected_text)
    
        confirm = QtWidgets.QMessageBox.question(
            self, "Confirm Deletion",
            f"Are you sure you want to delete:\n{selected_text}?",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
        )

        if confirm == QtWidgets.QMessageBox.StandardButton.Yes:
            self.db_manager.delete_system(selected_id)

            QtWidgets.QMessageBox.information(self, "Deleted", "Entry deleted.")
            self.refresh_combo()



### Window for uploading radar type
class RadarAppMainWindow(QtWidgets.QMainWindow):
    def __init__(self, radar_type, db_manager, parent=None):
        super().__init__(parent)
        self.radar_type = radar_type
        self.db_manager = db_manager
        self.setWindowTitle(f"Radar Recovery Application - {radar_type}")
        self.showMaximized()
       # self.setMinimumSize(1000, 700)
        self.init_ui()
        self.setStyleSheet("background-color: #e2f1f6;")  # Light blue background


    def init_ui(self):
        # Create main widget and a horizontal splitter for left (tree) and right (content)
        central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QtWidgets.QHBoxLayout(central_widget)

        self.main_splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal)
        self.main_splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: lightgray;
                width: 1px;
        }
        """)
        main_layout.addWidget(self.main_splitter)

        # Left panel: Search bar and tree view in a vertical layout
        left_panel = QtWidgets.QWidget(self)
        left_layout = QtWidgets.QVBoxLayout(left_panel)
        left_layout.setContentsMargins(5, 0, 5, 0)

        self.search_bar = QtWidgets.QLineEdit(self)
        self.search_bar.setFixedHeight(30)  # Adjust height as needed
        self.search_bar.setPlaceholderText("Search systems...")
        left_layout.addWidget(self.search_bar)

        self.tree = QtWidgets.QTreeWidget(self)
        self.tree.setHeaderHidden(True)
        self.tree.setIndentation(15)  # Default is usually 20
        left_layout.addWidget(self.tree)
        self.main_splitter.addWidget(left_panel)
        self.main_splitter.setStretchFactor(0, 1)  # Approximately 1/3     #### (index, factor size)                self.main_splitter.setSizes([20, 40])  # Left: 200px, Right: 400px


        # Right panel: Vertical splitter for description (top) and video (bottom)
        right_panel = QtWidgets.QWidget(self)
        right_layout = QtWidgets.QVBoxLayout(right_panel)
        right_layout.setContentsMargins(5, 0, 0, 0)
        

        self.content_splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Vertical)
        right_layout.addWidget(self.content_splitter)

        # Right upper panel: Text description (read-only)
        self.text_description = QtWidgets.QTextEdit(self)
        self.text_description.setReadOnly(True)
        self.content_splitter.addWidget(self.text_description)


        add_rem_layout = QtWidgets.QHBoxLayout()

        # Upload Button
        self.Upload_button = QtWidgets.QPushButton("Upload System")
        self.Upload_button.clicked.connect(self.open_upload_dialog)
        add_rem_layout.addWidget(self.Upload_button)

        # Remove Button
        self.remove_button = QtWidgets.QPushButton("Remmove System")
        self.remove_button.clicked.connect(self.request_login)
        add_rem_layout.addWidget(self.remove_button)

        # Log 
        self.remove_button = QtWidgets.QPushButton("Log")
        self.remove_button.clicked.connect(self.open_remove_dialog)
        add_rem_layout.addWidget(self.remove_button)

        

        left_layout.addLayout(add_rem_layout)


        # Right lower panel: Video player widget
        self.video_player = VideoPlayerWidget(self)
        self.content_splitter.addWidget(self.video_player)

        # Ensure both description and video share equal space initially
        self.content_splitter.setStretchFactor(0, 1)    ## the (desc, 1 factor)
        self.content_splitter.setStretchFactor(1, 1)    ## the (vid, 1 factor ) both equial
        self.main_splitter.addWidget(right_panel)
        self.main_splitter.setStretchFactor(1, 3)       ## index 1 ie right panel will get more size

        # Status Bar
        self.status = self.statusBar()
        self.update_status("No system selected", "", "")

        # Menu Bar: Upload and Home actions
        menu = self.menuBar()
        file_menu = menu.addMenu("File")
        upload_action = QtGui.QAction("Upload", self)
        upload_action.triggered.connect(self.open_upload_dialog)
        file_menu.addAction(upload_action)

        remove_action = QtGui.QAction("Remove", self)
        remove_action.triggered.connect(self.open_remove_dialog)
        file_menu.addAction(remove_action)

        home_action = QtGui.QAction("Home", self)
        home_action.triggered.connect(self.go_home)
        file_menu.addAction(home_action)

        # Connect tree view selection and search bar
        self.tree.itemClicked.connect(self.tree_item_clicked)
        self.search_bar.textChanged.connect(self.filter_tree)

        # Populate tree from database
        self.populate_tree()



    def populate_tree(self):
        self.tree.clear()
        # Get top-level systems for this radar type
        top_systems = self.db_manager.get_top_level_systems(self.radar_type)
##        print(top_systems)
        for sys_id, name in top_systems:
            parent_item = QtWidgets.QTreeWidgetItem([name])
            parent_item.setData(0, QtCore.Qt.ItemDataRole.UserRole, sys_id)
        # Always add a dummy child to force the drop-down arrow
            dummy_child = QtWidgets.QTreeWidgetItem([""])
            parent_item.addChild(dummy_child)

            # Add real subsystems (if any), and remove dummy if real ones are found
            if self.add_subsystems(parent_item, sys_id):
                parent_item.removeChild(dummy_child)
            
            #self.add_subsystems(parent_item, sys_id)
            self.tree.addTopLevelItem(parent_item)
        self.tree.expandAll()

    def add_subsystems(self, parent_item, parent_id):
        subsystems = self.db_manager.get_subsystems(parent_id)
        if not subsystems:
            return False  # No subsystems added

        for sub_id, name in subsystems:
            child_item = QtWidgets.QTreeWidgetItem([f"- {name}"])
            child_item.setData(0, QtCore.Qt.ItemDataRole.UserRole, sub_id)
            parent_item.addChild(child_item)
            # Recursively add deeper levels if any
            self.add_subsystems(child_item, sub_id)
        return True

    def tree_item_clicked(self, item, column):
        system_id = item.data(0, QtCore.Qt.ItemDataRole.UserRole)
        details = self.db_manager.get_system_details(system_id)
        if details:
            # Unpack details (columns: id, parent_id, system_name, description, upload_date, uploader_name, video_path, radar_type)
            _, _, system_name, description, upload_date, uploader_name, video_path, _ = details
            self.text_description.setPlainText(description)
            self.update_status(system_name, upload_date, uploader_name)
            self.video_player.load_video(video_path)

##    def filter_tree(self, text):
##        # Simple filtering: iterate over top-level items and hide those that don't match.
##        root = self.tree.invisibleRootItem()
##        child_count = root.childCount()
##        for i in range(child_count):
##            item = root.child(i)
##            match = text.lower() in item.text(0).lower()
##            item.setHidden(not match)
##            # Could be enhanced to search recursively over all children.

    def filter_tree(self, text):
        def search_item(item, text):
            match = text.lower() in item.text(0).lower()
            child_match = False

            # Recursively search children
            for i in range(item.childCount()):
                child = item.child(i)
                child_visible = search_item(child, text)
                child.setHidden(not child_visible)
                if child_visible:
                    child_match = True

            # Show item if it matches or any of its children match
            item.setHidden(not (match or child_match))
            return match or child_match

        root = self.tree.invisibleRootItem()
        for i in range(root.childCount()):
            top_item = root.child(i)
            search_item(top_item, text)


    def update_status(self, system_name, upload_date, uploader):
        status_message = f"System: {system_name} | Date Added: {upload_date} | Added by: {uploader}"
        self.status.showMessage(status_message)

    ###  authentication for deletion
    def request_login(self):
        login_dialog = LoginDialog(self.radar_type, self.db_manager, self)
        if login_dialog.exec():
            if login_dialog.access_granted:
                print("done")
                try:
                    self.open_remove_dialog()
                except NameError as e:
                    print(f"An error occurred: {e}")

    def open_upload_dialog(self):
        dialog = UploadDialog(self.radar_type, self.db_manager, self)
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            data = dialog.get_upload_data()
            # Insert new system record into the database
            self.db_manager.insert_system(data["parent_id"], data["system_name"],
                                          data["description"], data["upload_date"],
                                          data["uploader_name"], data["video_path"],
                                          data["radar_type"])
            QtWidgets.QMessageBox.information(self, "Upload", "New system uploaded successfully!")
            # Refresh tree view to reflect new data
            self.populate_tree()

    def open_remove_dialog(self):
        dialog = RemoveDialog(self.radar_type, self.db_manager, self)
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            pass
##            data = dialog.get_upload_data()
##            # Insert new system record into the database
##            self.db_manager.insert_system(data["parent_id"], data["system_name"],
##                                          data["description"], data["upload_date"],
##                                          data["uploader_name"], data["video_path"],
##                                          data["radar_type"])
##            QtWidgets.QMessageBox.information(self, "Upload", "New system uploaded successfully!")
##            # Refresh tree view to reflect new data
##            self.populate_tree()

    def go_home(self):
        self.close()
        self.parent().show_main_menu()


class MainMenuWindow(QtWidgets.QMainWindow):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.setWindowTitle("Radar Recovery Software - Main Menu")
        self.setStyleSheet("background-color: #B4f96D;")  # Light blue background

        #self.setMinimumSize(700, 500)
        self.init_ui()
        self.showMaximized()

    def init_ui(self):
        central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(central_widget)

      
        layout = QtWidgets.QVBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)  # adjust as needed
      #  layout.setSpacing(20)                      # space between left and right


        Upper_layout =QtWidgets.QHBoxLayout()
        Upper_layout.setSpacing(250)       # space between buttons

        ### Wessec Monogram
##        monogram_label_1 = QtWidgets.QLabel()
##        pixmap1 = QPixmap(r"C:\Users\PMYLS\Documents\radar_recovery\487_mono.png")        
##        monogram_label_1.setPixmap(pixmap1)                 
##        monogram_label_1.setScaledContents(True)           # scale 
##        monogram_label_1.setFixedSize(200-50, 250-50)            # display dimensions
##        monogram_label_1.setAlignment(Qt.AlignmentFlag.AlignLeft)  # 
##        Upper_layout.insertWidget(0, monogram_label_1) 

        gif_label = QtWidgets.QLabel()
        gif_label.setScaledContents(True)           # scale 
        gif_label.setFixedSize(200-50, 200-50)            # display dimensions
        gif_label.setAlignment(Qt.AlignmentFlag.AlignRight)  # 
        movie = QtGui.QMovie(r"C:\Users\PMYLS\Documents\radar_recovery\Photos\rad_gify.gif")  
        gif_label.setMovie(movie)
        movie.start()  # Start the animation
        Upper_layout.insertWidget(0,gif_label) 

        
        ### 487 Monogram
        monogram_label_3 = QtWidgets.QLabel()
        pixmap3 = QPixmap(r"C:\Users\PMYLS\Documents\radar_recovery\Photos\lable_487.png")        
        monogram_label_3.setPixmap(pixmap3)                 
        monogram_label_3.setScaledContents(True)           # scale pixmap to label’s size 
        monogram_label_3.setFixedSize(400, 100)            # display dimensions
        monogram_label_3.setAlignment(Qt.AlignmentFlag.AlignCenter)  
        Upper_layout.insertWidget(0, monogram_label_3) 


        #Upper_layout.addWidget(Upper_lable)
        ### 487 Monogram
        monogram_label_2 = QtWidgets.QLabel()
        pixmap2 = QPixmap(r"C:\Users\PMYLS\Documents\radar_recovery\Photos\487_mono.png")        
        monogram_label_2.setPixmap(pixmap2)                 
        monogram_label_2.setScaledContents(True)           # scale pixmap to label’s size 
        monogram_label_2.setFixedSize(200-50, 250-50)            # display dimensions
        monogram_label_2.setAlignment(Qt.AlignmentFlag.AlignRight)  
        Upper_layout.insertWidget(0, monogram_label_2) 

        # container widget for buttons
        button_container = QtWidgets.QWidget()
        button_container.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Fixed,     # Do not expand horizontally
            QtWidgets.QSizePolicy.Policy.Preferred   # Allow vertical adjustment
        )
        button_container.setMaximumWidth(450)  # Optional cap on width
 
        button_layout = QtWidgets.QHBoxLayout(button_container)  

        button_layout.setSpacing(40)       # space between buttons
        button_layout.setContentsMargins(0, 0, 0, 0)   # no extra padding


##middle layout
        middle_layout = QtWidgets.QVBoxLayout()

        # Header information with larger fonts
        header_label = QtWidgets.QLabel("Idea Conceived by: XXX")
        author_label = QtWidgets.QLabel("Developed by:  Flt Lt M. Ramzan Badini")
        conceived_label = QtWidgets.QLabel("Advisor:  xxxx")
        for label in (header_label, author_label, conceived_label):
            label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet("font-size: 18px; font-weight: bold;")
            middle_layout.addWidget(label)


        # Radar system font making
        self.radar1_btn = QtWidgets.QPushButton("Radar Systems", self)
        self.radar1_btn.setMinimumSize(200, 80)
        self.radar1_btn.setStyleSheet("""
            QPushButton {
                background-color: #007ACC;
                color: black;
                font-size: 22px;
                font-weight: bold;
                border: none;
                border-radius: 16px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #003f7f;
            }
            """)

        self.radar1_btn.clicked.connect(lambda: self.open_radar_app("Radar 1"))


        self.radar2_btn = QtWidgets.QPushButton("Comm Systems", self)
        self.radar2_btn.setMinimumSize(200, 80)
        self.radar2_btn.setStyleSheet("""
            QPushButton {
                background-color: #28A745;
                color: black;
                font-size: 22px;
                font-weight: bold;
                border: none;
                border-radius: 16px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #157a2c;
            }
            QPushButton:pressed {
                background-color: #0f6523;
            }
            """)

        self.radar2_btn.clicked.connect(lambda: self.open_radar_app("COMM"))

        button_layout.addWidget(self.radar2_btn)
        button_layout.addWidget(self.radar1_btn)
        button_layout.setAlignment(Qt.AlignmentFlag.AlignTop)  # keeps them at the top of their column

        layout.addLayout(Upper_layout)

        
        layout.addLayout(middle_layout)
        layout.addStretch()           # pushes the button column all the way right

        layout.addWidget(button_container)
        layout.setAlignment(button_container, Qt.AlignmentFlag.AlignHCenter)   

        layout.addLayout(button_layout)


    def open_radar_app(self, radar_type):
        self.radar_window = RadarAppMainWindow(radar_type, self.db_manager, parent=self)
        self.radar_window.show()
        self.hide()

    def show_main_menu(self):
        self.show()


# ---------------------------
# Main Application Execution
# ---------------------------
def main():
    app = QtWidgets.QApplication(sys.argv)
    # Set a global stylesheet for a larger, cleaner font
    app.setStyleSheet("QWidget { font-size: 13px; }")

    db_manager = DatabaseManager()
    main_menu = MainMenuWindow(db_manager)
    main_menu.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
