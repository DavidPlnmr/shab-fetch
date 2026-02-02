from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QRadioButton, QLabel, QPushButton, QDateEdit, QWidget, QFileDialog, QCheckBox, QGridLayout
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtGui import QPixmap, QIcon
import sys
import os
from shab_request_api import SHABRequestAPI
import pandas as pd


class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        # Configuration de la fenêtre principale
        self.setWindowTitle(
            "Récupération des inscriptions au registre du commerce")
        self.setGeometry(100, 100, 400, 300)

        # Création d'un widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Création d'un layout principal vertical
        main_layout = QVBoxLayout()

        # Ajout d'un label
        label = QLabel("Sélectionnez une option et une date", self)
        main_layout.addWidget(label)

        # Création des Radio Buttons dans un layout horizontal
        radio_layout = QHBoxLayout()
        self.rdb_new_entries = QRadioButton("Nouvelles entrées uniquement")
        self.rdb_new_entries.setChecked(True)  # Sélectionner par défaut
        self.rdb_all = QRadioButton("Tout")

        radio_layout.addWidget(self.rdb_new_entries)
        radio_layout.addWidget(self.rdb_all)
        main_layout.addLayout(radio_layout)

        # Ajout de la sélection des cantons
        cantons_label = QLabel("Sélectionnez les cantons:", self)
        main_layout.addWidget(cantons_label)

        # Liste des cantons suisses
        self.cantons_list = [
            "AG", "AI", "AR", "BE", "BL", "BS", "FR", "GE", "GL", "GR",
            "JU", "LU", "NE", "NW", "OW", "SG", "SH", "SO", "SZ", "TG",
            "TI", "UR", "VD", "VS", "ZG", "ZH"
        ]

        # Création d'un layout en grille pour les checkboxes
        cantons_grid = QGridLayout()
        self.canton_checkboxes = {}
        
        # Créer les checkboxes en grille (5 colonnes)
        for idx, canton in enumerate(self.cantons_list):
            # Créer un widget conteneur pour chaque canton (logo + checkbox)
            canton_widget = QWidget()
            canton_layout = QHBoxLayout()
            canton_layout.setContentsMargins(0, 0, 0, 0)
            canton_layout.setSpacing(5)
            
            # Ajouter le logo
            logo_label = QLabel()
            logo_path = os.path.join("canton_logos", f"{canton}.png")
            if os.path.exists(logo_path):
                pixmap = QPixmap(logo_path)
                # Redimensionner le logo à 20x20 pixels
                pixmap = pixmap.scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                logo_label.setPixmap(pixmap)
            else:
                # Si le logo n'existe pas, afficher un espace vide
                logo_label.setFixedSize(20, 20)
            
            canton_layout.addWidget(logo_label)
            
            # Ajouter le checkbox
            checkbox = QCheckBox(canton, self)
            if canton == "GE":  # GE sélectionné par défaut
                checkbox.setChecked(True)
            self.canton_checkboxes[canton] = checkbox
            canton_layout.addWidget(checkbox)
            
            canton_widget.setLayout(canton_layout)
            
            row = idx // 5
            col = idx % 5
            cantons_grid.addWidget(canton_widget, row, col)
        
        main_layout.addLayout(cantons_grid)

        # Ajout d'un sélecteur de date de début (DatePicker)
        start_date_label = QLabel("Date de début:", self)
        main_layout.addWidget(start_date_label)

        self.start_date_picker = QDateEdit(self)
        # Initialise avec la date actuelle
        self.start_date_picker.setDate(QDate.currentDate().addDays(-7))
        # Permet d'afficher le calendrier
        self.start_date_picker.setCalendarPopup(True)
        main_layout.addWidget(self.start_date_picker)

        # Ajout d'un sélecteur de date de fin (DatePicker)
        end_date_label = QLabel("Date de fin:", self)
        main_layout.addWidget(end_date_label)

        self.end_date_picker = QDateEdit(self)
        # Initialise avec la date actuelle
        self.end_date_picker.setDate(QDate.currentDate())
        # Permet d'afficher le calendrier
        self.end_date_picker.setCalendarPopup(True)
        main_layout.addWidget(self.end_date_picker)

        # Création d'un bouton d'action
        self.button = QPushButton(
            "Récupérer les inscriptions au registre du commerce", self)
        self.button.clicked.connect(self.on_button_click)
        main_layout.addWidget(self.button)

        # Ajout d'un label pour afficher les résultats
        self.error_label = QLabel("", self)
        # Color red
        self.error_label.setStyleSheet("color: red")
        main_layout.addWidget(self.error_label)
        self.label = QLabel("", self)
        main_layout.addWidget(self.label)

        # Attribuer le layout principal au widget central
        central_widget.setLayout(main_layout)

    # Fonction exécutée au clic sur le bouton
    def on_button_click(self):
        self.clear_error_labels()

        new_entries = True
        if self.rdb_new_entries.isChecked():
            new_entries = True
        else:
            new_entries = False

        selected_date_start = self.start_date_picker.date().toString("yyyy-MM-dd")
        selected_date_end = self.end_date_picker.date().toString("yyyy-MM-dd")

        # Vérifier que end date est supérieure à start date
        if self.start_date_picker.date() > self.end_date_picker.date():
            self.error_label.setText(
                "La date de fin doit être supérieure à la date de début")
            return

        # Vérifier que la date de début n'est pas supérieure à aujourd'hui
        if self.start_date_picker.date() > QDate.currentDate() or self.end_date_picker.date() > QDate.currentDate():
            self.error_label.setText(
                "Les dates ne peuvent pas être supérieure à la date actuelle")
            return

        # Récupérer les cantons sélectionnés
        selected_cantons = [canton for canton, checkbox in self.canton_checkboxes.items() if checkbox.isChecked()]
        
        # Vérifier qu'au moins un canton est sélectionné
        if not selected_cantons:
            self.error_label.setText(
                "Veuillez sélectionner au moins un canton")
            return

        shab = SHABRequestAPI()

        data = None
        if new_entries:
            data = shab.get_new_entries(
                publication_date_end=selected_date_end, publication_date_start=selected_date_start, size=1000, list_cantons=selected_cantons)
        else:
            data = shab.get_publications(
                publication_date_end=selected_date_end, publication_date_start=selected_date_start, size=1000, list_cantons=selected_cantons)

        df = shab.publications_data_to_df(data)

        self.open_save_file_dialog(df)
    # Fonction pour clear le ou les labels d'erreur

    def clear_error_labels(self):
        self.error_label.setText("")

    def open_save_file_dialog(self, df):
        # Ouvrir le dialogue "Enregistrer sous"
        default_file_name = QDate.currentDate().toString("yyyy-MM-dd") + ".csv"
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Enregistrer le fichier", default_file_name, "CSV (*.csv)")
        
        

        # Vérifier si un chemin de fichier a été sélectionné
        if file_path:
            self.label.setText(f"Fichier enregistré : {file_path}")
            # Simulation de l'enregistrement du fichier
            df.to_csv(file_path, index=False, sep=';')
        else:
            self.label.setText("Aucun fichier enregistré")


# Création de l'application Qt
app = QApplication(sys.argv)

# Création de la fenêtre
window = Window()
window.show()

# Exécution de l'application
sys.exit(app.exec_())
