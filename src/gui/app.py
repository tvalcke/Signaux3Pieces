"""Interface principale de l'application de reconnaissance de pièces - fichier partiellement réalisé avec claude ( car ce n'est pas le sujet du cours + gagner du temps)"""

from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, ttk

import cv2
from PIL import Image, ImageOps
from PIL import ImageTk

from src.acquisition.image_loader import load_image
from src.config import (
    DEFAULT_CURRENCY,
    get_currency_choices,
    get_currency_directory,
    get_currency_label,
    is_path_allowed_for_currency,
    is_supported_image_extension,
)
from src.detection.detection import detect_circles, detect_edges
from src.preprocessing.preprocessing import gaussian_blur, to_grayscale
from src.utils.visualization import draw_circles

GAUSSIAN_KERNEL_SIZE = 7
CANNY_THRESHOLD1 = 40
CANNY_THRESHOLD2 = 120


class CoinRecognitionApp(tk.Tk):
    """Fenêtre principale de l'application de reconnaissance de pièces."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Signaux III - Reconnaissance de pièces")
        self.geometry("1000x700")
        self.minsize(850, 600)

        self.current_currency = DEFAULT_CURRENCY
        self.current_image_path: Path | None = None
        self.current_image: Image.Image | None = None
        self.preview_photo: ImageTk.PhotoImage | None = None
        self.original_preview_photo: ImageTk.PhotoImage | None = None
        self.gray_preview_photo: ImageTk.PhotoImage | None = None

        self.currency_var = tk.StringVar(value=self.current_currency)
        self.file_name_var = tk.StringVar(value="Aucun fichier sélectionné")
        self.image_info_var = tk.StringVar(value="Dimensions : --")
        self.currency_info_var = tk.StringVar(
            value=f"Devise active : {get_currency_label(self.current_currency)} ({self.current_currency})"
        )
        self.status_var = tk.StringVar(value="Prêt.")

        self._build_ui()
        self._reset_results()
        self._refresh_status("Prêt.")
        self._update_currency_display()

    def _build_ui(self) -> None:
        """Construit l'interface principale de l'application."""
        self.main_frame = ttk.Frame(self, padding=12)
        self.main_frame.pack(fill="both", expand=True)

        self.title_label = ttk.Label(
            self.main_frame,
            text="Signaux III - Reconnaissance de pièces",
            font=("Segoe UI", 18, "bold"),
        )
        self.title_label.pack(anchor="w", pady=(0, 12))

        controls_frame = ttk.Frame(self.main_frame)
        controls_frame.pack(fill="x", pady=(0, 12))

        currency_frame = ttk.Frame(controls_frame)
        currency_frame.pack(side="left", padx=(0, 20))

        ttk.Label(currency_frame, text="Devise", font=("Segoe UI", 10, "bold")).pack(anchor="w")

        currency_values = get_currency_choices()
        self.currency_combobox = ttk.Combobox(
            currency_frame,
            values=currency_values,
            state="readonly",
            width=22,
        )
        self.currency_combobox.set("Euro (EUR)")
        self.currency_combobox.pack(anchor="w", pady=(4, 0))
        self.currency_combobox.bind("<<ComboboxSelected>>", self._on_currency_change)

        select_button_frame = ttk.Frame(controls_frame)
        select_button_frame.pack(side="left")
        self.select_image_button = ttk.Button(
            select_button_frame,
            text="Choisir une image",
            command=self._choose_image,
        )
        self.select_image_button.pack(side="left")

        self.analyse_button = ttk.Button(
            self.main_frame,
            text="Analyser l'image",
            command=self.run_analysis,
            state="disabled",
        )
        self.analyse_button.pack(anchor="w", pady=(0, 12))

        self.preview_header = ttk.Frame(self.main_frame)
        self.preview_header.pack(fill="x")

        ttk.Label(self.preview_header, textvariable=self.currency_info_var, font=("Segoe UI", 10, "bold")).pack(
            side="left"
        )
        ttk.Label(self.preview_header, textvariable=self.file_name_var).pack(side="left", padx=(20, 0))
        ttk.Label(self.preview_header, textvariable=self.image_info_var).pack(side="left", padx=(20, 0))

        self.preview_panel = ttk.Frame(self.main_frame, padding=10, relief="sunken", borderwidth=1)
        self.preview_panel.pack(fill="both", expand=True)
        self.preview_panel.configure(height=360)
        self.preview_panel.pack_propagate(False)

        self.preview_container = ttk.Frame(self.preview_panel)
        self.preview_container.pack(fill="both", expand=True)

        self.preview_left = ttk.Label(self.preview_container, text="Image originale", anchor="center")
        self.preview_right = ttk.Label(
            self.preview_container,
            text="Pièces détectées — Hough",
            anchor="center",
        )

        self.preview_left.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=(0, 8))
        self.preview_right.grid(row=0, column=1, sticky="nsew", padx=(8, 0), pady=(0, 8))
        self.preview_container.grid_columnconfigure(0, weight=1)
        self.preview_container.grid_columnconfigure(1, weight=1)
        self.preview_container.grid_rowconfigure(0, weight=1)

        self.preview_panel.bind("<Configure>", self._refresh_preview)

        result_frame = ttk.LabelFrame(self.main_frame, text="Résultats de l'analyse", padding=10)
        result_frame.pack(fill="x", pady=(12, 0))

        self.result_text = tk.Text(result_frame, height=7, wrap="word", state="disabled")
        self.result_text.pack(fill="both", expand=True)

        self.status_bar = ttk.Label(
            self,
            textvariable=self.status_var,
            relief="sunken",
            anchor="w",
            padding=(8, 4),
        )
        self.status_bar.pack(fill="x", side="bottom")

    def _on_currency_change(self, _event: tk.Event | None = None) -> None:
        """Met à jour la devise active lorsque l'utilisateur change le menu."""
        selected = self.currency_combobox.get()
        currency_code = self._currency_code_from_label(selected)
        self.current_currency = currency_code
        self._clear_loaded_image()
        self._reset_results()
        self._update_currency_display()
        self._refresh_status(f"Devise sélectionnée : {get_currency_label(currency_code)} ({currency_code})")

    def _currency_code_from_label(self, label: str) -> str:
        """Convertit le libellé du menu en code de devise."""
        choices = {choice: code for code, choice in zip(["EUR", "TWD"], get_currency_choices())}
        return choices.get(label, DEFAULT_CURRENCY)

    def _update_currency_display(self) -> None:
        """Met à jour les informations sur la devise actuelle."""
        currency_label = get_currency_label(self.current_currency)
        self.currency_info_var.set(f"Devise active : {currency_label} ({self.current_currency})")
        self.currency_var.set(self.current_currency)

    def _clear_loaded_image(self) -> None:
        """Supprime les informations de l'image courante."""
        self.current_image_path = None
        self.current_image = None
        self.preview_photo = None
        self.original_preview_photo = None
        self.gray_preview_photo = None
        self.file_name_var.set("Aucun fichier sélectionné")
        self.image_info_var.set("Dimensions : --")
        self.preview_left.configure(text="Image originale", image="")
        self.preview_right.configure(
            text="Pièces détectées — Hough",
            image="",
        )
        self.analyse_button.configure(state="disabled")

    def _reset_results(self) -> None:
        """Remet la zone de résultats dans un état neutre."""
        self.result_text.configure(state="normal")
        self.result_text.delete("1.0", "end")
        self.result_text.insert("end", "Aucune analyse lancée.\n")
        self.result_text.configure(state="disabled")

    def _refresh_status(self, message: str) -> None:
        """Met à jour la barre de statut."""
        self.status_var.set(message)

    def _choose_image(self) -> None:
        """Ouvre le sélecteur de fichiers en forçant le dossier de la devise active."""
        currency_directory = get_currency_directory(self.current_currency)
        currency_directory.mkdir(parents=True, exist_ok=True)

        file_path = filedialog.askopenfilename(
            title=f"Sélectionner une image ({self.current_currency})",
            initialdir=str(currency_directory),
            filetypes=[
                ("Images", "*.png *.jpg *.jpeg *.bmp *.tif *.tiff"),
                ("PNG", "*.png"),
                ("JPG", "*.jpg *.jpeg"),
                ("BMP", "*.bmp"),
                ("TIFF", "*.tif *.tiff"),
            ],
            parent=self,
        )

        if not file_path:
            self._refresh_status("Sélection annulée.")
            return

        selected_path = Path(file_path).resolve()

        if not is_supported_image_extension(selected_path):
            self._refresh_status("Erreur : format d'image non pris en charge.")
            self._show_result("Format d'image non pris en charge. Les extensions autorisées sont PNG, JPG, JPEG, BMP, TIFF.")
            return

        if not is_path_allowed_for_currency(selected_path, self.current_currency):
            self._refresh_status("Erreur : le fichier sélectionné n'appartient pas au dossier de la devise active.")
            self._show_result("Le fichier sélectionné est hors du dossier autorisé pour la devise active.")
            return

        try:
            with Image.open(selected_path) as opened_image:
                opened_image.load()
                self.current_image = opened_image.copy()
        except Exception as exc:  # pragma: no cover - dépend de l'image sélectionnée
            self._refresh_status("Erreur : image corrompue ou illisible.")
            self._show_result(f"Impossible d'ouvrir l'image : {exc}")
            return

        self.current_image_path = selected_path
        self.file_name_var.set(selected_path.name)
        self.image_info_var.set(
            f"Dimensions : {self.current_image.width} x {self.current_image.height} pixels"
        )
        self._refresh_status(f"Image chargée : {selected_path.name}")
        self._refresh_preview()
        self.analyse_button.configure(state="normal")

    def _refresh_preview(self, _event: tk.Event | None = None) -> None:
        """Affiche l'image chargée dans le panneau de prévisualisation."""
        if self.current_image is None:
            self.preview_left.configure(text="Image originale", image="")
            self.preview_right.configure(
                text="Pièces détectées — Hough",
                image="",
            )
            return

        preview_width = max(200, int((self.preview_panel.winfo_width() - 60) / 2))
        preview_height = max(180, self.preview_panel.winfo_height() - 30)

        resized_image = ImageOps.contain(self.current_image, (preview_width, preview_height))
        self.preview_photo = ImageTk.PhotoImage(resized_image)
        self.preview_left.configure(image=self.preview_photo, text="")
        self.preview_right.configure(
            text="Pièces détectées — Hough",
            image="",
        )

    def run_analysis(self) -> None:
        """Charge l'image, filtre, détecte les cercles et les affiche dans l'interface."""
        if self.current_image_path is None:
            self._refresh_status("Erreur : aucune image n'a été chargée.")
            self._show_result("Aucune image sélectionnée pour l'analyse.")
            return

        try:
            original_array = load_image(self.current_image_path)
            gray_array = to_grayscale(original_array)
            blurred_array = gaussian_blur(gray_array, kernel_size=GAUSSIAN_KERNEL_SIZE)
            circles = detect_circles(blurred_array)
            annotated_array = draw_circles(original_array, circles)
        except (FileNotFoundError, ValueError, TypeError, IsADirectoryError) as exc:
            self._refresh_status("Erreur lors de la détection des cercles.")
            self._show_result(f"Impossible de traiter l'image : {exc}")
            return

        rgb_original = cv2.cvtColor(original_array, cv2.COLOR_BGR2RGB)
        rgb_annotated = cv2.cvtColor(annotated_array, cv2.COLOR_BGR2RGB)

        original_pil = Image.fromarray(rgb_original)
        annotated_pil = Image.fromarray(rgb_annotated)

        preview_width = max(200, int((self.preview_panel.winfo_width() - 80) / 2))
        preview_height = max(180, self.preview_panel.winfo_height() - 60)

        original_resized = ImageOps.contain(original_pil, (preview_width, preview_height))
        annotated_resized = ImageOps.contain(annotated_pil, (preview_width, preview_height))

        self.original_preview_photo = ImageTk.PhotoImage(original_resized)
        self.gray_preview_photo = ImageTk.PhotoImage(annotated_resized)

        self.preview_left.configure(image=self.original_preview_photo, text="")
        self.preview_right.configure(
            image=self.gray_preview_photo,
            text="Pièces détectées — Hough",
        )

        self._refresh_status(f"Détection terminée : {len(circles)} cercle(s) détecté(s)")

        if not circles:
            self._show_result("Aucun cercle détecté.")
            return

        details = [f"Nombre de cercles détectés : {len(circles)}"]
        for index, (x, y, radius) in enumerate(circles, start=1):
            details.append(f"Cercle {index} : centre=({x}, {y}), rayon={radius} px")

        self._show_result("\n".join(details))

    def _show_result(self, message: str) -> None:
        """Met à jour la zone de résultats avec un message lisible."""
        self.result_text.configure(state="normal")
        self.result_text.delete("1.0", "end")
        self.result_text.insert("end", message)
        self.result_text.configure(state="disabled")


def build_app() -> CoinRecognitionApp:
    """Crée une instance de l'application Tkinter."""
    return CoinRecognitionApp()
