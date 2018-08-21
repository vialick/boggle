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

    letter_dist = OrderedDict({ 'a': 	0.08167,
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
    gamestate = Board()
    players = []
    words = {}

    def __init__(self, height=5, width=5, playercount=2):
        self.gamestate = Board(height, width)
        self.players = [{'name': 'Player {}'.format(i), 'score' : 0} for i in range(1, playercount + 1)]  # fix to be proper player

    def make_move(self, word, player_no):
        coords = self.gamestate.find_word(word)
        if coords:
            self.update_words(word, player_no, coords)
            self.update_scores()

    def update_words(self, word, player_no, coords):
                
        if word in self.words:
            self.words[word]['player'] = 'Excluded'
        else:
            self.words[word] = {'player': player_no, 'coords': coords, 'score': 1}
            if debug: print('Added')

    def update_scores(self):
        scores = {}
        for i in self.words:
            if self.words[i]['player'] in scores:
                scores['player'] += self.words[i]['score']
            else:
                scores['player'] = self.words[i]['score']
        for i in self.players:
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
    search_window = tkinter.Toplevel(board_window)
    score_window = tkinter.Toplevel(board_window)

    board_window.withdraw()
    search_window.withdraw()
    score_window.withdraw()

    search_entry = tkinter.Entry()
    
    cells = [] # may be duplicating the work of gamestate...refactor later

    disp_font = font.Font(size = 32)
    cell_settings = {'activebackground' : 'yellow',
                     'relief' : 'ridge',
                     'width' : 2}
    active = set()          # words which have been highlighted
    active_player = 0

    player_buttons = []

    def __init__(self, rows = 5, columns = 5, playercount = 2):
        
        #initialise the parent class
        super().__init__(rows, columns, playercount)
        
        #board window
        self.board_window.deiconify()
        for r, i in enumerate(self.gamestate.cells):
            self.cells.append([])
            for c, j in enumerate(i):
                self.cells[r].append(tkinter.Label(self.board_window, text = j, **self.cell_settings))
                self.cells[r][c]['font'] = self.disp_font
                self.cells[r][c].grid(row = r, column = c)

        self.display_search_window() # show search window
        self.display_score_window() # show score window

    def display_search_window(self):
        """displays search window"""
        self.search_window.deiconify()
        tkinter.Label(self.search_window, text = 'Word').grid(row=0,column=0)
        self.search_entry = tkinter.Entry(self.search_window)
        self.search_entry.grid(row=0, column=1)
        tkinter.Button(self.search_window, text = "go", command = self.search_button).grid(row=0, column=2)
        for x,i in enumerate(self.players):
            tkinter.Button(self.search_window, text = i['name'], command = lambda p = x:self.set_active(p)).grid(row=1,column=x)

    def set_active(self, player_no):
        self.active_player = player_no

    def display_score_window(self):
        self.score_window.deiconify()

        ex_name = tkinter.Label(self.score_window, text='Excluded')
        ex_name.grid(row = 0, column = 0)
        ex_score = tkinter.Label(self.score_window, text='0') # FIX
        ex_score.grid(row = 1, column = 0)
        
        for i,j in enumerate(self.players):
            p_name = tkinter.Label(self.score_window, text=j['name'])
            p_name.grid(row=0, column=i+1)

            p_score = tkinter.Label(self.score_window, text=j['score'])
            p_score.grid(row = 1, column = i+1)

    def search_button(self):
        text = self.search_entry.get()

        #self.make_move(text, self.active_player)
        try:
            coords = self.gamestate.find_word(text) or []
        except Exception:
            coords = []
        self.highlight(coords)

    def highlight(self, target = []):
        """display the board, highlighting specified cells"""
        
        #remove existing highlighting
        for i in self.active:
            self.cells[i[0]][i[1]].config(state = 'normal')

        self.active = target

        #apply highlighting
        for i in self.active:
            self.cells[i[0]][i[1]].config(state = 'active')


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
