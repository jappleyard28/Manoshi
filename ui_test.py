from tkinter import *
from datetime import datetime
from tkinter import font
import webbrowser

import nlp
import prediction_guesser

BG_GRAY = "lightgray"
BG_COLOR = "white"
TEXT_COLOR = "black"
FONT = "Helvetica 14"
FONT_BOLD = "Helvetica 13 bold"
row_counter = 1 # number of widgets before the messages
bot_last = False # bot must send the first message
intro_msg = "Hello, how can I help?"

root = Tk()
root.title("Chat")
root.configure(width=500, height=750, bg=BG_COLOR) # root.geometry("500x750")
root.resizable(False, False) # stops window from being resizable

row_counter = 0
bot_last = False # bot must send the first message

#Holds bot conversation state
class State:
    def __init__(self, cur_req, reqs, last_q):
        self.cur_req = cur_req
        self.reqs = reqs
        self.last_q = last_q
        
    def reset(self):
        self.cur_req = None
        self.reqs = None
        self.last_q = None
    
state = State(None, None, None)

#Calls the appropriate request function based on request
def proc(intent):
    global state
    state.cur_req = None
    
    p = state.reqs
    state.reqs = None
    if intent == 'book':
        return nlp.find_ticket(p[0][1], p[1][1], p[2][1], p[3][1])
    if intent == 'bookreturn':
        return nlp.find_return(p[0][1], p[1][1], p[2][1], p[3][1], p[4][1], p[5][1])
    if intent == 'delay':
        return prediction_guesser.get_prediction(p[0][1], p[1][1], p[2][1])

#Determines chatbot response
def help_me(intent, message):
    
    global state
    
    if state.reqs == None: #Determine parameters for rq
        if intent == 'book':
            state.reqs = [["start", None, "GPE", "Where are you travelling from?"],
                     ["destination", None, "GPE", "Where would you like to travel to?"],
                     ["date", None, "DATE", "What date are you travelling?"],
                     ["time", None, "TIME", "What time do you want to travel?"]]
            state.cur_req = 'book'
        elif intent == 'bookreturn':
            state.reqs = [["start", None, "GPE", "Where are you travelling from?"],
                     ["destination", None, "GPE", "Where would you like to travel to?"],
                     ["date", None, "DATE", "What date are you travelling?"],
                     ["time", None, "TIME", "What time do you want to travel?"],
                     ["return_date", None, "DATE", "What date do you want to return?"],
                     ["return_time", None, "TIME", "What time do you want to return?"]]
            state.cur_req = 'bookreturn'
        elif intent == 'delay':
            state.reqs = [["destination", None, "GPE", "Where is your train now?"],
                     ["time", None, "GPE", "Where are you travelling to?"],
                     ["time", None, "TIME", "How long are you delayed?"]]
            state.cur_req = 'delay'
        else:
            return nlp.speak(intent) #Simple response
    
        state.reqs = nlp.response(state.reqs, message, None, intent)
        is_valid = not any(None in l for l in state.reqs)
        if not is_valid: #Not all params acquired, ask a question
            for r in state.reqs:
                if r[1] == None:
                    state.last_q = r[3]
                    return r[3]
        else:
            return proc(intent)
    else:
        state.reqs = nlp.response(state.reqs, message, None, intent)
        is_valid = not any(None in l for l in state.reqs)
        if not is_valid:
            for r in state.reqs:
                if r[1] == None:
                    print(r[3])
                    print(state.last_q)
                    if r[3] == state.last_q:
                        return nlp.speak("datanotfound") + "\n" + state.last_q
                    state.last_q = r[3]
                    return r[3]
        else:
            return proc(intent)
        
def callback(url):
    webbrowser.open_new(url)

class ChatUI:
    
    def __init__(self):
        # head label
        head_label = Label(root, bg=BG_COLOR, fg=TEXT_COLOR, text="Welcome", font=FONT_BOLD, pady=10)
        head_label.grid(row=0, column=0, columnspan=2)
        
        # WIDGET 2
        self.message_canvas = Canvas(root,width=450,height=600)
        self.message_canvas.grid(row=0, column=0, columnspan=2)
        self.message_canvas.grid_propagate(False) # keeps the canvas a fixed size
        
        # SCROLLBAR WIDGET 3
        self.my_scrollbar = Scrollbar(root, orient=VERTICAL, command=self.message_canvas.yview)
        self.my_scrollbar.grid(row=0, column=2, sticky='ns')
        self.message_canvas.configure(yscrollcommand=self.my_scrollbar.set)

        second_frame = Frame(self.message_canvas)
        second_frame.bind('<Configure>', lambda e: self.message_canvas.configure(scrollregion=self.message_canvas.bbox("all")))

        self.message_canvas.create_window((0,0), window=second_frame, anchor="nw")

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
        self.add_message(row_counter, True, intro_msg, second_frame, False)
        
    def run(self):
        root.mainloop()
    
    # WRITES THE USER'S MESSAGE --> CHANGE
    def on_enter_pressed(self, event, second_frame):
        msg = self.input_msgbox.get() # this is the user's message
        self.add_message(row_counter, False, msg, second_frame, False)
        
        #Process bot reply
        message = None
        global state
        if state.cur_req != None:
            intent, message = nlp.parse_input(msg)
            if intent == 'cancel':
                state.reset()
                message = nlp.speak(intent)
            else:
                intent = state.cur_req
                message = help_me(intent, message)
        else:
            intent, message = nlp.parse_input(msg)
            message = help_me(intent, message)
        
        #Determine if a link is provided
        if type(message) == tuple:
            self.add_message(row_counter, True, message[0], second_frame, False)
            self.add_message(row_counter, True, message[1], second_frame, True)
        else:
            self.add_message(row_counter, True, message, second_frame, False)
          
        #Scroll to bottom upon new message
        self.message_canvas.update_idletasks()
        self.message_canvas.yview_moveto(row_counter)
        
    # def insert_message(self, msg, bot_sender):
    def add_message(self, row_no, bot_sender, message_contents, second_frame, is_link):
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
        
        #Change font and add event binding for link message
        if is_link:
            url_font = font.Font(my_message, my_message.cget("font"))
            url_font.configure(underline = True)
            my_message.configure(font=url_font)
            my_message.bind("<Button-1>", lambda e: callback(message_contents))
        my_message.grid(row=row_no, column=column_no, sticky="nsew") # spacing between the message and the message border
        row_counter += 1

        if bot_sender:
            bot_last = True
        else:
            bot_last = False
            
uiTest = ChatUI()
uiTest.run()