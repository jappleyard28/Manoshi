from tkinter import *
from datetime import datetime
# from chat import get_response, bot_name

BG_GRAY = "lightgray"
BG_COLOR = "white"
TEXT_COLOR = "black"

FONT = "Helvetica 14"
FONT_BOLD = "Helvetica 13 bold"

window = Tk()
window.title("Chat")
window.configure(width=500, height=750, bg=BG_COLOR)

bubbles = []

class ChatApplication:
    
    def __init__(self):        
        # head label
        head_label = Label(window, bg=BG_COLOR, fg=TEXT_COLOR, text="Welcome", font=FONT_BOLD, pady=10)
        head_label.place(relwidth=1)
        
        # text widget (SECTION THAT DISPLAYS THE TEXT MESSAGES)
        self.text_widget = Text(window, width=20, height=2, bg=BG_COLOR, fg=TEXT_COLOR, font="FONT", padx=5, pady=5)
        self.text_widget.place(relheight=0.745, relwidth=1, rely=0.08) # sizes the text messages section in proportion to the window's size
        self.text_widget.configure(cursor="arrow", state=DISABLED) # this makes it only readable as the user can't click on it so that it can be written to afterwards
        
        # scroll bar
        scrollbar = Scrollbar(self.text_widget)
        scrollbar.place(relheight=1, relx=0.974)
        scrollbar.configure(command=self.text_widget.yview)
        
        # bottom label (background for the section around the input text box and send button)
        bottom_label = Label(window, bg=BG_GRAY, height=80)
        bottom_label.place(relwidth=1, rely=0.825)
        
        # input message entry box (message box user writes in)
        self.input_msgbox = Entry(bottom_label, bg="white", fg=TEXT_COLOR, font=FONT)
        self.input_msgbox.place(relwidth=0.74, relheight=0.06, rely=0.008, relx=0.011)
        self.input_msgbox.focus()
        self.input_msgbox.bind("<Return>", self._on_enter_pressed)
        
        # send button
        send_button = Button(bottom_label, text="Send", font=FONT_BOLD, width=20, bg=BG_GRAY,command=lambda: self._on_enter_pressed(None))
        send_button.place(relx=0.77, rely=0.008, relheight=0.06, relwidth=0.22)
        
    def run(self):
        window.mainloop()
        
    
    # WRITES THE USER'S MESSAGE --> CHANGE
    def _on_enter_pressed(self, event):
        msg = self.input_msgbox.get() # this is the user's message
        self._insert_message(msg, "You")
        
    def _insert_message(self, msg, sender):
        if not msg:
            return
        
        # User message
        self.input_msgbox.delete(0, END)
        msg1 = f"{sender}: {msg}\n\n"
        self.text_widget.configure(state=NORMAL)
        self.text_widget.insert(END, msg1)
        self.text_widget.configure(state=DISABLED)
        
        # bot message
        bot_name = "Bot noob"
        message = "I do not understand"

        msg2 = f"{bot_name}: {message}\n\n"
        self.text_widget.configure(state=NORMAL)
        self.text_widget.insert(END, msg2)
        self.text_widget.configure(state=DISABLED)
        
        self.text_widget.see(END)

        
if __name__ == "__main__":
    ui = ChatApplication()
    ui.run()