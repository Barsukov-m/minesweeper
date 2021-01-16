# MINESWEEPER game
# by Michael Barsukov

from tkinter import *
from tkinter import messagebox as msg
from os import listdir, remove
from random import randint

IMAGES_PATH = 'sprites/'

# Modes
NOVICE = (9, 9, 10)
NORMAL = (16, 16, 40)
HARD = (16, 30, 90)

# Rating coefficients
NOVICE_COEF = 1
NORMAL_COEF = 5
HARD_COEF = 10


class Player:  # Rating entry
    def __init__(self, master, number, name):
        self.name = name[:-1]
        self.player = Radiobutton(master, variable=pl_var, value=number,
                                  command=lambda: show_stats(self.name),
                                  text=self.name)
        self.player.pack(anchor=W, pady=3, padx=5)


class Cell:  # Field
    def __init__(self, master, x, y):
        """
            Initialize a cell on given field and chords
        """
        self.hidden = True
        self.flag_state = 0
        self.value = solution[x][y]

        self.cell = Button(master, padx=5, pady=1, bd=2,
                           text='  ', font='Arial 14 bold',
                           command=(lambda x=x, y=y: self.reveal(x, y)))
        self.cell.grid(row=x, column=y)

        # On click
        self.cell.bind('<Button-1>', lambda event: set_face(1))
        self.cell.bind('<ButtonRelease-1>', lambda event: set_face(0))
        self.cell.bind('<Button-3>', self.flag)

    def flag(self, event):
        if self.hidden:
            if self.flag_state == 0:
                self.cell.configure(image=flag_img, width=20, height=23)
                self.flag_state = 1
                mines_found['text'] += 1
            elif self.flag_state == 1:
                self.cell.configure(image='', text='?', fg='#000',
                                    activeforeground='#000', width=1, height=1)
                self.flag_state = 2
                mines_found['text'] -= 1
            else:
                self.cell.configure(image='', text='', width=1, height=1)
                self.flag_state = 0

    def colorize(self):
        colors = ['#0000FD', '#007E00', '#FF0000', '#000080',
                  '#800000', '#000000', '#808080', '#808080']
        for i in range(7):
            if self.value == i+1:
                self.cell['fg'] = colors[i]
                self.cell['activeforeground'] = colors[i]

    def reveal(self, x, y, clicked=True, reveal_all=False):
        """
            X, Y - coordinates of the cell to be revealed.
            CLICKED - when True, function is supposed to be called
            by clicking a cell, otherwise called by another function.
            REVEAL_ALL - cells are opened up when gets True.
        """
        global firstclick

        # Generate a new field when first click reveals a bomb
        while solution[x][y] == '*' and firstclick:
            reset(mode, False)
        firstclick = False

        if self.flag_state:
            self.flag(0)
        self.colorize()

        # Cell disabling
        cell = field[x][y].cell
        cell['relief'] = SUNKEN
        field[x][y].hidden = False
        cell.unbind('<Button-1>')
        cell.unbind('<ButtonRelease-1>')
        cell.unbind('<Button-3>')
        cell['command'] = ''

        if field[x][y].value != '*' and not reveal_all:
            win_check()

        if self.value == '*':  # Bomb image
            cell.configure(image=mine_img, width=20, height=23)
            if clicked:
                cell['bg'] = 'red'
                game_over()
                return
        elif self.value != 0:
            cell['text'] = self.value
            return

        # FloodFill
        if solution[x][y] == 0 and not reveal_all:
            for i in range(x-1, x+2):
                for j in range(y-1, y+2):
                    if i >= 0 and i < field_rows\
                              and j >= 0 and j < field_cols:
                        if field[i][j].hidden:
                            field[i][j].reveal(i, j, False)


def win_check():
    global win_rate

    for i in range(field_rows):
        for j in range(field_cols):
            if solution[i][j] == '*' and not field[i][j].hidden\
                    or solution[i][j] != '*' and field[i][j].hidden:
                return 0

    # Win if passed
    for r in range(field_rows):
        for c in range(field_cols):
            field[r][c].reveal(r, c, False, True)
    set_face(3)

    # Evaluating player stats
    if mode == NORMAL:
        win_rate += NORMAL_COEF
        game = 'Normal - Win'
    elif mode == HARD:
        win_rate += HARD_COEF
        game = 'Hard - Win'
    else:
        win_rate += NOVICE_COEF
        game = 'Novice - Win'

    if username:
        user_file = username.lower()+'.data'
        with open(user_file) as f:
            data = f.readlines()
        with open(user_file, 'w') as f:
            try:
                data = data[:4] + [game+'\n'] + data[4:]
                del data[14:]
            except IndexError:
                pass
            for line in data:
                f.write(line)
        stats_update()

    msg.showinfo('Congratulations!', "You have won the game!")


def place_mine(array):
    row = len(array)
    col = len(array[0])
    x = randint(0, row-1)
    y = randint(0, col-1)

    if array[x][y] == '*':
        place_mine(array)
    array[x][y] = '*'


def number(arrray, i, j):
    if arrray[i][j]:  # Something is already placed
        return
    n = 0
    # Looking for a mine around the cell
    for r in range(i-1, i+2):
        # The previous and the next row (column) index
        for c in range(j-1, j+2):
            # Out of range check
            if (r >= 0 and c >= 0) and (r < field_rows and c < field_cols):
                if arrray[r][c] == '*':
                    n += 1
    arrray[i][j] = n


def solution_gen(user_mode):
    # Creating the solution grid
    G = [[0 for j in range(field_cols)] for i in range(field_rows)]

    # Filling up with mines
    for i in range(field_mines):
        place_mine(G)

    # Updating the cells
    for i in range(field_rows):
        for j in range(field_cols):
            number(G, i, j)

    return G


def field_gen(master, r, c):
    return [[Cell(cell_grid, i, j) for j in range(c)] for i in range(r)]


def game_over():
    global win_rate

    for r in range(field_rows):
        for c in range(field_cols):
            field[r][c].reveal(r, c, False, True)
    set_face(2)

    if mode == NORMAL:
        game = 'Normal - Lose'
    elif mode == HARD:
        game = 'Hard - Lose'
    else:
        game = 'Novice - Lose'
    win_rate -= 1
    if win_rate < 0:  # Win rate should not be negative
        win_rate = 0

    if username:
        user_file = username.lower()+'.data'
        with open(user_file) as f:
            data = f.readlines()
        with open(user_file, 'w') as f:
            try:
                data = data[:4] + [game+'\n'] + data[4:]
                del data[14:]
            except IndexError:
                pass
            for line in data:
                f.write(line)
        stats_update()

    askretry = msg.askretrycancel('Game over', 'You lose!')
    if askretry:
        reset(mode)
    else:
        root.destroy()


def reset(user_mode, update=True, load=False):
    global solution, field, firstclick, mode
    global field_rows, field_cols, field_mines

    field_rows, field_cols, field_mines = user_mode
    firstclick = True
    mines_found['text'] = 0
    mines_left['text'] = field_mines
    mode = user_mode

    if not load:
        solution = solution_gen(mode)
    if update:
        # Removing cells from the screen
        for i in range(len(field)):
            for j in range(len(field[0])):
                field[i][j].cell.destroy()
        field = field_gen(cell_grid, field_rows, field_cols)
    set_face(0)
    for i in range(field_rows):
        for j in range(field_cols):
            field[i][j].value = solution[i][j]


def set_face(image):
    face_btn['image'] = face_default if image == 0\
            else face_surprise if image == 1\
            else face_lose if image == 2\
            else face_win


# Authentication
def login():
    global username, win_rate
    username = username_field.get()
    password = password_field.get()
    user_file = username.lower() + '.data'

    # User data is saved in the directory
    if user_file in listdir():
        with open(user_file) as userdata:
            data = userdata.readlines()
        if not data:  # File is empty
            msg.showerror('Error!', 'User data is missing. Please try again')
            remove(user_file)
            return
        elif (data[1] == password) or (data[1] == password+'\n'):
            msg.showinfo('Greeting!', 'Welcome back, %s!' % username)
            if len(data) > 3:  # Fetch win rate of the user
                win_rate = data[3]
        else:
            msg.showerror('Error!', 'Incorrect password. Please try again')
            return
    elif username:  # Username is not empty
        with open(user_file, 'w') as userdata:
            # Login, password, saved game, win rate
            data = username + '\n' + password + '\n\n0\n'
            userdata.write(data)  # Save login info
        msg.showinfo('Successful!', 'Your login data has been added.')
    else:
        msg.showinfo('Warning!', 'You are logged in as Anonymous.')

    auth.destroy()  # Close the login window


def save_game(username):
    global solution

    # List encryption
    solution_enc = str(solution)
    solution_enc = list(bytearray([ord(i) for i in solution_enc]))

    user_file = username.lower() + '.data'
    with open(user_file) as f:  # Save the file data
        data = f.readlines()

    with open(user_file, 'w') as f:
        try:  # Searching for lines below user login data
            if '[' in data[2]:  # Saved field data is on the third line
                askoverwrite = msg.askyesno('Saved game found',
                                            'Would you like to overwrite\
                                            your saved data?')
                if askoverwrite:
                    data[2] = str(solution_enc)+'\n'
                else:
                    for line in data:
                        f.write(line)
                    return
            else:  # No saved field data
                data[2] = str(solution_enc)+'\n'
            for line in data:
                f.write(line)
        except IndexError:
            f.write
            f.write(data[0] + data[1] + str(solution_enc))
        msg.showinfo('Success!',
                     'The current game is saved for %s' % username)


def load_game(username):
    global solution, mode

    user_file = username.lower() + '.data'
    with open(user_file) as f:
        data = f.readlines()
    try:
        saved_game = eval(data[2])
        if not saved_game:  # No saved games
            raise Exception
        else:  # Decrypt the solution list
            saved_game = bytes(saved_game).decode('utf-8')

        mines = 0
        for r in saved_game:
            for c in r:
                if c == '*':
                    mines += 1
        mode = NORMAL if mines == NORMAL[2]\
            else HARD if mines == HARD[2]\
            else NOVICE

        if mines:
            solution = eval(saved_game)
        else:
            raise Exception
    except IndexError:
        msg.showinfo('Something went wrong',
                     'No saved games found for the current user')
        return

    reset(mode, True, True)
    msg.showinfo('Success!', 'The game is loaded for %s' % username)


def rating():
    global pl_var, rating, player_names, stats
    rating = Tk()
    rating.title('Rating')
    rating.minsize(300, 200)
    rating.maxsize(700, 450)

    pl_var = BooleanVar()
    pl_var.set(1)

    stats = Frame(rating)
    player_list = Frame(stats)

    # Should be sorted by rating later
    player_names = []
    for i in listdir():
        if '.data' in i:
            with open(i) as f:
                # if data[3]:
                data = f.readlines()
            if not data:  # User data is missing
                continue
            player_names.append(data[0])

    stats.pack(expand=1)
    player_list.pack(expand=1, side=LEFT, pady=30)
    for i, p in enumerate(player_names):
        Player(player_list, i+1, p)

    rating.mainloop()


def show_stats(username):
    global stats, stats_list
    try:  # Remove stats when selecting another player
        stats_list.destroy()
    except NameError:
        pass
    stats_list = Frame(stats)

    user_file = username.lower()+'.data'
    with open(user_file) as f:
        data = f.readlines()
    username = username + ' (%s)' % data[3][:-1]
    user_label = Label(stats_list, text=username, font='14')

    stats.pack(expand=1, pady=30)
    stats_list.pack(expand=1, side=RIGHT, padx=30)
    user_label.pack(pady=10)

    with open(user_file) as f:
        data = f.readlines()
        try:
            if data[4]:
                for i in range(4, len(data)):
                    game_entry = Label(stats_list, text='%d. %s' %
                                       (i-3, data[i]))
                    game_entry.pack(anchor=W)
        except IndexError:
            Label(stats_list, text='No games found', font='italic').pack()


def stats_update():
    if username:
        user_file = username.lower()+'.data'
        with open(user_file) as f:
            data = f.readlines()
        try:
            data[3] = str(win_rate)+'\n'
            with open(user_file, 'w') as f:
                for line in data:
                    f.write(line)
        except IndexError:
            pass


# User authentication
auth = Tk()
auth.title('Authentication')
auth.minsize(200, 150)
auth.maxsize(400, 250)

username = ''
auth_container = Frame(auth)
label_1 = Label(auth_container, text='Username:')
label_2 = Label(auth_container, text='Password:')
username_field = Entry(auth_container)
password_field = Entry(auth_container, show='*')
btn_login = Button(auth_container, text='Login', padx=20, pady=5,
                   command=login)

auth_container.pack(expand=1, fill=X)
label_1.pack()
username_field.pack()
label_2.pack()
password_field.pack()
btn_login.pack(pady=5)

auth.mainloop()


# User rating
field_rows = NOVICE[0]
field_cols = NOVICE[1]
field_mines = NOVICE[2]
mode = NOVICE
win_rate = 0

root = Tk()
root.title('Minesweeper Game')
root.resizable(0, 0)

# Images
face_default = PhotoImage(file=IMAGES_PATH + '1.png')
face_surprise = PhotoImage(file=IMAGES_PATH + '2.png')
face_lose = PhotoImage(file=IMAGES_PATH + '3.png')
face_win = PhotoImage(file=IMAGES_PATH + '4.png')
mine_img = PhotoImage(file=IMAGES_PATH + 'bomb.png').subsample(2, 2)
flag_img = PhotoImage(file=IMAGES_PATH + 'flag.png').subsample(2, 2)

# GUI
main_menu = Menu(root)
root.config(menu=main_menu)
file_menu = Menu(main_menu, tearoff=0)
if username:
    file_menu.add_command(label='Save', command=lambda: save_game(username))
    file_menu.add_command(label='Load', command=lambda: load_game(username))
else:
    file_menu.add_command(label='Save', command=lambda:
                          msg.showerror('Error!', 'You are not logged in'))
    file_menu.add_command(label='Load', command=lambda:
                          msg.showerror('Error!', 'You are not logged in'))
file_menu.add_command(label='Rating', command=rating)

mode_menu = Menu(main_menu, tearoff=0)
mode_menu.add_command(label='Novice',
                      command=(lambda: reset(NOVICE)))
mode_menu.add_command(label='Normal',
                      command=(lambda: reset(NORMAL)))
mode_menu.add_command(label='Hard',
                      command=(lambda: reset(HARD)))

main_menu.add_cascade(label='File', menu=file_menu)
main_menu.add_cascade(label='Mode', menu=mode_menu)

master = Frame(root, borderwidth=3, relief='sunken')
status = Frame(master, pady=10)
cell_grid = Frame(master)

# Field generation
solution = solution_gen(mode)
field = field_gen(cell_grid, field_rows, field_cols)
firstclick = True

# Status
face_btn = Button(status, image=face_default, padx=6, pady=5, bd=2)
face_btn.bind('<Button-1>',
              lambda event: reset(mode))
mines_left = Label(status, text=field_mines, font='mono 18',
                   width=3, pady=6, borderwidth=3, relief='sunken')
mines_found = Label(status, text=0, font='mono 18',
                    width=3, pady=6, borderwidth=3, relief='sunken')

# Display
master.pack(padx=50, pady=25, expand=1)
status.grid(row=0)
mines_left.grid(row=0, column=1)
face_btn.grid(row=0, column=2, padx=field_cols*4)
mines_found.grid(row=0, column=3)
cell_grid.grid(row=1)


root.mainloop()
