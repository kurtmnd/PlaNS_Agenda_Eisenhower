# PlaNS

# Last update: 2020-05-16 22:51
# Running in Python 3.8.1
# http://github.com/kurtmnd
# Developed by N.S.

'''

TODO list:
- Automatic pausa
- Days of year in squares

Bugs:
- 

'''

############################# STATIC VARIABLES AND INITIALIZATION

PROGRAM_NAME_LONG = "PlaNS"
PROGRAM_NAME_SHORT = "PlaNS"

YEAR = 2020

CHAR_TO_REMOVE = ' ' # space, other option is *

HOUR_FIRST = 6
HOUR_LAST = 23

FILE_NAME_DATA_BASE = 'acts.csv'

WRAP_TEXT = 'none' # 'none' 'word"'

fft = 'Arial' # 'Ink Free' 'Arial'
ffs = 9

IDENT_1 = '_' # hour without actiities
IDENT_2 = '▪' # activities without hour

ww1 = 35 #35
ww2 = ww1
ww3 = ww1
hh = 44 #44

BG_W13 = "whitesmoke"
BG_W24 = "white"
BG_W5 = "whitesmoke"

# Variables for the Eisenhower Matrix

FONT_EISENHOWER = 'Arial 11 bold'

EH0 = 'black'
EH1 = 'orangered'
EH2 = 'blue'
EH3 = 'darkmagenta'
EH4 = 'green'

main_width = 600
main_height = 400
left_space = main_width/2

lastx = 0
lasty = 0

############################# IMPORT PYTHON LIBRARIES

from tkinter import *
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
import webbrowser
import os
import datetime

############################# IMPORT EXTERNAL LIBRARIES

# For Windows open C:\Windows\System32\cmd.exe as administrator

import PySimpleGUI as sg
import pandas as pd
import numpy as np
from natsort import index_natsorted, order_by_index

############################# SIMPLE BASIC METHODS

def log(s): print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S | ")+s)
def logError(e,s):
    log("")
    try: log("*** "+s+"\n\n"+str(e)+"\n")
    except:
        log("*** "+s+"\n\n")
        traceback.print_exc()

############################# MAIN METHODS

def insert_new_activity():
    global df, Day1, Day2, Today, Tomorrow
    #try:

    sg.theme('DefaultNoMoreNagging') # LightGreen3

    layout = [
    [
        sg.Frame(layout=
        [
            [
                sg.Radio('Yesterday', "RADIO2"),
                sg.Radio('Today', "RADIO2", default=True),
                sg.Radio('Tomorrow', "RADIO2"),
                sg.Text('Other:'),
                sg.InputText(size=(7, 1), tooltip='Format: D/M')
            ]
        ], title=''),
        
    ],
    [
        sg.Text('Brief description:'),
        sg.InputText(size=(36, 1))
    ],
    [
        sg.Text("Hour:", size=(4, 1)),
        sg.InputText(size=(7, 1), tooltip='Format: HHMM'),
        sg.Frame(layout=
        [
            [
                sg.Radio('Planned', "RADIO1"),
                sg.Radio('Done', "RADIO1", default=True),
                sg.Checkbox('Remove')
            ]
        ], title=''),
    ],
        [sg.Submit(), sg.Cancel()]
    ]

    window = sg.Window('Insert a new activity', layout)
    event, values = window.read()
    window.close()

    if event=="Submit" and values[4]!='':

        new_row = pd.DataFrame([[""] * df.shape[1]], columns=df.columns)

        # date

        date_on_form = ''
        if values[3]=='':
            if values[0]:
                yesterday = Today - datetime.timedelta(days=1)
                date_on_form = date_to_str1(yesterday)
            if values[1]:
                date_on_form = date_to_str1(Today)
            if values[2]:
                date_on_form = date_to_str1(Tomorrow)
        else:
            if values[3]==CHAR_TO_REMOVE:
                date_on_form = ''
            else:
                temp = values[3].split('/')
                date_on_form = str(YEAR)+'-'+nn(temp[1])+'-'+nn(temp[0])
        new_row.at[0, 'Date1'] = date_on_form

        # brief description

        new_row.at[0, 'BriefDesc'] = values[4]

        # hour

        if values[5] != '':
            hour_on_form = values[5][:2]+':'+values[5][2:]
        else:
            hour_on_form = '0'
        new_row.at[0, 'Hour1'] = hour_on_form

        # planned or done

        if values[6]: plan_done_on_form = 'Plan'
        if values[7]: plan_done_on_form = 'Done'
        new_row.at[0, 'PlanDone'] = plan_done_on_form

        delete_activity = False
        if values[8]:
            delete_activity = True
            df = df.drop(df[(df.Date1 == date_on_form) &
                        (df.BriefDesc == values[4]) &
                        (df.PlanDone == plan_done_on_form)].index)
            if values[3]==CHAR_TO_REMOVE: # remove activities without date
                df = df.drop(df[(df.Date1 != df.Date1) &
                    (df.BriefDesc == values[4])].index)

        # other
        
        new_row.at[0, 'Eisenhower'] = '0'

        if not delete_activity:
            df = pd.concat([df, new_row], ignore_index=True)

        df.to_csv(FILE_NAME_DATA_BASE, index=False)
        load_activities()

    #except Exception as e:
    #    logError(e,"It was not possible to insert the activity.")

def nn(s):
    if int(s)<10: return '0'+s
    else: return s

def move_among_days(moveForward):
    global Day1, Day2
    d = datetime.timedelta(days=1)
    if moveForward:
        Day1 += d 
        Day2 += d
    else:
        Day1 -= d 
        Day2 -= d
    load_activities()

def load_activities():
    global df, df5, len_df5, Day1, Day2, Today, index_for_eisenhower
    global HOUR_FIRST, HOUR_LAST, EH0,EH1,EH2,EH3,EH4

    color1 = "mediumaquamarine" # lightgreen  turquoise
    color2 = "white"
    if date_to_str2(Day1) == date_to_str2(Today):
        label_date1.configure(text="TODAY ( "+date_to_str2(Day1)+" )", bg=color1)
        label_date2.configure(text=date_to_str2(Day2), bg=color2)
    else:
        if date_to_str2(Day2) == date_to_str2(Today):
            label_date1.configure(text=date_to_str2(Day1), bg=color2)
            label_date2.configure(text="TODAY ( "+date_to_str2(Day2)+" )", bg=color1)
        else:
            label_date1.configure(text=date_to_str2(Day1), bg=color2)
            label_date2.configure(text=date_to_str2(Day2), bg=color2)

    st1.delete("1.0", END)
    st2.delete("1.0", END)
    st3.delete("1.0", END)
    st4.delete("1.0", END)
    st5.delete("1.0", END)

    st1.insert(INSERT,"PLANNED TASK")
    st2.insert(INSERT,"TASK DONE")
    st3.insert(INSERT,"PLANNED TASK")
    st4.insert(INSERT,"TASK DONE")
    st5.insert(INSERT,"PLANNED TASK")
    
    df = pd.read_csv(FILE_NAME_DATA_BASE)

    df1 = df.loc[(df['Date1'] == date_to_str1(Day1)) & (df['PlanDone'] == "Plan")]
    df2 = df.loc[(df['Date1'] == date_to_str1(Day1)) & (df['PlanDone'] == "Done")]
    df3 = df.loc[(df['Date1'] == date_to_str1(Day2)) & (df['PlanDone'] == "Plan")]
    df4 = df.loc[(df['Date1'] == date_to_str1(Day2)) & (df['PlanDone'] == "Done")]
    df5 = df.loc[df['Date1'].isnull()]

    index_for_eisenhower = []
    for i,x in df.iterrows():
        if x['Date1'] != x['Date1']:
            index_for_eisenhower.append(i)

    len_df5 = len(df5)

    all_df = [df1,df2,df3,df4,df5]
    all_st = [st1,st2,st3,st4,st5]

    ############################################### FIRST 4 TEXT FIELDS
    
    for k in range(5):
        # sorting by column avinf text (hour in the format HH:MM)
        all_df[k] = all_df[k].reindex(index=order_by_index(
            all_df[k].index, index_natsorted(all_df[k]['Hour1'], reverse=False)))

    for k in range(4):
        # append data into scrolled text fields
        for j in range(HOUR_FIRST, HOUR_LAST+1):
            s=IDENT_1
            for i,x in all_df[k].iterrows():
                h=int(x['Hour1'].split(':')[0])
                if j==h:
                    s = hour_to_str(x['Hour1'])+x['BriefDesc']
                    append_to(all_st[k],s)
            if s==IDENT_1: append_to(all_st[k],s)
        for l,y in all_df[k].iterrows():
            if y['Hour1']=='0':
                append_to(all_st[k],hour_to_str(y['Hour1'])+y['BriefDesc'])

    ############################################### 5 th. COLUMN

    all_df[4] = all_df[4].reindex(index=order_by_index(
            all_df[4].index, index_natsorted(all_df[4]['Eisenhower'], reverse=False)))

    for i,x in all_df[4].iterrows():
        append_with_tag(all_st[4],hour_to_str(x['Hour1'])+x['BriefDesc'],
                        str(x['Eisenhower']))

    all_st[4].tag_config('0', foreground=EH0)
    all_st[4].tag_config('1', foreground=EH1)
    all_st[4].tag_config('2', foreground=EH2)
    all_st[4].tag_config('3', foreground=EH3)
    all_st[4].tag_config('4', foreground=EH4)

def open_eisenhower_matrix():

    global win2, df5, leftspace, canvas_1, EH0,EH1,EH2,EH3,EH4
    
    win2 = Toplevel(root)
    win2.wm_title(PROGRAM_NAME_SHORT)
    win2.resizable(width=False, height=False)
    win2.winfo_toplevel().title("Eisenhower Matrix")

    canvas_1 = Canvas(win2, background="white",
                     width=main_width+left_space, height=main_height)

    left_canvas = Canvas(win2, background="#eee", width=1, height=400)
    left_canvas.pack(side="left", fill="x")
    canvas_1.pack(fill="both", expand=True)

    counter_eisenhower = [0,0,0,0,0]
    for item,x in df5.iterrows():
        cat = str(x['Eisenhower'])
        if cat=='0': 
            canvas_1.create_text(10, 40+counter_eisenhower[0],
                text=x['BriefDesc'], anchor='w', font=FONT_EISENHOWER, fill = EH0)
            counter_eisenhower[0] += 20
        if cat=='1': 
            canvas_1.create_text(10+left_space, 40+counter_eisenhower[1],
                text=x['BriefDesc'], anchor='w', font=FONT_EISENHOWER, fill = EH1)
            counter_eisenhower[1] += 20
        if cat=='2': 
            canvas_1.create_text(10+left_space,
                                 40+counter_eisenhower[2]+main_height/2,
                text=x['BriefDesc'], anchor='w', font=FONT_EISENHOWER, fill = EH2)
            counter_eisenhower[2] += 20
        if cat=='3': 
            canvas_1.create_text(10+left_space+main_width/2, 40+counter_eisenhower[3],
                text=x['BriefDesc'], anchor='w', font=FONT_EISENHOWER, fill = EH3)
            counter_eisenhower[3] += 20
        if cat=='4': 
            canvas_1.create_text(10+left_space+main_width/2,
                                 40+counter_eisenhower[4]+main_height/2,
                text=x['BriefDesc'], anchor='w', font=FONT_EISENHOWER, fill = EH4)
            counter_eisenhower[4] += 20

    canvas_1.update()
    w = canvas_1.winfo_width() - left_space
    h = canvas_1.winfo_height()

    canvas_1.update()
    w = canvas_1.winfo_width() - left_space
    h = canvas_1.winfo_height()

    create_label(10,15,"Uncategorized activities",EH0)
    create_label(left_space+10,15,"Important & Urgent: Do it now!",EH1)
    create_label(left_space+10,h/2+15,"Less Important & Urgent: Do it later",EH2)
    create_label(left_space+w/2+10,15,"Important & Not Urgent: Schedule",EH3)
    create_label(left_space+w/2+10,h/2+15,"Less Important & Not Urgent: Ignore",EH4)

    wl = 3 # tickness of lines

    #vertical lines
    canvas_1.create_line(left_space+w/2, 0, left_space+w/2, h, width= wl)
    canvas_1.create_line(left_space, 0, left_space, h, width= wl)
    canvas_1.create_line(left_space+w-wl, 0, left_space+w-wl, h, width= wl)

    #horizontal lines
    canvas_1.create_line(left_space+0, h/2, left_space+w, h/2, width= wl)
    canvas_1.create_line(left_space+0, wl, left_space+w, wl, width= wl)
    canvas_1.create_line(left_space+0, h-wl, left_space+w, h-wl, width= wl)

    win2.update()
    windowWidth = win2.winfo_reqwidth()
    windowHeight = win2.winfo_reqheight()
    positionRight = int(win2.winfo_screenwidth()/2 - windowWidth/2)
    positionDown = int(win2.winfo_screenheight()/2 - windowHeight/2)
    win2.geometry("+{}+{}".format(positionRight, positionDown))

    canvas_1.bind('<ButtonPress-1>', mouse_down)
    canvas_1.bind('<B1-Motion>', mouse_motion)
    canvas_1.bind('<ButtonRelease-1>', mouse_release)
    win2.bind('<Key-Escape>', close_win2)

def verify_ehm_category(x,y):
    global main_width, main_height, left_space
    cat = 0
    x0 = left_space
    w = main_width
    h = main_height
    if x>x0 and x<x0+w/2 and y<h/2: cat = 1
    if x>x0 and x<x0+w/2 and y>h/2: cat = 2
    if x>x0+w/2 and y<h/2: cat = 3
    if x>x0+w/2 and y>h/2: cat = 4
    return cat

def create_label(x,y,s,color):
    canvas_1.create_text(x, y, text=s, anchor="w", font='Arial 12', fill=color)

def append_to(st,value):
    st.insert(END,"\n\n"+str(value))

def append_with_tag(st,value, tag):
    st.insert(END,"\n\n"+str(value), tag)

def date_to_str1(date):
    return date.strftime("%Y-%m-%d")

def date_to_str2(date):
    return date.strftime("%A - %B, %d")+" th."

def hour_to_str(value):
    if value!=value: return ""
    else:
        if value=='0': return IDENT_2+' '
        else: return str(value)+" "

############################# CALLBACKS (GUI METHODS/EVENTS)
    
def b1_event(): # insert new activity
    insert_new_activity()
    
def link_event1(event): # link to web of about/author
    webbrowser.open_new(r"https://github.com/kurtmnd")

def on_closing(): # close
    '''
    if messagebox.askokcancel(PROGRAM_NAME_SHORT, "Do you want to quit?"):
        try:
            #messagebox.showinfo(PROGRAM_NAME_SHORT, "debug")
            ''
        except Exception as e: logError(e,"")
        root.destroy()
    '''
    root.destroy()
    
def key_event1(event):
    insert_new_activity()

def key_event2(event):
    move_among_days(False)

def key_event3(event):
    move_among_days(True)

def key_event4(event):
    open_eisenhower_matrix()

def close_win2(event):
    global win2
    win2.destroy()

def mouse_motion(event):
    global len_df5, lastx, lasty
    current = event.widget.find_withtag("current")
    if current:
        item_id = current[0]
        if item_id < len_df5 + 1:
            dx = event.x - lastx
            dy = event.y - lasty
            canvas_1.move(item_id, dx, dy)
    lastx = event.x
    lasty = event.y
   
def mouse_down(event):
    global lastx, lasty
    lastx = event.x
    lasty = event.y

def mouse_release(event):
    global df, len_df5, left_space, index_for_eisenhower
    current = event.widget.find_withtag("current")
    if current:
        item_id = current[0]-1
        if item_id < len_df5:
            cat = verify_ehm_category(event.x, event.y)
            df.at[index_for_eisenhower[item_id], 'Eisenhower'] = cat
            df.to_csv(FILE_NAME_DATA_BASE, index=False)
            load_activities()
            

############################# GRAPHICAL USER INTERFACE

root = Tk()
#root.wm_attributes("-topmost", 1) # always on top
root.wm_title(PROGRAM_NAME_SHORT)
root.resizable(width=False, height=False)
root.bind("<Key-Insert>", key_event1)
root.bind("<Key-Prior>", key_event2)
root.bind("<Key-Next>", key_event3)
root.bind("<Key-F3>", key_event4)
root.protocol("WM_DELETE_WINDOW", on_closing)

############# TOP BUTTONS
'''
b1 = Button(root, text="Insert a new activity", command=b1_event)
b1.config( height = 1, width = 40, bg="grey", fg="white");
b1.pack(side=TOP)
'''
############# CENTER

centralFrame = Frame(root)
centralFrame.pack(side=LEFT)

############# CENTER 1

centralFrame1 = Frame(centralFrame)
centralFrame1.pack(side=LEFT)

label_date1 = Label(centralFrame1, text="TODAY", width = 2*ww1+6, relief=RIDGE)
label_date1.pack(side=TOP)

st1 = ScrolledText(centralFrame1, width = ww1, height=hh, bg=BG_W13)
st1.pack(side=LEFT)
st1.configure(font=(fft, ffs), wrap=WRAP_TEXT)

st2 = ScrolledText(centralFrame1, width = ww1, height=hh, bg=BG_W24)
st2.pack(side=LEFT)
st2.configure(font=(fft, ffs), wrap=WRAP_TEXT)

############# CENTER 2

centralFrame2 = Frame(centralFrame)
centralFrame2.pack(side=LEFT)

label_date2 = Label(centralFrame2, text="TOMORROW", width = 2*ww1+6, relief=RIDGE)
label_date2.pack(side=TOP)

st3 = ScrolledText(centralFrame2, width = ww2, height=hh, bg=BG_W13)
st3.pack(side=LEFT)
st3.configure(font=(fft, ffs), wrap=WRAP_TEXT)

st4 = ScrolledText(centralFrame2, width = ww2, height=hh, bg=BG_W24)
st4.pack(side=LEFT)
st4.configure(font=(fft, ffs), wrap=WRAP_TEXT)

############# CENTER 3

centralFrame3 = Frame(centralFrame)
centralFrame3.pack(side=LEFT)

ld3 = Label(centralFrame3, text="OTHER", width = ww1+3, relief=RIDGE, bg=BG_W5).pack(side=TOP)

st5 = ScrolledText(centralFrame3, width = ww3, height=hh, bg=BG_W5)
st5.pack(side=LEFT)
st5.configure(font=(fft, ffs), wrap=WRAP_TEXT)

############# FOOTER
'''
footerFrame = Frame(root)
footerFrame.pack(side=BOTTOM, fill = X)

Label(footerFrame, text="Developed by:").pack(side=LEFT)

l4 = Label(footerFrame, text="github.com/kurtmnd", fg="blue", cursor="hand2")
l4.bind("<Button-1>", link_event1)
l4.pack(side=LEFT)
'''
############################# CENTER WINDOW

root.update()
windowWidth = root.winfo_reqwidth()
windowHeight = root.winfo_reqheight()
positionRight = int(root.winfo_screenwidth()/2 - windowWidth/2)
positionDown = int(root.winfo_screenheight()/2 - windowHeight/2)
root.geometry("+{}+{}".format(positionRight, positionDown))

############################# INITIAL ROUTINE

#try:

log(PROGRAM_NAME_LONG)

Today = datetime.date.today()
Tomorrow = Today + datetime.timedelta(days=1)

Day1 = datetime.date.today()
Day2 = Day1 + datetime.timedelta(days=1)

load_activities()
        
#except Exception as e:
#    logError(e,"Some problems in the initial routine.")

mainloop() # start the GUI
