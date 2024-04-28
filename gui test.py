import tkinter as tk
import customtkinter
from PIL import Image, ImageTk
import tflite_panel_state_detection as PSD
import threading

customtkinter.set_appearance_mode("dark")

class App(customtkinter.CTk):
    width = 800
    height = 480

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title("CustomTkinter Solar Panel Cleaner.py")
        self.geometry(f"{self.width}x{self.height}")
        self.resizable(True,True)

        self.main_window()
        self.task_running = False

    def main_window(self):
        # Create background image label
        self.bg_image = customtkinter.CTkImage(Image.open(r"Background 8.png"), size=(self.width, self.height))
        self.bg_image_label = customtkinter.CTkLabel(self, text="", image=self.bg_image)
        self.bg_image_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Create gray bar at the top
        self.top_bar = customtkinter.CTkFrame(self, bg_color="gray", corner_radius=0)
        self.top_bar.place(relx=0, rely=0, relwidth=1, relheight=0.10)

        # Add text "INNORAIDERS" to the top right corner
        self.innoraider_label = customtkinter.CTkLabel(self.top_bar, text="INNORAIDERS", font=customtkinter.CTkFont(size=35, weight="bold"))
        self.innoraider_label.place(relx=0.30, rely=0.08, anchor="ne")

        # Creates option menu
        self.optionmenu = customtkinter.CTkOptionMenu(self.top_bar, values=["MANUAL", "TIMER", "AUTO AI"], width=200, height=40,font=customtkinter.CTkFont(size=17, weight="bold"),fg_color="#4a4a49",button_color="#4a4a49",dropdown_font=customtkinter.CTkFont(size=15, weight="bold"),button_hover_color="black")
        self.optionmenu.place(relx=0.93, rely=0.5, anchor="e")

        # Create settings button
        self.settings_button = customtkinter.CTkButton(self.top_bar, text="", image=customtkinter.CTkImage(Image.open(
            r"images/settings.png")), font=customtkinter.CTkFont(size=20, weight="bold"), fg_color=("#141314"), hover_color="#4a4a49", width=35, height=38, corner_radius=10, command=self.open_settings)
        self.settings_button.place(relx=0.99, rely=0.5, anchor="e")

        # Create textbox
        self.textbox = customtkinter.CTkTextbox(self, width=175, height=200, border_color="#9D0FFF", border_width=5, corner_radius=10,font=customtkinter.CTkFont(size=12, weight="bold"))
        self.textbox.place(relx=0.01, rely=0.13)
        self.textbox.insert(1.0, "::::::::DEBUG WINDOW::::::::\n")

        # Create main frame
        self.slider_progressbar_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.slider_progressbar_frame.place(relx=0.5, rely=0.63, anchor="center", relwidth=1)

        # Create progress bar
        self.progressbar_1 = customtkinter.CTkProgressBar(self.slider_progressbar_frame, progress_color="#9D0FFF")
        self.progressbar_1.pack(fill="x", padx=5, pady=5)
        self.progressbar_1.configure(mode="indeterminate", indeterminate_speed=.75 , height=25)

        # Create start button
        self.start_button = customtkinter.CTkButton(self, text="START", font=customtkinter.CTkFont(size=65, weight="bold"), fg_color=("#9D0FFF"), hover_color="#4a4a49", width=320, height=100, corner_radius=0, command=self.start_task)
        self.start_button.place(relx=0.25, rely=0.82, anchor="center")

        # Create stop button
        self.stop_button = customtkinter.CTkButton(self, text="STOP", font=customtkinter.CTkFont(size=65, weight="bold"), fg_color=("#EF6F8F"), hover_color="#4a4a49", width=320, height=100, corner_radius=0, command=self.stop_task)
        self.stop_button.place(relx=0.75, rely=0.82, anchor="center")

        PSD.run_camera(self)

    def start_task(self):
        self.task_running = True
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.progressbar_1.configure(progress_color="#EF6F8F")
        self.progressbar_1.start()
        self.debug_window("Process Started\n")

        if self.optionmenu.get() == "MANUAL":
            self.debug_window("Manual Task Started.\n")
        elif self.optionmenu.get() == "AUTO AI":
            if PSD.capture_and_classify():
                self.debug_window("PANEL IS DIRTY AHHHHHHHHHH")
            else:
                self.debug_window("PANEL IS CLEAN MORON")
        else:
            self.debug_window("Timer Task Started.\n")

    def stop_task(self):
        self.task_running = False
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        self.progressbar_1.configure(progress_color="#9735F8")
        self.progressbar_1.stop()
        self.debug_window("Process Completed\n")

    def debug_window(self, text):
        self.textbox.insert("end", text + "\n")
        self.textbox.see("end")

    def open_settings(self):
        for widget in (self.optionmenu, self.textbox, self.slider_progressbar_frame, self.start_button, self.stop_button,self.settings_button):
            widget.place_forget()

        # Create a new frame for settings
        self.settings_frame = customtkinter.CTkFrame(self, bg_color="gray")
        self.settings_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.top_bar = customtkinter.CTkFrame(self.settings_frame, bg_color="gray", corner_radius=0)
        self.top_bar.place(relx=0, rely=0, relwidth=1, relheight=0.10)
        self.innoraider_label = customtkinter.CTkLabel(self.top_bar, text="INNORAIDERS", font=customtkinter.CTkFont(size=35, weight="bold"))
        self.innoraider_label.place(relx=0.30, rely=0.08, anchor="ne")
        self.home_button = customtkinter.CTkButton(self.top_bar, text="", image=customtkinter.CTkImage(Image.open(
            r"/images\home-button-white-icon.webp")), width=35, height=38, fg_color=("#141314"), hover_color="#4a4a49", corner_radius=10, command=self.close_settings)
        self.home_button.place(relx=0.99, rely=0.5, anchor="e")

        cycles_frame = customtkinter.CTkFrame(self.settings_frame, border_width=5, border_color="white", width=self.width/3-10, height=self.height/2)
        cycles_frame.place(relx=0.17,rely=0.5,anchor="center")
        # Add widgets to the settings frame (for example, a label and a button)
        cycles_label = customtkinter.CTkLabel(cycles_frame, text="Number of Cycles", font=customtkinter.CTkFont(size=20, weight="bold"))
        cycles_label.place(relx=0.5, rely=0.15, anchor="center")

        cycles_input = customtkinter.CTkEntry(cycles_frame)
        cycles_input.place(relx=0.5, rely=0.5, anchor="center")

        home_system_button = customtkinter.CTkButton(self.settings_frame,text="PRESS\n TO MOVE TO SYSTEM HOME",font=customtkinter.CTkFont(size=20, weight="bold"), border_width=5, border_color="white", width=self.width/3, height=self.height/2, fg_color="black")
        home_system_button.place(relx=0.5,rely=0.5,anchor="center")

        misc_settings_frame = customtkinter.CTkFrame(self.settings_frame, border_width=5, border_color="white", width=self.width/3-10, height=self.height/2)
        misc_settings_frame.place(relx=0.83,rely=0.5,anchor="center")
        misc_settings_label = customtkinter.CTkLabel(misc_settings_frame, text="Misc Settings", font=customtkinter.CTkFont(size=20, weight="bold"))
        misc_settings_label.place(relx=0.5, rely=0.15, anchor="center")

        wizard_onoff = customtkinter.CTkSwitch(misc_settings_frame, text="Wizard", switch_height=25,switch_width=45)
        wizard_onoff.place(relx=0.1, rely=0.25, anchor="w")


        def save():
            print("saved to file")

        save_settings = customtkinter.CTkButton(self.settings_frame, text="SAVE", command=save())
        save_settings.place(relx=0.5, rely=0.95, anchor="center")

    def close_settings(self):
        # Remove the settings frame
        self.settings_frame.place_forget()

        # Restore the original placements of widgets
        self.main_window()


if __name__ == "__main__":
    app = App()
    app.mainloop()
