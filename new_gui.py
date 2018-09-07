import tkinter
from tkinter import font
import boggle



class Board_Frame(tkinter.Frame): #make to inherit from board
    
    def __init__(self, master = None, cnf = {}, **kw):
        self.master = master
        tkinter.Frame.__init__(self, cnf, **kw)
        self.active = []
        self.cells = []
        self.set_board()


    def set_board(self):
        self.cells = []
        for r, i in enumerate(self.master.game.gamestate.cells):
            self.cells.append([])
            for c, j in enumerate(i):
                self.cells[r].append(tkinter.Label(self, text = j, **self.master.prefs['cell_settings']))
                self.cells[r][c].config(**self.master.prefs['board_display']['normal'])
                self.cells[r][c].grid(row = r, column = c)

    def highlight(self, target = []):
        
        #remove existing highlighting
        if self.active:
            for i in self.active:
                self.cells[i[0]][i[1]].config(**self.master.prefs['board_display']['normal'])

        self.active = target or []

        #apply highlighting
        for i in self.active:
            self.cells[i[0]][i[1]].config(**self.master.prefs['board_display']['highlight'])

    def update_display(self, mode):
        for r in self.cells:
            for c in r:
                c.config(**self.master.prefs['board_display'][mode])


class Search_Frame(tkinter.Frame):
    
    #def __init__(self, game, board_frame, score_frame, master = None, cnf = {}, **kw):
    def __init__(self, master = None, cnf = {}, **kw):
        self.master = master
        self.game = master.game
        self.board_frame = master.board_frame
        self.score_frame = master.score_frame
        
        playercount = len(self.game.players)
        
        tkinter.Frame.__init__(self, cnf, **kw)

        tkinter.Label(self, text = 'Word', **self.master.prefs['UI_display']
                      ).grid(row=0,column=0)
        self.search_entry = tkinter.Entry(self, **self.master.prefs['UI_display'])
        self.search_entry.grid(row=0, column=1, columnspan=playercount -1 or 1, sticky='ew')
        tkinter.Button(self, text = "go", command = self.search_button, **self.master.prefs['UI_display'],
                       ).grid(row=0, column=playercount, sticky='e')

        #active player selection
        self.player_buttons = []
        self.active_player = tkinter.IntVar(value=0)
        for x,i in enumerate(self.game.players):
            self.player_buttons.append(tkinter.Radiobutton(self,
                                                           text = i['name'],
                                                           variable = self.active_player,
                                                           **self.master.prefs['UI_display'],
                                                           indicatoron = False,
                                                           value = x))           
            self.player_buttons[x].grid(row=1,column=x)
        #event handling
        self.search_entry.bind("<Return>", lambda x: self.search_button())


    def search_button(self):
        text = self.search_entry.get()

        self.game.make_move(text, self.active_player.get())
        try:
            coords = self.game.words[text]['coords']
        except Exception:
            coords = []
        self.board_frame.highlight(coords)
        self.score_frame.update_display()
        #highlight word so it can be re-written
        self.search_entry.selection_range(0, tkinter.END)


class Score_Frame(tkinter.Frame): #make inherit from game
    
    def __init__(self, master = None, cnf = {}, **kw):
        tkinter.Frame.__init__(self, cnf, **kw)
        self.game = master.game
        
        self.excluded_score = tkinter.IntVar()
        self.scores = []
        for i in self.game.players:
            self.scores.append(tkinter.IntVar(value=0))

        ex_name = tkinter.Label(self, text='Excluded',
                                fg = 'red', **self.master.prefs['UI_display'])
        ex_name.grid(row = 0, column = 0, columnspan = 2)
        ex_score = tkinter.Label(self, textvariable=self.excluded_score,
                                 fg = 'red', **self.master.prefs['UI_display'])
        ex_score.grid(row = 1, column = 0, columnspan = 2)
        
        for i,j in enumerate(self.game.players):
            col = (i+1) * 2
            
            p_name = tkinter.Label(self, text=j['name'], **self.master.prefs['UI_display'])
            p_name.grid(row=0, column=col)

            p_score = tkinter.Label(self, textvariable=self.scores[i],
                                    **self.master.prefs['UI_display'])
            p_score.grid(row = 1, column = col, columnspan = 2)

    def update_display(self):
        
        # update scores
        self.excluded_score.set(len([i for i in self.game.words if self.game.words[i]['player'] == 'Excluded']))
        for i in range(len(self.game.players)):
            self.scores[i].set(self.game.players[i]['score'])

        # build button if no button exists
        for i in self.game.words:
            if self.game.words[i].get('button'):
                pass
            else:
                self.game.words[i]['label'] = tkinter.Label(self, text = i, **self.master.prefs['UI_display'])
                self.game.words[i]['button'] = tkinter.Button(self, text = 'X',
                                                         command = lambda y = i: self.remove_button(y))

        # sort the word lists, set row to resultant sort, place items in grid
        for player in ['Excluded', *range(len(self.game.players))]:
            #Until excluded is fixed workaround is needed
            col = 0 if player == 'Excluded' else (player + 1) * 2

            words = sorted([x for x in self.game.words if self.game.words[x]['player'] == player])
            [self.game.words[i]['label'].grid(row = 2 + x, column = col) for x, i in enumerate(words)]
            [self.game.words[i]['button'].grid(row = 2 + x, column = col+1) for x, i in enumerate(words)]

    def remove_button(self, word):
        self.game.words[word]['label'].grid_forget()
        self.game.words[word]['button'].grid_forget()
        self.game.remove_word(word)
        self.update_display()


class Control_Frame(tkinter.Frame):
    
    def __init__(self, master = None, cnf = {}, **kw):
        tkinter.Frame.__init__(self, cnf, **kw)
        self.master = master

        #initialise buttons
        view_frame = tkinter.Frame(self, relief='ridge')
        tkinter.Button(self, text="Show/Hide board", command = master.show_hide).grid(row=0,column=0)
        view_frame.grid(row = 0, column = 1)
        tkinter.Button(view_frame, text="Game View", command = master.game_display).grid(row = 0, column = 0)
        tkinter.Button(view_frame, text="Score View", command = master.score_display).grid(row = 0, column = 1)


class Timer_Frame(tkinter.Frame):
    
    def __init__(self, master = None, cnf = {}, **kw):
        tkinter.Frame.__init__(self, cnf, **kw)


class BigBoard(tkinter.Tk):

    prefs = {}
    hidden = False   

    def __init__(self):
        tkinter.Tk.__init__(self)
        
        self.game = boggle.Game()

        self.prefs_init()
        
        self.board_frame = Board_Frame(self, relief = 'ridge', borderwidth = 2)
        self.score_frame = Score_Frame(self, relief = 'ridge', borderwidth = 2)
        self.timer_frame = tkinter.Frame(self, relief = 'ridge', borderwidth = 2)
        self.control_frame = Control_Frame(self, self, relief = 'ridge', borderwidth = 2)
        self.search_frame = Search_Frame(self, relief = 'ridge', borderwidth = 2)

        #self.menu_init()
        self.display_init()

        self.cover = tkinter.Frame(self, background = 'grey')
        
        self.game_display()

    def prefs_init(self):
        self.prefs = {'cell_settings':   {'bg':      'white',
                                         'relief':  'ridge',
                                         'width':   2},
                                    #I think the font calculation would be better done dynamically
                     'board_display':   {'game_display':    {'font':font.Font(size = 90)},
                                         'score_display':   {'font':font.Font(size = 50)},
                                         'normal':  {'bg':  'white'},
                                         'highlight':{'bg': 'yellow'}},
                     'UI_display':      {'font':    font.Font(size = 22)}}

    def menu_init(self):

        self.menu_bar = tkinter.Menu(self)

        self.game_menu = tkinter.Menu(self.menu_bar)
        self.game_menu.add_command(label="New game", command=self.new_game)
        self.game_menu.add_command(label="Preferences", command=self.display_pref_window)
        self.menu_bar.add_cascade(label="Game", menu = self.game_menu)
                
        self.view_menu = tkinter.Menu(self.menu_bar)
        self.view_menu.add_command(label="Search window", command=self.display_search_window)
        self.view_menu.add_command(label="Score window", command=self.display_score_window)
        self.menu_bar.add_cascade(label="View", menu = self.view_menu)

        self.board_window.config(menu=self.menu_bar)

    def display_init(self):

        #self.board_frame.set_board(self.game.gamestate.cells)
        tkinter.Label(self.timer_frame, text = "timer").pack()

    def clear_display(self):
        """reset the root window"""
        self.board_frame.grid_forget()
        self.search_frame.grid_forget()
        self.score_frame.grid_forget()
        self.timer_frame.grid_forget()
        self.control_frame.grid_forget()
        
    def score_display(self):
        """change the display for scoring mode"""
        self.clear_display()
        
        self.search_frame.grid(row = 0, column = 0, sticky = "NESW")
        self.score_frame.grid(row = 0, column = 1, sticky = "NESW", rowspan = 2)
        self.board_frame.grid(row = 1, column = 0, sticky = "NESW")
        self.control_frame.grid(row = 2, column = 0, sticky = "NESW", columnspan = 2)

        self.board_frame.update_display('score_display')

    def game_display(self):
        self.clear_display()

        self.board_frame.grid(row = 1, column = 0)
        self.timer_frame.grid(row = 1, column = 1)
        self.control_frame.grid(row = 2, column = 0, columnspan = 2)

        self.board_frame.update_display('game_display')

    def show_hide(self):
        if self.hidden == False:
            self.hidden = True
            self.cover.grid(row=        self.board_frame.grid_info()['row'],
                            column=     self.board_frame.grid_info()['column'],
                            sticky =    'NESW')
        else:
            self.hidden = False
            self.cover.grid_forget()
