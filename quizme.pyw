"""GUI for taking tests based on quizme-xxx.json files.
"""
import os
import sys
import json
from random import randint

import tkinter as tk
from tkinter import font
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox

from widgetrefs import widgets

def center_window(window):
    """Position a window in the center of the screen.

    1st parameter = window
    """
    window.update_idletasks()
    width = window.winfo_screenwidth()
    height = window.winfo_screenheight()
    size = tuple(int(_) for _ in window.geometry().split('+')[0].split('x'))
    offsetx = width/2 - size[0]/2
    offsety = height/2 - size[1]/2
    window.geometry("%dx%d+%d+%d" % (size + (offsetx, offsety)))


def display_help():
    """Display the help screen.
    """
    helpmsg = (
        'QuizMe is an interactive tool for testing your ability to answer\n'
        'a set of multi-choice questions.\n\n'
        'Use the underlined hotkeys 1-5 to select your answer, then\n'
        'press C to check your answer. You can also press Enter to\n'
        'check your answer.\n\n'
        'To select a different question, press P, N, or R for Previous,\n'
        'Next or Random. You can also use the left/right arrow keys to\n'
        'move through the questions in order.\n\n'
        'Have fun!')
    messagebox.showinfo('Help', helpmsg)


def display_score():
    """Display the current score (number and percent correct).
    """
    totq = len(widgets.questions) # total questions in current topic
    totans = widgets.totAnswered # number of questions answered so far
    correct = widgets.totCorrect # number of correct answers so far
    perc = 0 if totans == 0 else 100*(correct/totans)
    title = widgets.topic + ' - {0} total questions'.format(totq)
    msg = "You have {0} out of {1} correct for {2:.0f}%."
    messagebox.showinfo(title, msg.format(correct, totans, perc))


def display_question():
    """Refresh display for current question.

    Note: question-related state info is stored in widgets. properties.
    """
    q_num = widgets.currentq # current question#
    u_answered = (q_num in widgets.answered) # whether answered
    u_answer = widgets.answered.get(q_num, '') # user's answer (if any)
    question = widgets.questions[q_num] # current question dict()
    q_corrnum = question['correct'] # the correct answer ('1' through '5')
    q_corrtext = question['answers'].get(q_corrnum, '') # text of answer
    u_correct = (u_answer == q_corrnum) # whether user's answer is correct

    widgets.lblHeader.configure(text='Topic:\n'+widgets.topic)
    widgets.txtQuestion.config(state="normal")
    widgets.txtQuestion.delete(1.0, tk.END)
    widgets.txtQuestion.insert(tk.END, question['question'])
    widgets.txtQuestion.focus_set() # set focus to the question
    widgets.txtQuestion.config(state="disabled")
    currentstate = 'disabled' if u_answered else 'normal'
    display_radiobuttons(rbstate=currentstate, rbselected=u_answer)
    # "correct answer" textbox
    widgets.txtCorrect.config(state="normal")
    widgets.txtCorrect.delete(1.0, tk.END)
    widgets.txtCorrect.config(bg="white")
    if u_answered:
        if u_correct:
            msg = '#' + u_answer + ' is CORRECT - ' + q_corrtext
        else:
            msg = '#' + u_answer + \
                ' is INCORRECT - correct answer is #' + \
                q_corrnum + ': ' + q_corrtext
        widgets.txtCorrect.insert(tk.END, msg)
        bgcolor = "#B1ECB1" if u_correct else "#FFC6C5"
    else:
        bgcolor = 'white' # white background if question not answered yet
    widgets.txtCorrect.config(bg=bgcolor)
    widgets.txtCorrect.config(state="disabled")
    widgets.txtExplanation.config(state="normal")
    widgets.txtExplanation.delete(1.0, tk.END)
    if u_answered:
        widgets.txtExplanation.insert(tk.END, question.get('explanation', ''))
    widgets.txtExplanation.config(state="disabled")

    image = question.get('image', '')
    answerimage = question.get('answerimage', '')
    displayedimage = answerimage if (u_answered and answerimage) else image
    if displayedimage:
        displayedimage = 'images/' + displayedimage
        # PhotoImage() needs a reference to avoid garbage collection
        widgets.image = tk.PhotoImage(file=displayedimage)
        widgets.lblImage.configure(image=widgets.image)
    else:
        widgets.image = None
        widgets.lblImage['image'] = None


def display_radiobuttons(rbstate='normal', rbselected=''):
    """Set radiobuttons to the answer options for the current question.

    state = the state to set the radiobuttons to; 'normal' or 'disabled'
    selected = the radiobutton to select (e.g., '1', or '' for none)
    """
    question = widgets.questions[widgets.currentq]

    # radiobuttons (answers)
    text1 = question['answers'].get('1', '')
    text2 = question['answers'].get('2', '')
    text3 = question['answers'].get('3', '')
    text4 = question['answers'].get('4', '')
    text5 = question['answers'].get('5', '')
    # note that we hide unused radiobuttons by lowering them in
    # the Z-order so that they're hidden behind widgets.rbframe
    if text1:
        widgets.answer1.configure(text='1: '+text1, state=rbstate)
        widgets.answer1.lift(widgets.rbframe)
    else:
        widgets.answer1.configure(text='', state='disabled')
        widgets.answer1.lower(widgets.rbframe)
    if text2:
        widgets.answer2.configure(text='2: '+text2, state=rbstate)
        widgets.answer2.lift(widgets.rbframe)
    else:
        widgets.answer2.configure(text='', state='disabled')
        widgets.answer2.lower(widgets.rbframe)
    if text3:
        widgets.answer3.configure(text='3: '+text3, state=rbstate)
        widgets.answer3.lift(widgets.rbframe)
    else:
        widgets.answer3.configure(text='', state='disabled')
        widgets.answer3.lower(widgets.rbframe)
    if text4:
        widgets.answer4.configure(text='4: '+text4, state=rbstate)
        widgets.answer4.lift(widgets.rbframe)
    else:
        widgets.answer4.configure(text='', state='disabled')
        widgets.answer4.lower(widgets.rbframe)
    if text5:
        widgets.answer5.configure(text='5: '+text5, state=rbstate)
        widgets.answer5.lift(widgets.rbframe)
    else:
        widgets.answer5.configure(text='', state='disabled')
        widgets.answer5.lower(widgets.rbframe)

    # select the user's answer (or clear selection if rbselected=='')
    widgets.answerSelection.set(rbselected)


def initialize_score():
    """Initialize/reset the total answered and total correct.
    """
    widgets.totAnswered = 0
    widgets.totCorrect = 0
    widgets.answered = dict() # key=question#, value = user's answer


def keystroke_bindings():
    """Assign keyboard shortcuts.
    """
    root.bind('1', lambda event: widgets.answerSelection.set('1'))
    root.bind('2', lambda event: widgets.answerSelection.set('2'))
    root.bind('3', lambda event: widgets.answerSelection.set('3'))
    root.bind('4', lambda event: widgets.answerSelection.set('4'))
    root.bind('5', lambda event: widgets.answerSelection.set('5'))
    root.bind('c', lambda event: save_answer())
    root.bind('C', lambda event: save_answer())
    root.bind('<Return>', lambda event: save_answer())
    root.bind('<Left>', lambda event: move_previous())
    root.bind('p', lambda event: move_previous())
    root.bind('P', lambda event: move_previous())
    root.bind('<Right>', lambda event: move_next())
    root.bind('n', lambda event: move_next())
    root.bind('N', lambda event: move_next())
    root.bind('r', lambda event: move_random())
    root.bind('R', lambda event: move_random())
    root.bind('s', lambda event: display_score())
    root.bind('S', lambda event: display_score())
    root.bind('t', lambda event: select_topic(gui=True))
    root.bind('T', lambda event: select_topic(gui=True))
    root.bind('h', lambda event: display_help())
    root.bind('H', lambda event: display_help())
    root.bind('<F1>', lambda event: display_help())
    root.bind("<Key-Escape>", lambda event: root.quit()) # Esc=quit


def move_next():
    """Move to next question.
    """
    qnum_int = int(widgets.currentq) # convert question# to integer
    if qnum_int < widgets.totalquestions:
        widgets.currentq = str(qnum_int + 1)
        display_question()


def move_previous():
    """Move to previous question.
    """
    qnum_int = int(widgets.currentq) # convert question# to integer
    if qnum_int > 1:
        widgets.currentq = str(qnum_int - 1)
        display_question()


def move_random():
    """Move to a random question.
    """
    # handle the case where all questions have been answered
    if len(widgets.answered) == widgets.totalquestions:
        topic_completed()
        return

    # unanswered[] = list of remaining unanswered question numbers
    unanswered = []
    for qnum in range(1, widgets.totalquestions+1):
        if str(qnum) not in widgets.answered:
            unanswered.append(str(qnum))
    # now we select a random question# from unanswered[]
    random_index = randint(0, len(unanswered)-1)
    widgets.currentq = str(unanswered[random_index])
    display_question()


def pythonw_setup():
    """Handle default folder location if running under pythonw.exe.

    The pythonw.exe launcher starts from the Windows System32 folder
    as the default location, which isn't typically what's desired.
    This function checks whether we're running under pythonw.exe, and
    if so sets the default folder to the location of this program.
    """
    fullname = sys.executable
    nameonly = os.path.split(fullname)[1].split('.')[0].lower()
    if nameonly == 'pythonw':
        progfolder = os.path.dirname(os.path.realpath(sys.argv[0]))
        os.chdir(progfolder)


def read_datafile():
    """Read widgets.dataFile and store questions in widgets.questions.

    NOTE: the data file must include questions numbered 1-N with no gaps.
    """
    with open(widgets.dataFile, 'r') as jsonfile:
        widgets.questions = json.load(jsonfile)

    widgets.currentq = '1' # current question#
    widgets.totalquestions = len(widgets.questions)


def save_answer():
    """Save the current answer and refresh displayed question.
    """
    q_num = widgets.currentq # current question#
    question = widgets.questions[q_num] # current question dict()

    if q_num in widgets.answered:
        return # this question has already been answered

    answer = widgets.answerSelection.get()
    if not answer or answer not in '12345':
        return # an answer has not been selected

    # update totals
    widgets.totAnswered += 1
    if answer == question['correct']:
        widgets.totCorrect += 1
    widgets.answered[q_num] = answer

    # refresh the display based on current status
    display_question()

    # if all questions have been answered, display score
    if len(widgets.answered) == widgets.totalquestions:
        topic_completed()


def select_topic(gui=True):
    """Select a topic (.json file).

    If gui=True, the quizme app window exists and will be updated if
    a topic is selected.

    Returns the selected filename (or '' if none selected), and the
    global widgets object's properties are updated.
    """
    if not gui:
        tempwindow = tk.Tk() # create the top-level window
        tempwindow.withdraw() # hide the top-level window behind this dialog

    newtopic = filedialog.askopenfilename(title='select QuizMe file',
                                          initialdir='data',
                                          filetypes=[('JSON files', '.json')])

    if not gui:
        tempwindow.destroy() # destroy the temporary top-level window

    if newtopic:
        # a file was selected
        widgets.dataFile = newtopic

        # by convention topic name is the part of the filename after '-'
        # e.g., filename = quizme-TopicName.json
        nameonly = os.path.basename(newtopic)
        nameonly = os.path.splitext(nameonly)[0]
        widgets.topic = nameonly

        widgets.currentq = '1' # start with first topic
        widgets.answered = {} # reset answered questions

        if gui:
            read_datafile()
            display_question()

    return newtopic


def topic_completed():
    """Topic has been completed, so show score and ask whether to re-start.
    """
    messagebox.showwarning(
        'Topic Completed',
        'You have already answered all of the questions in this topic!')
    display_score()
    questiontext = 'Do you want to start over with this topic?'
    if messagebox.askyesno('Topic Completed', questiontext):
        initialize_score()
        widgets.currentq = '1'
        display_question()


class MainApplication(ttk.Frame):
    """Root application class.
    """
    def __init__(self, parent, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        self.grid(sticky="nsew")
        self.parent = parent
        self.parent.title('QuizMe')
        self.parent.iconbitmap('quizme.ico')

        initialize_score()

        self.widgets_create()
        display_question() # display first question in selected topic

        # customize styles
        style = ttk.Style()
        style.configure("TButton", font=('Verdana', 12))
        style.configure("TRadiobutton", font=('Verdana', 12))

        keystroke_bindings()

    def widgets_create(self):
        """Create all widgets in the main application window.
        """
        # configure resizing behavior
        top = self.winfo_toplevel()
        top.rowconfigure(1, weight=1)
        top.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        # create the widgets
        self.frm_question = FrameQuestion(self)
        self.frm_controls = FrameControls(self)
        self.frm_question.grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.frm_controls.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        self.parent.columnconfigure(0, weight=1)

        widgets.lblImage = tk.Label(self)
        widgets.lblImage.place(x=511, y=50, height=300, width=300)

class FrameControls(ttk.Frame):
    """Frame for the controls (buttons).
    """
    def __init__(self, parent, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        widgets.lblHeader = tk.Label(self, text='Topic:\n???',
                                     font=font.Font(family="Verdana", size=12),
                                     bg="#6FD2F4", height=4, width=12)
        widgets.lblHeader.pack(fill=tk.Y, padx=10, pady=10, expand=True)
        btnpadding = dict(padx=10, pady=5)
        ttk.Button(self, underline=0, text="Check Answer",
                   command=save_answer).pack(**btnpadding)
        ttk.Button(self, underline=0, text="Next",
                   command=move_next).pack(**btnpadding)
        ttk.Button(self, underline=0, text="Previous",
                   command=move_previous).pack(**btnpadding)
        ttk.Button(self, underline=0, text="Random",
                   command=move_random).pack(**btnpadding)
        ttk.Button(self, underline=0, text="Score",
                   command=display_score).pack(**btnpadding)
        ttk.Button(self, underline=0, text="Topic",
                   command=lambda: select_topic(gui=True)).pack(**btnpadding)
        ttk.Button(self, underline=0, text="Help",
                   command=display_help).pack(**btnpadding)


class FrameQuestion(ttk.Frame):
    """Frame for the question, answers, and explanation.
    """
    def __init__(self, parent, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        widgets.txtQuestion = tk.Text(self, height=2, border=0,
                                      font=font.Font(family="Verdana", size=12))
        widgets.txtQuestion.pack(anchor=tk.W, padx=5, pady=5, expand=tk.Y)
        widgets.txtQuestion.config(state="disabled")

        widgets.answerSelection = tk.StringVar()
        # create a frame to be used for hiding/showing radiobuttons
        widgets.rbframe = tk.Frame(self)
        widgets.rbframe.pack(side="top", fill="both", expand=True)

        rbops = dict(variable=widgets.answerSelection, underline=0)
        packoptions = dict(in_=widgets.rbframe, anchor=tk.W, padx=15, pady=17)
        widgets.answer1 = ttk.Radiobutton(self, value='1', text="1:", **rbops)
        widgets.answer1.pack(**packoptions)
        widgets.answer2 = ttk.Radiobutton(self, value='2', text="2:", **rbops)
        widgets.answer2.pack(**packoptions)
        widgets.answer3 = ttk.Radiobutton(self, value='3', text="3:", **rbops)
        widgets.answer3.pack(**packoptions)
        widgets.answer4 = ttk.Radiobutton(self, value='4', text="4:", **rbops)
        widgets.answer4.pack(**packoptions)
        widgets.answer5 = ttk.Radiobutton(self, value='5', text="5:", **rbops)
        widgets.answer5.pack(**packoptions)
        widgets.txtCorrect = tk.Text(self, border=0, height=2,
                                     font=('Verdana', 12))
        widgets.txtCorrect.pack(anchor=tk.W, padx=5, pady=8, expand=tk.Y)
        widgets.txtCorrect.config(state="disabled")
        widgets.txtExplanation = tk.Text(
            self, height=2, border=0, font=font.Font(family="Verdana", size=12))
        widgets.txtExplanation.pack(anchor=tk.W, padx=5, pady=5, expand=tk.Y)


# if running standalone, launch the app
if __name__ == "__main__":

    pythonw_setup()
    filename = select_topic(gui=False) # pylint: disable=C0103
    if not filename:
        sys.exit(0)
    read_datafile() # read in the selected data file

    root = tk.Tk() # pylint: disable=C0103
    MainApplication(root)
    root.minsize(width=900, height=400)
    root.resizable(width=False, height=False) # app window not resizable
    root.attributes("-topmost", True) # force app window to top
    root.attributes("-topmost", False)
    root.focus_force() # give app window focus
    center_window(root)
    root.mainloop()
