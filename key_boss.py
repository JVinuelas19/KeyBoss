import customtkinter as ctk
import random
import hashlib
import os, sys
import webbrowser
import hardware_times as hw
from pygame import mixer as pymixer
from tkinter import messagebox, Menu
from PIL import Image
from screeninfo import get_monitors

"""KeyBoss main features:
    1 - Generates a password based on your criteria:
    Pick generation options and length. Then press GENERATE.
    A new password appears, its md5 hash and a time will display.
    This time is based on the picked brute-force hardware section
    Check time charts pressing the 'Show Hardware Chart' button.

    2 - Tests your passwords:
    You can measure how secure are your passwords.
    Type your password into the 'Insert yours' section
    Press 'TEST' button and it will show you the time to break it.
    This time is based on the picked brute-force hardware section"
    To learn more press 'How can you know this?' button."""

#Screen width and height
for m in get_monitors():
    if m.is_primary:
        RAW_WIDTH = m.width
        RAW_HEIGHT = m.height


#Constants
NUMBERS = list("0123456789")
LOWERCASE = list("abcdefghijklmnopqrstuvwxyz")
UPPERCASE = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
SYMBOLS = list("^*%$!&@#")
MIN_LENGTH_VALUE, MAX_LENGTH_VALUE = 4, 18
HW_VALUES=["RTX 2080", "RTX 3090", "RTX 4090", "8x A100 Amazon AWS", "ChatGPT HW (10000x A100)", "Leaked Passwords"]
TIME_DATA_SOURCE = "https://www.hivesystems.io/blog/are-your-passwords-in-the-green"
APP_WIDTH, APP_HEIGHT, APP_PADX, APP_PADY = int(RAW_WIDTH/3), int(RAW_HEIGHT/2), int(RAW_WIDTH/3), int(RAW_HEIGHT/4)
LOW_PAD_WIDTH, MID_PAD_WIDTH, HIGH_PAD_WIDTH, HIGHER_PAD_WIDTH = int(APP_WIDTH/50), int(APP_WIDTH/20), int(APP_WIDTH/5), int(APP_WIDTH/2)
LOWER_PAD_HEIGHT, LOW_PAD_HEIGHT, MID_PAD_HEIGHT, HIGH_PAD_HEIGHT = int(APP_HEIGHT/100), int(APP_HEIGHT/80), int(APP_HEIGHT/50), int(APP_HEIGHT/10)


#Widget related functions
def get_slider_length(slider):
    return int(slider.get())


def update_length(e, slider, text):
    pw_length = int(slider.get())
    slider.set(pw_length)
    text.configure(text=f"Password length: {pw_length}")


def change_checkbox(check_var, checkbox):
    if(check_var.get() == "on"):
        check_var.set("on")
        checkbox.configure(variable=check_var)
    else:
        check_var.set("off")
        checkbox.configure(variable=check_var)


def gen_options(have_number, have_lowercase, have_uppercase, have_symbols):
    pool = list()
    if have_number == "on":
        pool.append(NUMBERS)
    if have_lowercase == "on":
        pool.append(LOWERCASE)
    if have_uppercase == "on":
        pool.append(UPPERCASE)
    if have_symbols == "on":
        pool.append(SYMBOLS)
    return pool


def reset_textboxes(right_panel, is_ready):
    for widget in right_panel.winfo_children():
        if is_ready:
            if isinstance(widget, ctk.CTkTextbox):
                widget.configure(state="normal")
                widget.delete("1.0", "end")
        else:
            if isinstance(widget, ctk.CTkTextbox) and (widget.custom_name=="md5_text" or widget.custom_name=="time_text"):
                widget.configure(state="disabled")
                widget.delete("1.0", "end")


#Time chart related functions
def show_chart(hardware_options):
    #Crea nueva ventana 
    hardware = hardware_options.get()
    new_frame = ctk.CTkToplevel()
    new_frame.title(f"{hardware} Time Chart")
    new_frame.geometry(f'{APP_WIDTH}x{APP_HEIGHT}+{APP_PADX}+{APP_PADY}')
    #Obtiene el hardware
    #Obtiene la imagen en funcion del hardware
    app_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    image_path = os.path.join(app_path, "images", f"{hardware}.PNG")
    image = Image.open(image_path).resize((APP_WIDTH, APP_HEIGHT))
    ctk_image = ctk.CTkImage(light_image=image, dark_image=image, size=image.size)
    label = ctk.CTkLabel(master = new_frame, image = ctk_image, text="")
    label.pack()
    new_frame.mainloop()


def is_chartable(pw, has_numbers, has_uppers, has_lowers, has_symbols):
    if len(pw)>3 and len(pw)<19:
        for number in NUMBERS:
            if number in pw:
                has_numbers = True
                break
        for letter in UPPERCASE:
            if letter in pw:
                has_uppers = True
                break
        for letter in LOWERCASE:
            if letter in pw:
                has_lowers = True
                break
        for letter in SYMBOLS:
            if letter in pw:
                has_symbols = True
                break
        return has_numbers, has_uppers, has_lowers, has_symbols
    else:
        return False, False, False, False 
       

def get_time_of_yours(pw, chart):
    hw_chart = hw.get_chart(chart.get())
    try:
        has_numbers, has_uppers, has_lowers, has_symbols = False, False, False, False
        has_numbers, has_uppers, has_lowers, has_symbols = is_chartable(pw, has_numbers, has_uppers, has_lowers, has_symbols)
        if has_numbers and has_lowers and has_uppers and has_symbols:
            return hw_chart[len(pw)-4][4]
        elif has_numbers and has_lowers and has_uppers and not has_symbols:
            return hw_chart[len(pw)-4][3]
        elif not has_numbers and has_lowers and has_uppers and not has_symbols:
            return hw_chart[len(pw)-4][2]
        elif not has_numbers and has_lowers and not has_uppers and not has_symbols:
            return hw_chart[len(pw)-4][1]
        elif has_numbers and not has_lowers and not has_uppers and not has_symbols:
            return hw_chart[len(pw)-4][0]
        else:
            return "The password does not fit chart criteria"
    except:
        raise ValueError("An error happened while calculating brute-force time")


def get_time(chart, length, checkvars):
    hw_chart = hw.get_chart(chart.get())
    if checkvars[0].get() == "on" and checkvars[1].get() == "off" and checkvars[2].get() == "off" and checkvars[3].get() == "off":
        return hw_chart[length-4][0]
    elif checkvars[0].get() == "off" and checkvars[1].get() == "on" and checkvars[2].get() == "off" and checkvars[3].get() == "off":
        return hw_chart[length-4][1]
    elif checkvars[0].get() == "off" and checkvars[1].get() == "on" and checkvars[2].get() == "on" and checkvars[3].get() == "off":
        return hw_chart[length-4][2]
    elif checkvars[0].get() == "on" and checkvars[1].get() == "on" and checkvars[2].get() == "on" and checkvars[3].get() == "off":
        return hw_chart[length-4][3]
    elif checkvars[0].get() == "on" and checkvars[1].get() == "on" and checkvars[2].get() == "on" and checkvars[3].get() == "on":
        return hw_chart[length-4][4]
    else:
        return "The options chosen does not appear in the time chart"
    

#Password related functions
def gen_password(e, slider, checkvars, chart, right_panel):
    #Create pools and get length
    reset_textboxes(right_panel, True)
    pools = gen_options(checkvars[0].get(), checkvars[1].get(), checkvars[2].get(), checkvars[3].get())
    length = get_slider_length(slider)
    #Create the password
    tmp_password = list()
    try:
        #Avoid repeating pools somehow
        for i in range(length):
            if i<len(pools):
                pool_index = i
            else:
                pool_index = random.randint(0, len(pools)-1)
            char_pool = pools[pool_index]
            char_num = random.randint(0, len(char_pool)-1)
            selected = str(char_pool[char_num])
            tmp_password.append(selected)
        password = "".join(tmp_password)
        md5_hash = hashlib.md5(bytearray(password, encoding="utf-8")).hexdigest()
        #Creates password in the textbox
        for widget in right_panel.winfo_children():
            if isinstance(widget, ctk.CTkTextbox) and widget.custom_name == "pw_text":
                widget.insert("1.0", f"{password}")
            elif isinstance(widget, ctk.CTkTextbox) and widget.custom_name == "md5_text":
                widget.insert("1.0", f"{md5_hash}")
            elif isinstance(widget, ctk.CTkTextbox) and widget.custom_name == "time_text":
                try:
                    widget.insert("1.0", get_time(chart, length, checkvars))
                except:
                    raise ValueError("The options chosen to generate the password does not fit the chart.")
        reset_textboxes(right_panel, False)
        return password
    except:
        messagebox.showerror(title="Generation error", message="There are no options marked. Select at least one of the options")
        raise ValueError("No password generation options marked. Please mark at least one.")
            

def test_password(r_panel, chart): 
    for widget in r_panel.winfo_children():
            if isinstance(widget, ctk.CTkTextbox) and widget.custom_name == "pw_text":
                pw_textbox = widget
            elif isinstance(widget, ctk.CTkTextbox) and widget.custom_name == "md5_text":
                md5_textbox = widget
            elif isinstance(widget, ctk.CTkTextbox) and widget.custom_name == "time_text":
                time_textbox = widget
    md5_textbox.configure(state="normal")
    time_textbox.configure(state="normal")
    md5_textbox.delete("1.0", "end")
    time_textbox.delete("1.0", "end")
    password = pw_textbox.get("1.0", "end").replace("\n", "")
    hash = hashlib.md5(bytearray(password, encoding="utf-8")).hexdigest()
    md5_textbox.insert("1.0", f"{hash}")
    #Check if the password is available for time chart
    time_textbox.insert("1.0", get_time_of_yours(password, chart))
    md5_textbox.configure(state="disabled")
    time_textbox.configure(state="disabled")


def show_tutorial():
    messagebox.showinfo(title="Tutorial", 
                        message="KeyBoss main features:\n\n"
                                "1 - Generates a password based on your criteria:\n\n"
                                "Pick generation options and length. Then press GENERATE.\n"
                                "A new password appears, its md5 hash and a time will displa.\n"
                                "This time is based on the picked brute-force hardware section\n"
                                "Check time charts pressing the 'Show Hardware Chart' button.\n\n"
                                "2 - Tests your passwords:\n\n"
                                "You can measure how secure are your passwords.\n"
                                "Type your password into the 'Insert yours' section. \n"
                                "Press 'TEST' button and it will show you the time to break it.\n"
                                "This time is based on the picked brute-force hardware section\n\n"
                                "To learn more press 'How can you know this?' button.")
    

def generic_function():
    pymixer.init()
    pymixer.music.load("sounds/sea_shanty.mp3")
    pymixer.music.play(loops=0)
    messagebox.showinfo(title="Well...", 
                        message="Looks like you have found the easter egg. \n\n"
                                "I'm going to tell you a secret. I tried to code  \n"
                                "a MD5 hash generator from scratch in order to use\n"
                                "it for this application.\n\n"
                                "Spoiler: It did not work, and sadly i can not use\n"
                                "it because it is useless. However this is my own \n"
                                "redemption for the absurd amount of hours spent.\n"
                                "This was me coding the MD5 hash script for 20 hours\n"
                                "\n\nEnjoy!")
    pymixer.music.stop()
    webbrowser.open("https://www.youtube.com/watch?v=szcQjan875A")


#Window related functions
def change_theme(theme):
    ctk.set_appearance_mode(theme)


def create_main_window():
    root = ctk.CTk()
    ctk.set_default_color_theme("blue")
    ctk.set_appearance_mode("dark")
    root.title("KeyBoss")
    root.geometry(f'{APP_WIDTH}x{APP_HEIGHT}+{APP_PADX}+{APP_PADY}')
    return root


def create_menu(main_frame):
    menu = Menu(main_frame)
    #Config menu
    config_menu = Menu(menu, tearoff=False)
    appearance_menu = Menu(config_menu, tearoff=False)
    config_menu.add_cascade(label="Change app theme", menu=appearance_menu)
    appearance_menu.add_command(label="Day", command=lambda theme="light": change_theme(theme))
    appearance_menu.add_command(label="Night", command=lambda theme="dark": change_theme(theme))
    #Help menu
    help_menu = Menu(menu, tearoff=False)
    help_menu.add_command(label="Tutorial", command=show_tutorial)    
    #About menu
    about_menu = Menu(menu, tearoff=False)
    about_menu.add_command(label="Hello there, you curious human being")
    about_menu.add_command(label="It's Juan (JVinuelas19). I am a Junior Python developer!")
    about_menu.add_command(label="Check my socials and contact me if you wish to:")
    about_menu.add_command(label="GitHub 💻", command=lambda:webbrowser.open("https://github.com/JVinuelas19"))
    about_menu.add_command(label="Twitter 🐦", command=lambda:webbrowser.open("https://twitter.com/JVinuelas19"))
    about_menu.add_command(label="Instagram 📷", command=lambda:webbrowser.open("https://www.instagram.com/jvinuelas19/"))
    about_menu.add_command(label="Thank you for using KeyBoss!", command=generic_function)
    #Main menus
    menu.add_cascade(menu=config_menu, label="Configuration")
    menu.add_cascade(menu=help_menu, label="Help")
    menu.add_cascade(menu=about_menu, label="Who did this?")
    root.config(menu=menu)


def create_main_frame(root):
    main_frame = ctk.CTkFrame(root, width=APP_WIDTH, height=APP_HEIGHT)
    main_frame.rowconfigure(12, weight=1)
    main_frame.columnconfigure(1, weight=1)
    main_frame.pack(fill=ctk.BOTH, expand=True)
    return main_frame


def create_left_panel(main_frame, right_panel):
    #Left panel stuff
    options_text = ctk.CTkLabel(main_frame, width=LOW_PAD_WIDTH, height=LOW_PAD_HEIGHT, text="Select your generation options:")
    options_text.grid(column=0, row=0, padx=MID_PAD_WIDTH, pady=MID_PAD_HEIGHT, sticky="w")
    #Button1 
    check_var1, check_var2, check_var3, check_var4 = ctk.StringVar(value="on"), ctk.StringVar(value="on"), ctk.StringVar(value="on"), ctk.StringVar(value="on")
    checkvars = [check_var1, check_var2, check_var3, check_var4]
    checkbox1 = ctk.CTkCheckBox(main_frame, width=LOW_PAD_WIDTH, height=LOW_PAD_HEIGHT, text="Include numbers", variable=check_var1, onvalue="on", offvalue="off", 
                                command= lambda: change_checkbox(check_var=check_var1, checkbox = checkbox1))
    checkbox1.grid(column=0, row=1, padx=MID_PAD_WIDTH, pady=LOW_PAD_HEIGHT, sticky="w")
    #Button2 
    checkbox2 = ctk.CTkCheckBox(main_frame, width=LOW_PAD_WIDTH, height=LOW_PAD_HEIGHT, text="Include lowcase letters", variable=check_var2, onvalue="on", offvalue="off", 
                                 command= lambda: change_checkbox(check_var=check_var2, checkbox = checkbox2))
    checkbox2.grid(column=0, row=2, padx=MID_PAD_WIDTH, pady=LOW_PAD_HEIGHT, sticky="w")
    #Button3 
    checkbox3 = ctk.CTkCheckBox(main_frame, width=LOW_PAD_WIDTH, height=LOW_PAD_HEIGHT, text="Include uppercase letters ", variable=check_var3, onvalue="on", offvalue="off",
                                 command= lambda: change_checkbox(check_var=check_var3, checkbox = checkbox3))
    checkbox3.grid(column=0, row=3, padx=MID_PAD_WIDTH, pady=LOW_PAD_HEIGHT, sticky="w")
    #Button4 
    checkbox4 = ctk.CTkCheckBox(main_frame, width=LOW_PAD_WIDTH, height=LOW_PAD_HEIGHT, text="Include symbols ", variable=check_var4, onvalue="on", offvalue="off",
                                 command= lambda: change_checkbox(check_var=check_var4, checkbox = checkbox4))
    checkbox4.grid(column=0, row=4, padx=MID_PAD_WIDTH, pady=LOW_PAD_HEIGHT, sticky="w")
    #Length space
    length_text = ctk.CTkLabel(main_frame, width=LOW_PAD_WIDTH, height=LOW_PAD_HEIGHT, text="")
    length_text.grid(column=0, row=5, padx=MID_PAD_WIDTH, pady=LOW_PAD_HEIGHT, sticky="w")
    #Length slider
    slider = ctk.CTkSlider(main_frame, from_=4, to=18, orientation="horizontal", number_of_steps=14, width=2*HIGH_PAD_WIDTH-LOWER_PAD_HEIGHT)
    slider.set(18)
    length_text = ctk.CTkLabel(main_frame, width=LOW_PAD_WIDTH, height=LOW_PAD_HEIGHT, text=f"Password length: {int(slider.get())}")
    length_text.grid(column=0, row=7, padx=MID_PAD_WIDTH, pady=LOW_PAD_HEIGHT, sticky="w")
    slider.configure(command=lambda event, slider=slider, text=length_text :update_length(event, slider, text))
    slider.grid(column=0, row=6, padx=MID_PAD_WIDTH, pady=LOW_PAD_HEIGHT, sticky="w")
    #HW selection
    hw_text = ctk.CTkLabel(main_frame, width=20, height=20, text="Pick brute-Force Hardware:")
    hw_text.grid(column=0, row=8, padx= MID_PAD_WIDTH, pady=LOW_PAD_HEIGHT, sticky="w")
    hardware_options = ctk.CTkComboBox(main_frame, width=2*HIGH_PAD_WIDTH-LOWER_PAD_HEIGHT, height=MID_PAD_HEIGHT, values=HW_VALUES, state="readonly")
    hardware_options.set(HW_VALUES[0])
    hardware_options.grid(column=0, row=9, padx=MID_PAD_WIDTH, pady=LOWER_PAD_HEIGHT, sticky="w")
    #Chart Button
    chart_button = ctk.CTkButton(main_frame, width=2*HIGH_PAD_WIDTH-LOWER_PAD_HEIGHT, height=30, text="Show Hardware Chart", 
                                 fg_color="#000000", text_color="#ffffff", command=lambda hardware_options = hardware_options: show_chart(hardware_options))
    chart_button.grid(column=0, row=10, padx=MID_PAD_WIDTH, pady=LOWER_PAD_HEIGHT, sticky="w")
    #Generate Button
    generate_button = ctk.CTkButton(main_frame, width=250, height=HIGH_PAD_HEIGHT, text="GENERATE", font=("SF Display", 20), 
                                    command=lambda event=None, slider = slider, checkvars = checkvars, right_panel = right_panel: 
                                    gen_password(event, slider, checkvars,  hardware_options, right_panel))
    generate_button.grid(column=0, row=12, padx=MID_PAD_WIDTH, pady=MID_PAD_HEIGHT, sticky="w")
    #Test button generar hash, y modificar el time en caso de poder
    test_button = ctk.CTkButton(main_frame, width=HIGHER_PAD_WIDTH, height=HIGH_PAD_HEIGHT, text="TEST", font=("SF Display", 20), 
                                command=lambda r_panel = right_panel, chart = hardware_options: test_password(r_panel, chart))
    test_button.grid(column=1, row=12, padx=MID_PAD_WIDTH, pady=MID_PAD_HEIGHT, sticky="w")
    return main_frame


def create_right_panel(main_frame):
     #Password
    password_label = ctk.CTkLabel(main_frame, width=20, height=20, text=f"Password (GENERATE) / Insert yours (TEST):")
    password_label.grid(column=1, row=0, padx=MID_PAD_WIDTH, sticky="w")
    pw_textbox = ctk.CTkTextbox(main_frame, width=HIGHER_PAD_WIDTH, height=HIGH_PAD_HEIGHT)
    pw_textbox.custom_name="pw_text"
    pw_textbox.grid(column=1, row=1, rowspan=2, padx=MID_PAD_WIDTH, sticky="w")
    #MD5 Hash
    md5_label = ctk.CTkLabel(main_frame, width=20, height=20, text=f"MD5 Hash:")
    md5_label.grid(column=1, row=3, padx=MID_PAD_WIDTH, pady=LOWER_PAD_HEIGHT, sticky="w")
    md5_textbox = ctk.CTkTextbox(main_frame, width=HIGHER_PAD_WIDTH, height=HIGH_PAD_HEIGHT, state="disabled")
    md5_textbox.custom_name="md5_text"
    md5_textbox.grid(column=1, row=4, rowspan=2, padx=MID_PAD_WIDTH, pady=LOWER_PAD_HEIGHT, sticky="w")
    #Time elapsed
    time_label = ctk.CTkLabel(main_frame, width=20, height=20, text=f"Time elapsed to breach your password: ")
    time_label.grid(column=1, row=6, padx=MID_PAD_WIDTH, pady=LOWER_PAD_HEIGHT, sticky="w")
    time_textbox = ctk.CTkTextbox(main_frame, width=HIGHER_PAD_WIDTH, height=HIGH_PAD_HEIGHT, state="disabled")
    time_textbox.custom_name="time_text"
    time_textbox.grid(column=1, row=7, rowspan=2, padx=MID_PAD_WIDTH, pady=LOWER_PAD_HEIGHT, sticky="w")
    #Data source
    data_button = ctk.CTkButton(main_frame, width=HIGHER_PAD_WIDTH, height=30, text="How can you know this?",fg_color="#000000", text_color="#ffffff", 
                                command = lambda: webbrowser.open(TIME_DATA_SOURCE))
    data_button.grid(column=1, row=10, padx=MID_PAD_WIDTH, pady=LOWER_PAD_HEIGHT, sticky="w")
    return main_frame


#Main function
def main():
    main_frame = create_main_frame(root)
    menu = create_menu(main_frame)
    right_panel = create_right_panel(main_frame)
    left_panel = create_left_panel(main_frame, right_panel)
    root.mainloop()    


if __name__ == "__main__":
    root = create_main_window()
    main()