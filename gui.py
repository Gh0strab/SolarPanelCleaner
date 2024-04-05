import customtkinter
from PIL import Image
import controller
import threading
#import tensorflow_panel_state_detection as PSD
import tflite_panel_state_detection as PSD

customtkinter.set_appearance_mode("dark")

class App(customtkinter.CTk):
    width = 800
    height = 480

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title("CustomTkinter Solar Panel Cleaner.py")
        self.geometry(f"{self.width}x{self.height}")
        self.resizable(True,True)

        # Creates background image
        self.bg_image = customtkinter.CTkImage(Image.open(r"OPTION5.png"), size=(self.width, self.height))
        self.bg_image_label = customtkinter.CTkLabel(self, text="", image=self.bg_image)
        self.bg_image_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Creates bar at the top
        self.top_bar = customtkinter.CTkFrame(self, bg_color="gray", corner_radius=0)
        self.top_bar.place(relx=0, rely=0, relwidth=1, relheight=0.10)

        # Add text "INNORAIDERS" to the top left corner
        self.innoraider_label = customtkinter.CTkLabel(self.top_bar, text="INNORAIDERS", font=customtkinter.CTkFont(size=35, weight="bold"))
        self.innoraider_label.place(relx=0.30, rely=0.1, anchor="ne")

        # Adds option menu to top right corner
        self.optionmenu = customtkinter.CTkOptionMenu(self.top_bar, values=["MANUAL", "TIMER", "AUTO AI"], width=200, height=40,font=customtkinter.CTkFont(size=17, weight="bold"),fg_color="gray",button_color="gray",dropdown_font=customtkinter.CTkFont(size=20, weight="bold"),button_hover_color="black")
        self.optionmenu.place(relx=0.98, rely=0.5, anchor="e")

        # Create textbox
        self.textbox = customtkinter.CTkTextbox(self, width=175, height=200, border_color="#9D0FFF", border_width=5, corner_radius=15,font=customtkinter.CTkFont(size=12, weight="bold"))
        self.textbox.place(relx=0.01, rely=0.13)
        self.textbox.insert(1.0, "::::DEBUG WINDOW::::\n")

        # Create main frame
        self.slider_progressbar_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.slider_progressbar_frame.place(relx=0.5, rely=0.63, anchor="center", relwidth=1)

        # Create progress bar
        self.progressbar_1 = customtkinter.CTkProgressBar(self.slider_progressbar_frame, progress_color="#9D0FFF")
        self.progressbar_1.pack(fill="x", padx=5, pady=5)
        self.progressbar_1.configure(mode="indeterminate", indeterminate_speed=.75 , height=25)

        # Create start button
        self.start_button = customtkinter.CTkButton(self, text="START", font=customtkinter.CTkFont(size=65, weight="bold"), fg_color=("#9D0FFF"), width=320, height=100, corner_radius=0, command=self.start_task)  # Removed parentheses
        self.start_button.place(relx=0.25, rely=0.8, anchor="center")

        # Create stop button
        self.stop_button = customtkinter.CTkButton(self, text="STOP", font=customtkinter.CTkFont(size=65, weight="bold"), fg_color=("#EF6F8F"), width=320, height=100, corner_radius=0, command=self.stop_task)  # Removed parentheses
        self.stop_button.place(relx=0.75, rely=0.8, anchor="center")

        # Initial Conditions
        self.task_running = False
        self.controller_instance = controller.cleaner_logic(self)
        PSD.run_camera(self)


    def start_task(self):
        if self.task_running:
            self.debug_window("Task already running.\n")
            return

        self.task_running = True
        self.start_button.configure(state="disabled")
        self.progressbar_1.configure(progress_color="#EF6F8F")
        self.progressbar_1.start()

        if self.optionmenu.get() == "MANUAL":
            threading.Thread(target=self.controller_instance.perform_task).start()
            self.debug_window("Manual Task Started.\n")
        elif self.optionmenu.get() == "AUTO AI":
            if PSD.capture_and_classify():
                threading.Thread(target=self.controller_instance.perform_task).start()
                self.debug_window("Dirty Panel Detected.")
                self.debug_window("AUTO-AI Task Started")
            else:
                self.debug_window("Clean Panel Detected.")
                self.stop_task()
        else:
            self.debug_window("Timer Task Started.\n")

    def stop_task(self):
        if not self.task_running:
            self.debug_window("No task running.\n")
            return

        self.task_running = False
        self.start_button.configure(state="normal")
        self.progressbar_1.configure(progress_color="#9D0FFF")
        self.progressbar_1.stop()
        self.controller_instance.stop_task()

        self.debug_window("Process Complete.\n")

    def debug_window(self, text):
        self.textbox.insert("end", text + "\n")
        self.textbox.see("end")

if __name__ == "__main__":
    app = App()
    app.mainloop()
