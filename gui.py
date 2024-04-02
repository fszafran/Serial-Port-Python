import tkinter as tk
from tkinter import filedialog, END, Text, Frame, Scrollbar, Label, Entry, Button
import sys 
import serial
import time 
import threading


nazwa_portu = ''
port = None
thread=None
class SerialPort:
    def __init__(self, port_name, baud_rate, byte_size, stop_bits, parity):
        self.ser = serial.Serial(
            port=port_name,
            baudrate=baud_rate,
            bytesize=byte_size,
            stopbits=stop_bits,
            parity=parity,
            timeout=0.5 
        )
        

    def read_data(self):
        mess=""
        while self.ser and self.ser.isOpen():
            if self.ser.in_waiting > 0:
                byte = self.ser.read(1)
                if byte==b'\n' or byte==b'\r':
                    print(mess)
                    mess =""

                else:
                    mess+= byte.decode("utf-8")
            else:
                time.sleep(0.1)  

    def write_string(self, message):
        message = bytes(message, 'utf-8')
        try:
            self.ser.write(message)
            print("INFO: Successfully wrote to serial port.")
        except serial.SerialException:
            print("ERROR: Unable to write to serial port.")
            return False
        

        
    def close(self):
        self.ser.close()
        return True

def redirect_stdout_to_text_widget(text_widget):
    class StdoutRedirector:
        def __init__(self, text_widget):
            self.text_widget = text_widget

        def write(self, text):
            self.text_widget.insert(tk.END, text)
            self.text_widget.see(tk.END)

        def flush(self):
            pass

    sys.stdout = StdoutRedirector(text_widget)


class MyApp:
    def __init__(self, root):
        self.root = root
        self.root.title('ETPG ZADANIE 1')
        self.root.geometry('600x400')
        self.create_main_window()

    def create_main_window(self):
        global nazwa_portu, port
        port = None
        for widget in self.root.winfo_children():
            widget.grid_remove()
        
        self.root.geometry('500x250')

        self.nadawanie = Button(self.root, text="SEND", command=self.fourth_window, width=20, height=10, font=('Arial', 12, 'bold'), bg='blue', fg='white')
        self.nadawanie.grid(row=0, column=0, padx=10, pady=10)
        self.odbior = Button(self.root, text="RECEIVE", command=self.second_window, width=20, height=10, font=('Arial', 12, 'bold'), bg='green', fg='white')
        self.odbior.grid(row=0, column=2, padx=10, pady=10)

        puste = Label(self.root, text="  ")
        puste.grid(row=0, column=1)

    def second_window(self):
        global nazwa_portu, port
        port = None
        for widget in self.root.winfo_children():
            widget.grid_remove()

        self.root.geometry('600x300')

        info = Label(self.root, text='TYPE PORT NAME', font=('Arial', 20, 'bold'))
        info.grid(row=0, column=0, columnspan=4, pady=20)

        self.port_name = Entry(self.root, width=40, font=('Arial', 20))
        self.port_name.grid(row=1, column=0, columnspan=4, padx=10, pady=10)

        self.error_label = Label(self.root, text='', font=('Arial', 16), fg='red')
        self.error_label.grid(row=2, column=0, columnspan=4, pady=10)

        puste = Label(self.root, text="  ")
        puste.grid(row=3, column=2)

        next_button = Button(self.root, text="NEXT", command=self.check_port_name_one, width=30, height=2, font=('Arial', 14, 'bold'), bg='lightblue')
        next_button.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

        back_button = Button(self.root, text="Return to main menu", command=self.stop_communication, font=('Arial', 14), bg='red', fg='white')
        back_button.grid(row=3, column=2, columnspan=2, padx=10, pady=10)

    def check_port_name_one(self):
        port_name = self.port_name.get()
        if not port_name:
            self.error_label.configure(text='Port name is empty')
        else:
            self.error_label.configure(text='')
            self.third_window()

    def stop_communication(self):
        global port, thread
        if port is not None and thread is not None:
            self.ser.close()
            port.close()
            thread = None 
            port = None
            print('Port closed successfully')
        else:
            print('Port is not opened')
        self.create_main_window()

    def read_from_port(self):
        global port, thread
        if port.ser.isOpen():
            print('Reading from port...')
            thread = threading.Thread(target=port.read_data)
            thread.start()
        else:
            print('Port is not opened')

    def save_to_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if file_path:
            try:
                with open(file_path, 'w') as file:
                    console_text = self.console_output.get(1.0, tk.END)  
                    file.write(console_text)
                    print(f"Saved output to {file_path}")
            except Exception as e:
                print(f"An error occurred: {e}")


    def third_window(self):
        for widget in self.root.winfo_children():
            widget.grid_remove()

        self.root.geometry('800x500')

        self.console_output = Text(self.root, wrap=tk.WORD, width=100, height=20)
        self.console_output.grid(row=0, column=0, columnspan=6)

        pusty = Label(self.root, text="")
        pusty.grid(row=1, column=0)

        start_button = Button(self.root, text="Start Communication", width=30, height=5, command=self.open_port, bg='lightgreen')
        start_button.grid(row=2, column=0, columnspan=2)

        back_button = Button(self.root, text="Return to main menu", width=30, height=5, command=self.stop_communication, bg='red', fg='white')
        back_button.grid(row=2, column=4, columnspan=2, )

        read_button = Button(self.root, text="Read", width=30, height=5, command=self.read_from_port, bg='lightblue')
        read_button.grid(row=2, column=2, columnspan=2, pady=10)

        save_button = Button(self.root, text="Save to file", command=self.save_to_file, bg='orange', height=2, width=30)
        save_button.grid(row=3, column=2, columnspan=2)

        self.port_status_label = Label(self.root, text="")
        self.port_status_label.grid(row=3, column=0, columnspan=2)

        redirect_stdout_to_text_widget(self.console_output)

    def open_port(self):
        global port
        if port:
            port.close()
            port = None
        if self.port_name.get():
            port=SerialPort(self.port_name.get().upper(),baud_rate=9600, byte_size=8, stop_bits=1, parity='N') 
        else:
            port = SerialPort(port_name='COM9', baud_rate=9600, byte_size=8, stop_bits=1, parity='N')
        print('Port opened successfully')
        if not port:
            print('Port is not opened')
            return    
        
    def write_to_port(self):
        global port
        print('Sending message...')
        if not port:
            print('Port is not opened')
            return
        message = self.input_text.get('1.0', END)
        port.write_string(message)

    def fourth_window(self):
        global nazwa_portu, port
        port = None
        for widget in self.root.winfo_children():
            widget.grid_remove()

        self.root.geometry('600x300')

        info = Label(self.root, text='TYPE PORT NAME', font=('Arial', 20, 'bold'))
        info.grid(row=0, column=0, columnspan=4, pady=20)

        self.port_name = Entry(self.root, width=40, font=('Arial', 20))
        self.port_name.grid(row=1, column=0, columnspan=4, padx=10, pady=10)

        self.error_label = Label(self.root, text='', font=('Arial', 16), fg='red')
        self.error_label.grid(row=2, column=0, columnspan=4, pady=10)

        puste = Label(self.root, text="  ")
        puste.grid(row=3, column=2)

        next_button = Button(self.root, text="NEXT", command=self.check_port_name_two, width=30, height=2, font=('Arial', 14, 'bold'), bg='lightblue')
        next_button.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

        back_button = Button(self.root, text="Return to main menu", command=self.stop_communication, font=('Arial', 14), bg='red', fg='white')
        back_button.grid(row=3, column=2, columnspan=2, padx=10, pady=10)

    def check_port_name_two(self):
        port_name = self.port_name.get()
        if not port_name:
            self.error_label.configure(text='Port name is empty')
        else:
            self.error_label.configure(text='')
            self.fifth_window()

    def fifth_window(self):
        for widget in self.root.winfo_children():
            widget.grid_remove()
        self.root.geometry('1200x600')

        input_label = Label(self.root, text="Input:", font=('Arial', 20, 'bold'), fg='blue')
        input_label.grid(row=0, column=0, columnspan=4)

        input_text_frame = Frame(self.root, width=50, height=20)
        input_text_frame.grid(row=1, column=0, rowspan=2, columnspan=4)

        output_text_frame = Frame(self.root, width=50, height=20)
        output_text_frame.grid(row=4, column=5, rowspan=2, columnspan=2, padx=10)

        self.input_text_scrollbar = Scrollbar(input_text_frame)
        self.input_text_scrollbar.pack(side='right', fill='y')
        
        self.output_text_scrollbar = Scrollbar(output_text_frame)
        self.output_text_scrollbar.pack(side='right', fill='y')

        self.input_text = Text(input_text_frame, width=50, font=('Arial', 20, 'bold'), height=10)
        self.input_text.pack(side='left', fill='both')

        self.console_output = Text(output_text_frame, wrap=tk.WORD, width=50, height=10)
        self.console_output.pack(side='left', fill='both')

        self.input_text_scrollbar.config(command=self.input_text.yview)
        self.input_text.config(yscrollcommand=self.input_text_scrollbar.set)

        self.output_text_scrollbar.config(command=self.console_output.yview)
        self.console_output.config(yscrollcommand=self.output_text_scrollbar.set)

        pusty = Label(self.root, text="")
        pusty.grid(row=3, column=0)

        import_button = Button(self.root, text="Import File", width=50, height=5, command=self.import_file, bg='lightgreen', fg='black')
        import_button.grid(row=4, column=0, columnspan=2)

        send = Button(self.root, text="Send", width=50, height=5, command=self.write_to_port, bg='orange', fg='white')
        send.grid(row=4, column=3, columnspan=2)

        back_button = Button(self.root, text="Return to main menu", command=self.stop_communication, font=('Arial', 14), bg='red', fg='white')
        back_button.grid(row=5, column=2, columnspan=2)

        open_button = Button(self.root, text="Open Port", command=self.open_port, width=30, height=10, bg='lightblue', fg='black')
        open_button.grid(row=1, column=5)

        read_button = Button(self.root, text="Read message", width=30, height=10, command=self.read_from_port, bg='darkblue', fg='white')
        read_button.grid(row=2, column=5)

        redirect_stdout_to_text_widget(self.console_output)


    def import_file(self):
        file_path = filedialog.askopenfilename(title="Select File", filetypes=[("Text files", "*.txt")])
        if not file_path:
            print("No file selected. Exiting.")
            return
        with open(file_path, 'r') as file:
            file_content = file.read()

        self.input_text.delete('1.0', END)
        self.input_text.insert('1.0', file_content)


if __name__ == "__main__":
    root = tk.Tk()
    app = MyApp(root)

    def delete_all():
        global port, thread 
        for widget in root.winfo_children():
            widget.grid_remove()
            if port is not None or thread is not None:
                port.close()
                thread = None  
                port = None
                print('Port closed successfully')
        root.quit()

    root.protocol("WM_DELETE_WINDOW", delete_all)
    root.mainloop()