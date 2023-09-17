import etcpak
import texture2ddecoder
import sys
import tkinter
from io import StringIO
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
from PIL import Image
from PIL import UnidentifiedImageError
from webbrowser import open as webOpen
import json

# Constants
PROFILE_WIDTH_DEFAULT = 1440
PROFILE_HEIGHT_DEFAULT = 832
ICON_WIDTH_DEFAULT = 352
ICON_HEIGHT_DEFAULT = 352
BLOCK_SIZE_PROFILE = 0x97E00
BLOCK_SIZE_ICON = 0xF200
GITHUB_SOURCE = "https://github.com/PizzaTimeJoshua/SV-Image-Injector"


class SVInjector:
    def __init__(self):
        self.root = tkinter.Tk()
        self.root.title("SV Image Injector")
        self.root.geometry("505x200")
        self.root.resizable(width=False, height=False)

        # Captures Console Messages
        self.console_output = StringIO()
        sys.stdout = self.console_output
        self.create_debug_text()

        # Load settings file if it exists, otherwise create one with defaults
        try:
            with open('settings.json', 'r') as file:
                settings = json.load(file)
                self.profile_width = settings["profileWidth"]
                self.profile_height = settings["profileHeight"]
                self.icon_width = settings["iconWidth"]
                self.icon_height = settings["iconHeight"]
        except FileNotFoundError:
            print("No Settings File Found. Using Default sizes.")
            self.profile_width = PROFILE_WIDTH_DEFAULT
            self.profile_height = PROFILE_HEIGHT_DEFAULT
            self.icon_width = ICON_WIDTH_DEFAULT
            self.icon_height = ICON_HEIGHT_DEFAULT

            # Create Settings File
            with open('settings.json', 'w') as file:
                settings = {
                    "profileWidth": PROFILE_WIDTH_DEFAULT,
                    "profileHeight": PROFILE_HEIGHT_DEFAULT,
                    "iconWidth": ICON_WIDTH_DEFAULT,
                    "iconHeight": ICON_HEIGHT_DEFAULT
                }
                json.dump(settings, file)

        # Initialize variables
        self.block_size = BLOCK_SIZE_PROFILE
        self.file_path = None
        self.current_width = self.profile_width
        self.current_height =self.profile_height

        # Widgets
        self.create_widgets()

        # Menus
        self.create_menubar()

        # Update Console
        self.update_console_display()

        # Main loop
        self.root.mainloop()
        sys.stdout = sys.__stdout__
        print(self.console_output.getvalue())

    def create_debug_text(self):
        """Creates a Text widget to display console messages"""
        self.debug_text = tkinter.Text(master=self.root, width=60, height=4, wrap="char")
        self.debug_text.grid(column=0, row=3, padx=(10, 10), pady=(10, 10), columnspan=4)
        self.debug_text.insert(tkinter.END, "Console Messages:\n")
        self.debug_text.config(state=tkinter.DISABLED)

        scrollbar = ttk.Scrollbar(master=self.root,orient='vertical',command=self.debug_text.yview)
        self.debug_text['yscrollcommand'] = scrollbar.set
        scrollbar.grid(column=3,row=3,ipady=15,sticky='e')

    def create_widgets(self):
        """Creates all the necessary widgets"""
        self.create_file_selector()
        self.create_converter_buttons()

    def create_file_selector(self):
        """Creates the file selector button and label"""
        self.file_select_btn = tkinter.Button(master=self.root, text="Select File",
                                              width=10, height=1, command=self.select_file)
        self.file_select_btn.grid(column=0, row=0, padx=(10, 10), pady=(10, 10))

        self.file_display = tkinter.Text(master=self.root, width=30, height=3, wrap="word")
        self.file_display.grid(column=0, row=1, padx=(10, 10), pady=(10, 10), columnspan=2, rowspan=2)
        self.file_display.insert(tkinter.END, "Selected File:\nNone")
        self.file_display.config(state=tkinter.DISABLED)

    def create_converter_buttons(self):
        """Creates the Convert and Save button"""
        self.convert_btn = tkinter.Button(master=self.root, text="Convert and Save",
                                          width=15, height=1, command=self.convert_and_save)
        self.convert_btn.grid(column=1, row=0, padx=(10, 10), pady=(10, 10))

        radio_sep = ttk.Separator(self.root, orient="horizontal")
        radio_sep.grid(column=2, row=1, ipadx=100, columnspan=2)

        self.create_file_type_radios()
        self.create_picture_type_radios()

    def create_file_type_radios(self):
        """Creates the file type radios"""
        self.file_type_var = tkinter.StringVar(self.root, "BIN to Image")
        self.file_type_selector = tkinter.Radiobutton(self.root, text="BIN to Image", variable=self.file_type_var, value="BIN to Image")
        self.file_type_selector2 = tkinter.Radiobutton(self.root, text="Image to BIN", variable=self.file_type_var, value="Image to BIN")
        self.file_type_selector.grid(column=2, row=0, padx=(10, 0), pady=(0, 10))
        self.file_type_selector2.grid(column=3, row=0, padx=(0, 10), pady=(0, 10))

    def create_picture_type_radios(self):
        """Creates the picture type radios"""
        self.picture_type_var = tkinter.StringVar(self.root, "Profile Picture")
        self.picture_type_selector = tkinter.Radiobutton(self.root, text="Profile Picture", variable=self.picture_type_var, value="Profile Picture", command=self.update_dimensions)
        self.picture_type_selector2 = tkinter.Radiobutton(self.root, text="Icon Picture", variable=self.picture_type_var, value="Icon Picture", command=self.update_dimensions)
        self.picture_type_selector.grid(column=2, row=2, padx=(10, 0), pady=(0, 10))
        self.picture_type_selector2.grid(column=3, row=2, padx=(0, 10), pady=(0, 10))

    def create_menubar(self):
        """Creates the menubar"""
        menu_bar = tkinter.Menu(self.root)

        file_menu = tkinter.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Select File", command=self.select_file)
        file_menu.add_command(label="Convert and Save", command=self.convert_and_save)
        file_menu.add_command(label="Configure", command=self.open_config)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        help_menu = tkinter.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="Documentation", command=lambda: webOpen(GITHUB_SOURCE))
        help_menu.add_command(label="About...", command=self.show_about)

        menu_bar.add_cascade(label="File", menu=file_menu)
        menu_bar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=menu_bar)

    def show_about(self):
        """Shows a message box with project details"""
        messagebox.showinfo("About Project", "Scarlet and Violet Image Injector\nLast Updated: September 16th, 2023\n\nThis Project allows you to extract and inject custom images for a player's profile and icon.")

    def select_file(self):
        """Prompts user to choose a file and updates the display"""
        self.file_path = filedialog.askopenfilename(filetypes=[("Binary and Image Files", "*.bin; *.png; *.jpg; *.jpeg"), ("All Files", "*.*")])
        if not self.file_path:
            print("File selection cancelled")
            return
        short_path = self.file_path.split('/')[-1]
        self.file_display.config(state=tkinter.NORMAL)
        self.file_display.delete(1.0, tkinter.END)
        self.file_display.insert(tkinter.END, f"Selected File:\n{short_path}\n")
        self.file_display.config(state=tkinter.DISABLED)

        # If an image is selected, auto Radio Button to 'Image to BIN'
        imageExts = [".png",".jpg",".jpeg"]
        if any(word in short_path for word in imageExts):
            self.file_type_var.set("Image to BIN")
            self.file_type_selector2.configure(state=tkinter.ACTIVE)
            print("Image File detected. Auto Selecting 'Image to BIN'")
        
        # If an binary file is selected, auto Radio Button to 'BIN to Image'
        binExts = [".bin",".tex",".dxt1"]
        if any(word in short_path for word in binExts):
            self.file_type_var.set("BIN to Image")
            self.file_type_selector2.configure(state=tkinter.ACTIVE)
            print("Binary File detected. Auto Selecting 'BIN to Image'")


    def update_dimensions(self):
        """Updates the dimensions based on the selected picture type"""
        if self.picture_type_var.get() == "Profile Picture":
            self.current_width = self.profile_width
            self.current_height = self.profile_height
            self.block_size = BLOCK_SIZE_PROFILE
        elif self.picture_type_var.get() == "Icon Picture":
            self.current_width = self.icon_width
            self.current_height = self.icon_height
            self.block_size = BLOCK_SIZE_ICON

    def convert_and_save(self):
        """Converts between BIN and Image formats"""
        if not self.file_path:
            print("No File Selected")
            return

        try:
            if self.file_type_var.get() == "BIN to Image":
                with open(self.file_path, "rb") as file:
                    compressed_data = file.read()
                if len(compressed_data) != self.block_size:
                    print(f"Warning: File size is {len(compressed_data)} bytes.\nExpected size is {self.block_size} bytes")
                    return
                decompressed_data = self.decompress_dxt1(compressed_data)
                output_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Image", ".png"), ("All Files", "*.*")], initialfile="output.png")
                if not output_path:
                    print("File Selection Cancelled")
                    return
                self.save_image(decompressed_data, output_path)
                print("Image Successfully Exported")
            else:
                image = Image.open(self.file_path).convert("RGBA")
                compressed_data = self.compress_image_to_dxt1(image)
                if not compressed_data:
                    return
                output_path = filedialog.asksaveasfilename(defaultextension=".bin", filetypes=[("Binary Image", ".bin"), ("All Files", "*.*")], initialfile="output.bin")
                if not output_path:
                    print("File Selection Cancelled")
                    return
                self.save_binary_data(compressed_data, output_path)
                print("Image Successfully Compressed")
        except FileNotFoundError:
            print("Error: Could not find file.")
        except UnidentifiedImageError:
            print("Error: Image File Invalid")

    def compress_image_to_dxt1(self, image):
        """Compresses an image to DTX1 format"""
        if (image.width, image.height) != (self.current_width, self.current_height):
            print(f"Size not correct. Expected width: {self.current_width}, height: {self.current_height}.\nObtained {image.width}, {image.height}.")
            return False
        raw = image.tobytes()
        compressed_data = etcpak.compress_to_dxt1(raw, image.width, image.height)
        padding = b'\x00' * (self.block_size - len(compressed_data))
        return compressed_data + padding

    def decompress_dxt1(self, compressed_data):
        """Decompresses DTX1 data to an image"""
        if len(compressed_data) != self.block_size:
            raise ValueError("Invalid Binary File")
        image_data = texture2ddecoder.decode_bc1(compressed_data, self.current_width, self.current_height)
        image = Image.frombytes("RGBA", (self.current_width, self.current_height), image_data, "raw", "BGRA")
        return image

    def save_image(self, image, output_path):
        """Saves an image to disk"""
        image.save(output_path)

    def save_binary_data(self, data, output_path):
        """Writes binary data to disk"""
        with open(output_path, "wb") as file:
            file.write(data)

    def update_console_display(self):
        """Displays recent console messages"""
        console_info = self.console_output.getvalue().strip("\n").split("\n")
        messages = "\n".join(console_info[:])
        
        if (self.debug_text.get(0.0,tkinter.END) != f"Console Messages:\n{messages}\n"):
            self.debug_text.config(state=tkinter.NORMAL)
            self.debug_text.delete(0.0, tkinter.END)
            self.debug_text.insert(tkinter.END, f"Console Messages:\n{messages}")
            self.debug_text.config(state=tkinter.DISABLED)
            self.debug_text.see('end')
        self.root.after(200, self.update_console_display)

    def open_config(self):
        """Opens a window to configure the dimensions"""
        config_window = tkinter.Toplevel(self.root)
        config_window.title("Configure")
        config_window.geometry("340x200")
        config_window.transient(self.root)
        config_window.grab_set()

        config_window.resizable(width=False, height=False)

        global profile_width_entry, profile_height_entry, icon_width_entry, icon_height_entry

        profile_width_lbl = tkinter.Label(config_window, text="*UInt32 KPictureProfileCurrentWidth (0xFEAA87DA) :")
        profile_width_lbl.grid(column=0, row=0, padx=(10, 0), pady=10)

        separator1 = ttk.Separator(config_window, orient="horizontal")
        separator1.grid(column=0, row=1, ipadx=160, columnspan=2)

        profile_height_lbl = tkinter.Label(config_window, text="*UInt32 KPictureProfileCurrentHeight (0x5361CEB5) :")
        profile_height_lbl.grid(column=0, row=2, padx=(10, 0), pady=10)

        separator2 = ttk.Separator(config_window, orient="horizontal")
        separator2.grid(column=0, row=3, ipadx=160, columnspan=2)

        icon_width_lbl = tkinter.Label(config_window, text="*UInt32 KPictureIconCurrentWidth (0x8FAB2C4D) :")
        icon_width_lbl.grid(column=0, row=4, padx=(10, 0), pady=10)

        separator3 = ttk.Separator(config_window, orient="horizontal")
        separator3.grid(column=0, row=5, ipadx=160, columnspan=2)

        icon_height_lbl = tkinter.Label(config_window, text="*UInt32 KPictureIconCurrentHeight (0x0B384C24) :")
        icon_height_lbl.grid(column=0, row=6, padx=(10, 0), pady=10)

        separator4 = ttk.Separator(config_window, orient="horizontal")
        separator4.grid(column=0, row=7, ipadx=160, columnspan=2)

        profile_width_entry = tkinter.Entry(config_window, width=5, justify="center")
        profile_width_entry.grid(column=1, row=0, padx=(0, 10), pady=10)
        profile_width_entry.insert(tkinter.INSERT, str(self.profile_width))

        profile_height_entry = tkinter.Entry(config_window, width=5, justify="center")
        profile_height_entry.grid(column=1, row=2, padx=(0, 10), pady=10)
        profile_height_entry.insert(tkinter.INSERT, str(self.profile_height))

        icon_width_entry = tkinter.Entry(config_window, width=5, justify="center")
        icon_width_entry.grid(column=1, row=4, padx=(0, 10), pady=10)
        icon_width_entry.insert(tkinter.INSERT, str(self.icon_width))

        icon_height_entry = tkinter.Entry(config_window, width=5, justify="center")
        icon_height_entry.grid(column=1, row=6, padx=(0, 10), pady=10)
        icon_height_entry.insert(tkinter.INSERT, str(self.icon_height))

        save_btn = tkinter.Button(config_window, width=5, text="Save", command=lambda:self.save_config(config_window))
        save_btn.grid(column=1, row=7)

        reset_btn = tkinter.Button(config_window, width=5, text="Default", command=self.reset_config)
        reset_btn.grid(column=0, row=7)
        

    def save_config(self,window):
        """Saves the new dimensions to the settings file"""
        try:
            self.profile_width = int(profile_width_entry.get())
            self.profile_height = int(profile_height_entry.get())
            self.icon_width = int(icon_width_entry.get())
            self.icon_height = int(icon_height_entry.get())

            with open('settings.json', 'w') as file:
                settings = {
                    "profileWidth": self.profile_width,
                    "profileHeight": self.profile_height,
                    "iconWidth": self.icon_width,
                    "iconHeight": self.icon_height
                }
                json.dump(settings, file)
            self.update_dimensions()
            window.destroy()    


        except ValueError:
            messagebox.showerror("Error: ValueError", message="All values must be integers.")
            return

    def reset_config(self):
        """Resets the dimensions to their default values"""
        profile_width_entry.delete(0, tkinter.END)
        profile_width_entry.insert(tkinter.INSERT, str(PROFILE_WIDTH_DEFAULT))
        profile_height_entry.delete(0, tkinter.END)
        profile_height_entry.insert(tkinter.INSERT, str(PROFILE_HEIGHT_DEFAULT))
        icon_width_entry.delete(0, tkinter.END)
        icon_width_entry.insert(tkinter.INSERT, str(ICON_WIDTH_DEFAULT))
        icon_height_entry.delete(0, tkinter.END)
        icon_height_entry.insert(tkinter.INSERT, str(ICON_HEIGHT_DEFAULT))

        with open('settings.json', 'w') as file:
            settings = {
                "profileWidth": PROFILE_WIDTH_DEFAULT,
                "profileHeight": PROFILE_HEIGHT_DEFAULT,
                "iconWidth": ICON_WIDTH_DEFAULT,
                "iconHeight": ICON_HEIGHT_DEFAULT
            }
            json.dump(settings, file)
        self.update_dimensions()

if __name__ == "__main__":
    app = SVInjector()
