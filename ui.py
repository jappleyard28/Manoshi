from tkinter import *
from datetime import datetime

BG_GRAY = "lightgray"
BG_COLOR = "white"
TEXT_COLOR = "black"
FONT = "Helvetica 14"
FONT_BOLD = "Helvetica 13 bold"
row_counter = 1 # number of widgets before the messages
bot_last = False # bot must send the first message
intro_msg = "Hello, how can I help?"
text1 = "hello this is going to be a very long message to see how well it packs it in the message box and if it packs it well, then that will be good"
text2 = "this is also a test to see how well it packs the message in the box"
root = Tk()
root.title("Chat")
root.configure(width=500, height=750, bg=BG_COLOR) # root.geometry("500x750")
root.resizable(False, False) # stops window from being resizable

row_counter = 0
bot_last = False # bot must send the first message

class ChatUI:
    
    def __init__(self):
        # head label
        head_label = Label(root, bg=BG_COLOR, fg=TEXT_COLOR, text="Welcome", font=FONT_BOLD, pady=10)
        head_label.grid(row=0, column=0, columnspan=2)
        
        # WIDGET 2
        message_canvas = Canvas(root,width=450,height=600)
        message_canvas.grid(row=0, column=0, columnspan=2)
        message_canvas.grid_propagate(False) # keeps the canvas a fixed size
        
        # SCROLLBAR WIDGET 3
        my_scrollbar = Scrollbar(root, orient=VERTICAL, command=message_canvas.yview)
        my_scrollbar.grid(row=0, column=2, sticky='ns')
        message_canvas.configure(yscrollcommand=my_scrollbar.set)

        second_frame = Frame(message_canvas)
        second_frame.bind('<Configure>', lambda e: message_canvas.configure(scrollregion=message_canvas.bbox("all")))

        message_canvas.create_window((0,0), window=second_frame, anchor="nw")

        # bottom label (background for the section around the input text box and send button)
        bottom_label = Label(root, bg=BG_GRAY)
        bottom_label.grid(row=1, column=0, sticky='nesw')
        
        # # input message entry box (message box user writes in)
        self.input_msgbox = Entry(bottom_label, bg="white", fg=TEXT_COLOR, font=FONT)
        self.input_msgbox.grid(row=0, column=0, padx=20, pady=10)
        self.input_msgbox.bind("<Return>", lambda event, num=4: self.on_enter_pressed(event, second_frame))
        
        # send button
        send_button = Button(bottom_label, text="Send", font=FONT_BOLD, width=20, bg=BG_GRAY,command=lambda: self.on_enter_pressed(None, second_frame))
        send_button.grid(row=0, column=1, padx=20, pady=10)

        # Test data for report
        self.add_message(row_counter, True, intro_msg, second_frame)
        self.add_message(row_counter, False, "dfaksjl", second_frame)
        self.add_message(row_counter, True, "Sorry I don't understand", second_frame)
        self.add_message(row_counter, False, "Find the cheapest train", second_frame)
        self.add_message(row_counter, True, "Where are you travelling from?", second_frame)
        self.add_message(row_counter, True, "Liverpool street", second_frame)
        self.add_message(row_counter, True, "Where are you travelling to?", second_frame)
        
    def run(self):
        root.mainloop()
    
    # WRITES THE USER'S MESSAGE --> CHANGE
    def on_enter_pressed(self, event, second_frame):
        msg = self.input_msgbox.get() # this is the user's message
        self.add_message(row_counter, False, msg, second_frame)
        
    # def insert_message(self, msg, bot_sender):
    def add_message(self, row_no, bot_sender, message_contents, second_frame):
        global row_counter
        global bot_last

        # if the bot sends the message
        column_no = 0
        message_header = "Train Bot"
        label_side = "nw"
        message_bg = "white"

        # if the user sends the message
        if not (bot_sender):
            column_no = 1
            message_header = "You"
            label_side = "ne"
            message_bg = "lightblue"
        
        # stops the bot or user title from showing if he sends multiple messages after one another
        if (bot_last and bot_sender) or (not(bot_last) and not(bot_sender)):
            message_header = ""
        
        self.input_msgbox.delete(0, END) # removes the text from the input message box after it is sent

        # CREATE ANOTHER FRAME INSIDE THE CANVAS
        frame1 = LabelFrame(second_frame, text=message_header, labelanchor=label_side, font=FONT_BOLD)
        frame1.grid(row=row_no, column=column_no, padx=20, pady=0)
        my_message = Message(frame1, text=message_contents, font=FONT, aspect=150, justify="left", bg=message_bg, width=100)
        my_message.grid(row=row_no, column=column_no, sticky="nsew") # spacing between the message and the message border
        row_counter += 1

        if bot_sender:
            bot_last = True
        else:
            bot_last = False

uiTest = ChatUI()
uiTest.run()