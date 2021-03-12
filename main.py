import ea_psu_controller
import tkinter as tk
import tkinter.messagebox
import tkinter.ttk as ttk
import serial.tools.list_ports


OUTPUT = 0


class Application(tk.Frame):
    psu: ea_psu_controller.PsuEA

    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.com_ports = serial.tools.list_ports.comports()
        self.create_widgets()
        self.psu = None
        self.connected = False
        self.prev_v = 0
        self.prev_c = 0
        # self.bind("<Enter>", self.psu_connect)
        for i, port in enumerate(self.com_ports):
            if "PS 2300" in port.description:
                self.com_set.set(self.com_set["values"][i])

    def update_com(self):
        if not self.connected:
            temp = serial.tools.list_ports.comports()
            if temp != self.com_ports:
                self.com_set.set("")

            self.com_ports = temp

            self.com_set["values"] = [x.description for x in self.com_ports]





    def create_widgets(self):
        self.vc_frame = tk.Frame(self)
        self.connect_frame = tk.Frame(self)

        self.voltage_frame = tk.Frame(self.vc_frame)
        self.current_frame = tk.Frame(self.vc_frame)


        self.voltage_get = tk.Label(self.voltage_frame, text="NA.NA V", font=("Seven Segment", 40), width=6)
        self.current_get = tk.Label(self.current_frame, text="NA.NA A", font=("Seven Segment", 40), width=6)
        self.com_label = tk.Label(self.connect_frame, text="COM PORT:")
        self.status_led = tk.Canvas(self.connect_frame, width=20, height=20, background="red")

        self.voltage_set = tk.Spinbox(self.voltage_frame, width=6, state="disabled", validate="key", font=("Seven Segment", 20), from_=0.0, to=42.0, format="%.2f", increment=0.1)
        self.voltage_set["validatecommand"] = (self.voltage_set.register(self.is_float), "%P")
        self.current_set = tk.Spinbox(self.current_frame, width=6, state="disabled", validate="key", font=("Seven Segment", 20), from_=0.0, to=5.0, format="%.2f", increment=0.1)
        self.current_set["validatecommand"] = (self.current_set.register(self.is_float), "%P")

        self.voltage_set.register(self.is_float)
        self.voltage_set.config(validate="key", validatecommand = (self.voltage_set.register(self.is_float), "%P"))

        self.button_offon = tk.Button(self.vc_frame, width=7, text="1/0", font=("Seven Segment", 18), command=self.offon, background="grey")
        self.voltage_button = tk.Button(self.voltage_frame, width=10, state="disabled", text="SET", command=self.set_voltage)
        self.current_button = tk.Button(self.current_frame, width=10, state="disabled", text="SET", command=self.set_current)
        # self.com_set = tk.Entry(self.connect_frame, width=6)
        self.com_set = ttk.Combobox(self.connect_frame, width=30, values=[port.description for port in self.com_ports], postcommand=self.update_com)
        self.com_set.after(500, self.update_com)

        self.connect_psu = tk.Button(self.connect_frame, text="Connect", command=self.psu_connect, width=20)

        self.voltage_get.pack(side=tk.TOP, pady=5)
        self.voltage_set.pack(side=tk.TOP, pady=5)
        self.voltage_button.pack(side=tk.TOP, pady=5)

        self.current_get.pack(side=tk.TOP, pady=5)
        self.current_set.pack(side=tk.TOP, pady=5)
        self.current_button.pack(side=tk.TOP, pady=5)



        self.com_label.pack(side=tk.LEFT)
        self.com_set.pack(side=tk.LEFT, padx=10)
        self.connect_psu.pack(side=tk.RIGHT, padx=10)
        self.status_led.pack(side=tk.RIGHT)

        self.button_offon.pack(side=tk.LEFT, fill=tk.BOTH, pady=5)
        self.voltage_frame.pack(side=tk.LEFT, padx=20)
        self.current_frame.pack(side=tk.LEFT)

        self.vc_frame.pack(side=tk.TOP,padx=10)
        self.connect_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(20,5), padx=(5,0))


    def offon(self):
        if self.connected:
            print(self.psu.get_status(OUTPUT))
            if self.psu.get_status(OUTPUT)["output on"]:
                self.psu.output_off(OUTPUT)
            else:
                self.psu.output_on(OUTPUT)

    def set_voltage(self):
        if self.connected and self.voltage_set.get() != "":
            self.psu.set_voltage(float(self.voltage_set.get()), OUTPUT)
            self.voltage_set["text"] = ""


    def set_current(self):
        if self.connected and self.current_set.get() != "":
            self.psu.set_current(float(self.current_set.get()), OUTPUT)
            self.current_set["text"] = ""



    def psu_connect(self):
        if not self.connected:
            try:
                self.psu = ea_psu_controller.PsuEA(comport=self.com_set.get())
                self.psu.remote_on(OUTPUT)

                self.connected = True

                self.vc_frame.after(300, self.update_values)

            except Exception as e:
                print(e)
                self.psu = None
        else:
            self.psu.close(remote=True)
            self.psu = None
            self.connected = False

    def update_values(self):
        if self.connected and self.psu is not None:
            self.connect_psu["text"] = "Disconnect"
            self.status_led["background"] = "green"
            self.voltage_set["state"] = "normal"
            self.current_set["state"] = "normal"
            self.voltage_button["state"] = "normal"
            self.current_button["state"] = "normal"

            try:
                current = round(self.psu.get_current(OUTPUT),2)
                voltage = round(self.psu.get_voltage(OUTPUT),2)
                self.voltage_get["text"] = "{:05.2f} V".format(voltage)
                self.current_get["text"] = "{:05.2f} A".format(current)

                if current > self.prev_c:
                    self.current_get["fg"]="green"
                elif current < self.prev_c:
                    self.current_get["fg"]="red"
                else:
                    self.current_get["fg"] = "black"

                if voltage > self.prev_v:
                    self.voltage_get["fg"]="green"
                elif voltage < self.prev_v:
                    self.voltage_get["fg"]="red"
                else:
                    self.voltage_get["fg"] = "black"

                self.prev_v = voltage
                self.prev_c = current

                self.status_led["background"] = "green"

                if self.psu.get_status(OUTPUT)["output on"]:
                    self.button_offon["background"] = "red"
                    self.button_offon["text"] = "OFF"
                else:
                    self.button_offon["background"] = "green"
                    self.button_offon["text"] = "ON"

            except serial.SerialException as e:
                print(e)
                self.connected = False
                self.psu = None
                tk.messagebox.showerror(title="COM error", message="Power Supply disconnected")

            self.com_set["state"] = "disabled"
            self.vc_frame.after(300, self.update_values)

        else:
            self.connect_psu["text"] = "Connect"
            self.status_led["background"] = "red"
            self.voltage_get["text"] = "NA.NA V"
            self.current_get["text"] = "NA.NA A"
            self.current_get["fg"] = "black"
            self.voltage_get["fg"] = "black"
            self.status_led["background"] = "red"
            self.button_offon["background"] = "grey"
            self.button_offon["text"] = "1/0"
            self.com_set["state"] = "normal"
            self.voltage_set["state"] = "disabled"
            self.current_set["state"] = "disabled"
            self.voltage_button["state"] = "disabled"
            self.current_button["state"] = "disabled"


    def on_exit(self):
        if self.psu is not None and self.connected:
            self.psu.close(remote=True)

    def is_float(self, x):
        if x == '':
            return True
        try:
            float(x)
            return True
        except ValueError:
            return False









def close_root():
    print("BYE")
    app.on_exit()
    root.destroy()

root = tk.Tk()
root.wm_iconbitmap("icon.ico")
root.wm_title("PowerSupply Output {} control".format(OUTPUT+1))
root.wm_resizable(0, 0)
app = Application(root)
root.protocol("WM_DELETE_WINDOW", close_root)
app.mainloop()



# psu = ea_psu_controller.PsuEA(comport="COM3")
# psu.remote_on(0)
# psu.set_voltage(12.0, 0)
# psu.set_current(1.0, 0)
# psu.output_on(0)
# print(psu.get_status(0), psu.get_voltage(0))
# psu.close(remote=True)
