from boggle import *

import tkinter
from tkinter import font
from tkinter import messagebox

class GuiGame (Game): # may separate these into different classes for each window

    board_window = tkinter.Tk()
    board_window.withdraw()
    search_entry = tkinter.Entry()
    
    cells = [] # may be duplicating the work of gamestate...refactor later

    prefs = {'board_bg'     : 'white',
             'board_hl'     : 'yellow',
             'board_font'   : font.Font(size = 64),
             'disp_font'    : font.Font(size = 22)
             }
    
    cell_settings = {'bg'       : 'white',
                     'relief'   : 'ridge',
                     'width'    : 2}
    
    active = set()          # words which have been highlighted


    def __init__(self, rows = 5, columns = 5, playercount = 2):
        (self.rows, self.columns, self.playercount) = (rows, columns, playercount)
        
        #initialise the parent class
        super().__init__(rows, columns, playercount)

        #initialise the players
        self.scores = []
        for i in self.players:
            self.scores.append(tkinter.IntVar(value=0))

        self.excluded_words = tkinter.StringVar()
        self.player_words = []
        self.excluded_score = tkinter.IntVar()
        
        for i in self.players:
            self.player_words.append(tkinter.StringVar())
        
        #board window -> move at least some to a function
        self.board_window.deiconify()

        self.menu_bar = tkinter.Menu(self.board_window)

        self.game_menu = tkinter.Menu(self.menu_bar)
        self.game_menu.add_command(label="New game", command=self.new_game)
        self.game_menu.add_command(label="Preferences", command=self.display_pref_window)
        self.menu_bar.add_cascade(label="Game", menu = self.game_menu)
                
        self.view_menu = tkinter.Menu(self.menu_bar)
        self.view_menu.add_command(label="Search window", command=self.display_search_window)
        self.view_menu.add_command(label="Score window", command=self.display_score_window)
        self.menu_bar.add_cascade(label="View", menu = self.view_menu)

        self.board_window.config(menu=self.menu_bar)

        # display the windows
        
        self.update_board_window()
        self.display_search_window() # show search window
        self.display_score_window() # show score window

##        #make sure the windows are not overlapping too much
##        ws = self.board_window.winfo_screenwidth() # width of the screen
##        hs = self.board_window.winfo_screenheight() # height of the screen
##        
##        board_geom = self.board_window.geometry().replace('x','+').split('+')
##        search_geom = self.search_window.geometry().replace('x','+').split('+')
##        score_geom = self.score_window.geometry().replace('x','+').split('+')
##
##        #print(board_geom, search_geom, score_geom)
##
##        board_geom[2] = 0
##        board_geom[3] = 0
##        self.board_window.geometry("{}x{}+{}+{}".format(*board_geom))
##
##        search_geom[2] = board_geom[0]
##        search_geom[3] = 0
##        self.search_window.geometry("{}x{}+{}+{}".format(*search_geom))
##        
##        score_geom[2] = board_geom[0]
##        score_geom[3] = search_geom[1]
##        self.score_window.geometry("{}x{}+{}+{}".format(*score_geom))


        #bring to the top
        self.board_window.attributes('-topmost', 1)
        self.board_window.attributes('-topmost', 0)

        #self.board_window.mainloop()


    def update_board_window(self):
        self.cells = []
        for r, i in enumerate(self.gamestate.cells):
            self.cells.append([])
            for c, j in enumerate(i):
                self.cells[r].append(tkinter.Label(self.board_window, text = j, **self.cell_settings))
                self.cells[r][c]['font'] = self.prefs['board_font']
                self.cells[r][c].grid(row = r, column = c)



    def display_search_window(self):
        """displays search window"""
        #does a search window exist?
        try:
            if self.search_window.winfo_exists() == 1:
                return
        except AttributeError:
            pass
        
        self.search_window = tkinter.Toplevel(self.board_window)

        #word searching
        tkinter.Label(self.search_window, text = 'Word', font = self.prefs['disp_font']).grid(row=0,column=0)
        self.search_entry = tkinter.Entry(self.search_window, font = self.prefs['disp_font'])
        self.search_entry.grid(row=0, column=1, columnspan=len(self.players)-1 or 1, sticky='ew')
        tkinter.Button(self.search_window, text = "go", command = self.search_button,
                       font = self.prefs['disp_font']).grid(row=0, column=len(self.players), sticky='e')

        #active player selection
        self.player_buttons = []
        self.active_player = tkinter.IntVar(value=0)
        for x,i in enumerate(self.players):
            self.player_buttons.append(tkinter.Radiobutton(self.search_window,
                                                           text = i['name'],
                                                           variable = self.active_player,
                                                           font = self.prefs['disp_font'],
                                                           indicatoron = False,
                                                           value = x))           
            self.player_buttons[x].grid(row=1,column=x)
        #event handling
        self.search_window.bind("<Return>", lambda x: self.search_button())


    def search_button(self):
        text = self.search_entry.get()

        self.make_move(text, self.active_player.get())
        try:
            coords = self.words[text]['coords']
        except Exception:
            coords = []
        self.highlight(coords)
        self.update_score_window()
        #highlight word so it can be re-written
        self.search_entry.selection_range(0, tkinter.END)

    def highlight(self, target = []):
        """display the board, highlighting specified cells"""
        
        #remove existing highlighting
        for i in self.active:
            self.cells[i[0]][i[1]].config(bg = self.prefs['board_bg'])

        self.active = target

        #apply highlighting
        for i in self.active:
            self.cells[i[0]][i[1]].config(bg = self.prefs['board_hl'])

    def display_score_window(self):
        """display the score window"""
        
        #does the score window exist?
        try:
            if self.score_window.winfo_exists() == 1:
                return
        except AttributeError:
            pass
        
        self.score_window = tkinter.Toplevel(self.board_window)

        #Player labels and scores
        ex_name = tkinter.Label(self.score_window, text='Excluded',
                                font = self.prefs['disp_font'], fg = 'red')
        ex_name.grid(row = 0, column = 0, columnspan = 2)
        ex_score = tkinter.Label(self.score_window, textvariable=self.excluded_score,
                                 font = self.prefs['disp_font'], fg = 'red')
        ex_score.grid(row = 1, column = 0, columnspan = 2)
        
        for i,j in enumerate(self.players):
            col = (i+1) * 2
            
            p_name = tkinter.Label(self.score_window, text=j['name'], font = self.prefs['disp_font'])
            p_name.grid(row=0, column=col)

            p_score = tkinter.Label(self.score_window, textvariable=self.scores[i],
                                    font = self.prefs['disp_font'])
            p_score.grid(row = 1, column = col, columnspan = 2)

    def update_score_window_old(self):

        #excludes
        excluded = [i for i in self.words if self.words[i]['player'] == 'Excluded']
        self.excluded_score.set(len(excluded))
        self.excluded_words.set('\n'.join(excluded))
        
        for i in range(len(self.players)):
            self.scores[i].set(self.players[i]['score'])

        #words used
        for i in range(len(self.players)):
            #self.player_words[i].set('\n'.join([i for i in self.words if self.words[i]['player'] == p]))
            self.player_words[i].set("\n".join([*filter(lambda y: self.words[y]['player']==i, self.words)]))

    def update_score_window(self):

        # update scores
        self.excluded_score.set(len([i for i in self.words if self.words[i]['player'] == 'Excluded']))
        for i in range(len(self.players)):
            self.scores[i].set(self.players[i]['score'])

        # build button if no button exists
        for i in self.words:
            if self.words[i].get('button'):
                pass
            else:
                self.words[i]['label'] = tkinter.Label(self.score_window, text = i, font = self.prefs['disp_font'])
                self.words[i]['button'] = tkinter.Button(self.score_window, text = 'X',
                                                         command = lambda y = i: self.remove_button(y))

        # sort the word lists, set row to resultant sort, place items in grid
        for player in ['Excluded', *range(len(self.players))]:
            #Until excluded is fixed workaround is needed
            col = 0 if player == 'Excluded' else (player + 1) * 2

            words = sorted([x for x in self.words if self.words[x]['player'] == player])
            [self.words[i]['label'].grid(row = 2 + x, column = col) for x, i in enumerate(words)]
            [self.words[i]['button'].grid(row = 2 + x, column = col+1) for x, i in enumerate(words)]

    def remove_button(self, word):
        self.words[word]['label'].grid_forget()
        self.words[word]['button'].grid_forget()
        self.remove_word(word)
        self.update_score_window()
        

    def display_pref_window(self):
        """display the preference window"""

        #needs work on validation
        
        #does the score window exist?
        try:
            if self.pref_window.winfo_exists() == 1:
                return
        except AttributeError:
            pass

        self.pref_window = tkinter.Toplevel(self.board_window)
        board_size_entry = tkinter.Entry(self.pref_window)
        board_size_entry.insert(0, self.prefs['board_font']['size'])
        board_size_entry.grid(row=0, column=0)
        tkinter.Label(self.pref_window, text = "Board font size").grid(row=0, column = 1)
        
        disp_size_entry = tkinter.Entry(self.pref_window)
        disp_size_entry.grid(row=1, column=0)
        disp_size_entry.insert(0, self.prefs['disp_font']['size'])
        tkinter.Label(self.pref_window, text = "Display font size").grid(row=1, column = 1)
        

        tkinter.Button(self.pref_window, text="Apply",
                       command=lambda: self.set_prefs(board_size = board_size_entry.get(),
                                                      disp_size = disp_size_entry.get())
                       ).grid(row = 2, column = 1)
        self.pref_window.bind("<Return>", lambda x: self.set_prefs(board_size = board_size_entry.get(),
                                                      disp_size = disp_size_entry.get()))

    def set_prefs(self, board_size, disp_size):
        self.prefs['board_font']['size'] = int(board_size)
        self.prefs['disp_font']['size'] = int(disp_size)

    def new_game(self):
        # Not happy with this implementation, but it works
        self.score_window.destroy()
        self.search_window.destroy()
        self.__init__(rows = self.rows, columns = self.columns, playercount = self.playercount)


class NewGame:
    row = 0
    col = 0
    
    def __init__(self):
        self.new_game()

    def new_game(self):
        top = self.top = tkinter.Toplevel()
        
        tkinter.Label(top, text="columns").pack()
        self.columns = tkinter.Entry(top)
        self.columns.pack()

        tkinter.Label(top, text="rows").pack()
        self.rows = tkinter.Entry(top)
        self.rows.pack()

        tkinter.Label(top, text="players").pack()
        self.players = tkinter.Entry(top)
        self.players.pack()

        b = tkinter.Button(top, text="New Game", command=self.new_ok)
        b.pack()

    def new_ok(self):
        #insert exception handling#

        try:
            self.col = int(self.columns.get())
            self.row = int(self.rows.get())
            self.player_count = int(self.players.get())

            assert self.col >= 1
            assert self.row >= 1
            assert self.player_count >= 1

            self.top.withdraw()
            self.game = GuiGame(self.row, self.col, self.player_count)
            
        except Exception:
            messagebox.showerror("Invalid values", "Values must be whole numbers equal or greater than one")


##if __name__ == '__main__':
##    GuiGame()
