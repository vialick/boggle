import random
from collections import OrderedDict
import tkinter
from tkinter import font
from tkinter import messagebox

debug = True

class Board:
    """A Boggle-style gameboard"""
    cells = []
    height = 0
    width = 0

    # scrabble distribution
    letter_dist = OrderedDict({ 'a':	0.090909091,
                                'b':	0.111111111,
                                'c':	0.131313131,
                                'd':	0.171717172,
                                'e':	0.303030303,
                                'f':	0.323232323,
                                'g':	0.353535354,
                                'h':	0.373737374,
                                'i':	0.464646465,
                                'j':	0.474747475,
                                'k':	0.484848485,
                                'l':	0.525252525,
                                'm':	0.545454545,
                                'n':	0.606060606,
                                'o':	0.686868687,
                                'p':	0.707070707,
                                'q':	0.717171717,
                                'r':	0.777777778,
                                's':	0.818181818,
                                't':	0.878787879,
                                'u':	0.919191919,
                                'v':	0.939393939,
                                'w':	0.95959596,
                                'x':	0.96969697,
                                'y':	0.98989899,
                                'z':	1})

    letter_dist_bkup = OrderedDict({ 'a': 	0.08167,
                                'b': 	0.09659,
                                'c': 	0.12441,
                                'd': 	0.16694,
                                'e': 	0.29396,
                                'f': 	0.31624,
                                'g': 	0.33639,
                                'h': 	0.39733,
                                'i': 	0.46699,
                                'j': 	0.46852,
                                'k': 	0.47624,
                                'l': 	0.51649,
                                'm': 	0.54055,
                                'n': 	0.60804,
                                'o': 	0.68311,
                                'p': 	0.7024,
                                'q': 	0.70335,
                                'r': 	0.76322,
                                's': 	0.82649,
                                't': 	0.91705,
                                'u': 	0.94463,
                                'v': 	0.95441,
                                'w': 	0.97801,
                                'x': 	0.97951,
                                'y': 	0.99925,
                                'z': 	1})
    # Data from http://www.oxfordmathcenter.com/drupal7/node/353
    # this could be made into a generator (or at least two tuples)

    def __init__(self, height=5, width=5):
        """initialise the board"""
        (self.height, self.width) = (height, width)
        self.set_board()

    def set_board(self):
        """The random-letter generator"""

        # This list comp is clunky as hell. Should probably go with nested for loops or similar
        # Main issue is random

        self.cells = [[i for i in random.choices(
            tuple(self.letter_dist.keys()), cum_weights=tuple(self.letter_dist.values()), k=self.width)]
                      for j in range(self.height)]

        # self.cells = [[str(i+j) for i in range(self.width)] for j in range(self.height)]

    def find_word(self, string):
        """search through the board for the target string. Call recursive search when
        first character found"""
        coords = []
        for i in range(self.height):
            for j in range(self.width):
                if self.cells[i][j] == string[0]:           # matches start of target string
                    coords = self.search(string, [[i, j]])   # recursive search
                    if coords:
                        return coords                # return coordinates of match if a match is found
        return False

    def search(self, string, coords):
        """Return list of coordinates of matching search"""

        # check if the cell has the required character
        if self.cells[coords[-1][0]][coords[-1][1]] != string[0]:
            return False
        elif len(string) == 1:                              # final character matched
            return coords

        for i in self.get_adjacent(coords[-1]):             # find adjacent cells
            if i not in coords:                             # that have not been used already
                tmp = self.search(string[1:], coords + [i])
                if tmp: return tmp                          # tmp only true if a match has been found
        return False

    def get_adjacent(self, cell):
        """return list of cells adjacent to target"""
        targets = [[cell[0] + i[0], cell[1]+i[1]] for i in
                   [[-1, -1], [-1, 0], [-1, 1],
                   [0, -1],            [0, 1],
                   [1, -1],   [1, 0],  [1, 1]]]

        return [i for i in targets if 0 <= i[0] < self.height and 0 <= i[1] < self.width]


class Game:

    def __init__(self, height=5, width=5, playercount=2):
        self.gamestate = Board()
        self.players = []
        self.words = {}
        self.gamestate = Board(height, width)
        self.players = [{'name': 'Player {}'.format(i), 'score' : 0} for i in range(1, playercount + 1)]

    def make_move(self, word, player_no):
        coords = self.gamestate.find_word(word)
        if coords:
            self.update_words(word, player_no, coords)
            self.update_scores()

    def remove_word(self, word):
        if word in self.words:
            self.words.pop(word)
            self.update_scores()

    def update_words(self, word, player_no, coords):

        # exclude existing words
        # only exclude words that belong to other players
        if word in self.words:
            if self.words[word]['player'] is not player_no:
                self.words[word]['player'] = 'Excluded'
        else:
            self.words[word] = {'player': player_no, 'coords': coords, 'score': 1}

    def update_scores(self):
        scores = {}
        for i in self.words:
            if self.words[i]['player'] in scores:
                scores[self.words[i]['player']] += self.words[i]['score']
            else:
                scores[self.words[i]['player']] = self.words[i]['score']

        for i in range(len(self.players)):
            if i in scores:
                self.players[i]['score'] = scores[i]
            else:
                self.players[i]['score'] = 0


class ConsoleGame (Game):
    """Currently just a few functions that are useful for debugging and development
    I'm hoping for a proper curses implementation later"""

    def print_board(self):
        print (*[' '.join(i) for i in self.gamestate.cells], sep = '\n')


class GuiGame (Game): # may separate these into different classes for each window

    board_window = tkinter.Tk()
    board_window.withdraw()
    search_entry = tkinter.Entry()
    
    cells = [] # may be duplicating the work of gamestate...refactor later

    board_font = font.Font(size = 64)
    disp_font = font.Font(size = 22)

    board_bg = 'white'
    board_hl = 'yellow'
    
    cell_settings = {#'activebackground' : 'yellow',
                     'relief' : 'ridge',
                     'width' : 2}
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
                self.cells[r][c]['font'] = self.board_font
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
        tkinter.Label(self.search_window, text = 'Word', font = self.disp_font).grid(row=0,column=0)
        self.search_entry = tkinter.Entry(self.search_window, font = self.disp_font)
        self.search_entry.grid(row=0, column=1, columnspan=len(self.players)-1 or 1, sticky='ew')
        tkinter.Button(self.search_window, text = "go", command = self.search_button,
                       font = self.disp_font).grid(row=0, column=len(self.players), sticky='e')

        #active player selection
        self.player_buttons = []
        self.active_player = tkinter.IntVar(value=0)
        for x,i in enumerate(self.players):
            self.player_buttons.append(tkinter.Radiobutton(self.search_window,
                                                           text = i['name'],
                                                           variable = self.active_player,
                                                           font = self.disp_font,
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
            self.cells[i[0]][i[1]].config(bg = self.board_bg)

        self.active = target

        #apply highlighting
        for i in self.active:
            self.cells[i[0]][i[1]].config(bg = self.board_hl)

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
                                font = self.disp_font, fg = 'red')
        ex_name.grid(row = 0, column = 0, columnspan = 2)
        ex_score = tkinter.Label(self.score_window, textvariable=self.excluded_score,
                                 font = self.disp_font, fg = 'red')
        ex_score.grid(row = 1, column = 0, columnspan = 2)
        
        for i,j in enumerate(self.players):
            col = (i+1) * 2
            
            p_name = tkinter.Label(self.score_window, text=j['name'], font = self.disp_font)
            p_name.grid(row=0, column=col)

            p_score = tkinter.Label(self.score_window, textvariable=self.scores[i],
                                    font = self.disp_font)
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
                self.words[i]['label'] = tkinter.Label(self.score_window, text = i, font = self.disp_font)
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
        board_size_entry.insert(0, self.board_font['size'])
        board_size_entry.grid(row=0, column=0)
        tkinter.Label(self.pref_window, text = "Board font size").grid(row=0, column = 1)
        
        disp_size_entry = tkinter.Entry(self.pref_window)
        disp_size_entry.grid(row=1, column=0)
        disp_size_entry.insert(0, self.disp_font['size'])
        tkinter.Label(self.pref_window, text = "Display font size").grid(row=1, column = 1)
        

        tkinter.Button(self.pref_window, text="Apply",
                       command=lambda: self.set_prefs(board_size = board_size_entry.get(),
                                                      disp_size = disp_size_entry.get())
                       ).grid(row = 2, column = 1)

    def set_prefs(self, board_size, disp_size):
        self.board_font['size'] = int(board_size)
        self.disp_font['size'] = int(disp_size)

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
            

#if __name__ == '__main__':
#    instance = NewGame()
