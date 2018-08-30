import random
from collections import OrderedDict, Counter
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
                                'qu':	0.717171717,
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
        #self.set_board()
        self.cells = build_board(height, width)

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
                     'bg'       : 'white',
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
        self.pref_window.bind("<Return>", lambda x: self.set_prefs(board_size = board_size_entry.get(),
                                                      disp_size = disp_size_entry.get()))

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
            

#this stuff needs to be cleaned up

ngrams = {'a':
            {'a': 79794787, 'b': 6479202253, 'c': 12625666388, 'd': 10375130449,
            'e': 349540062, 'f': 2092395523, 'g': 5772552144, 'h': 384694919,
            'i': 8922759715, 'j': 331384552, 'k': 2952167845, 'l': 30662410438,
            'm': 8032259916, 'n': 55974567611, 'o': 130442323, 'p': 5719570727,
            'q': 63283982, 'r': 30308513014, 's': 24561944198, 't': 41920838452,
            'u': 3356322923, 'v': 5778409728, 'w': 1689436638, 'x': 531206960,
            'y': 6128842727, 'z': 334669428},
    'b':
            {'a': 4122472992, 'b': 308276690, 'c': 53278096, 'd': 69761165,
            'e': 16249257887, 'f': 4108696, 'g': 7203255, 'h': 29797934,
            'i': 3005679357, 'j': 654853039, 'k': 2639491, 'l': 6581097936,
            'm': 88228719, 'n': 59062122, 'o': 5509918152, 'p': 15427250,
            'q': 346506, 'r': 3145611704, 's': 1292319275, 't': 482272940,
            'u': 5214802738, 'v': 108385069, 'w': 8319869, 'x': 778622,
            'y': 4975814759, 'z': 1007374},
    'c': 
            {'a': 15174413181, 'b': 17751935, 'c': 2344219345, 'd': 62905910,
            'e': 18367773425, 'f': 39704311, 'g': 24975673, 'h': 16854985236,
            'i': 7936922442, 'j': 2962048, 'k': 3316660134, 'l': 4201617719,
            'm': 75144874, 'n': 24249641, 'o': 22384167777, 'p': 37067423,
            'q': 154363546, 'r': 4214150542, 's': 643530723, 't': 12997849406,
            'u': 4585165906, 'v': 5869407, 'w': 3909223, 'x': 876736,
            'y': 1176324279, 'z': 20601701},
    'd': 
            {'a': 4259590348, 'b': 78190243, 'c': 71030077, 'd': 1205446875,
            'e': 21565300071, 'f': 78347492, 'g': 874188188, 'h': 153344431,
            'i': 13899990598, 'j': 134832736, 'k': 9494027, 'l': 911886482,
            'm': 512522701, 'n': 213431654, 'o': 5307591560, 'p': 48855638,
            'q': 19927900, 'r': 2409399231, 's': 3560125353, 't': 81648332,
            'u': 4186093215, 'v': 537221821, 'w': 230152384, 'x': 1296277,
            'y': 1421751251, 'z': 2200704},
    'e':
            {'a': 19403941063, 'b': 763383542, 'c': 13457763533, 'd': 32937140633,
            'e': 10647199443, 'f': 4588497002, 'g': 3370515965, 'h': 742240059,
            'i': 5169898489, 'j': 128194584, 'k': 464449289, 'l': 14952716079,
            'm': 10536054813, 'n': 41004903554, 'o': 2044268477, 'p': 4837800987,
            'q': 1614312175, 'r': 57754162106, 's': 37766388079, 't': 11634161334,
            'u': 878402090, 'v': 7184041787, 'w': 3293529190, 'x': 6035335807,
            'y': 4053144855, 'z': 127540198},
    'f': 
            {'a': 4624241031, 'b': 7730842, 'c': 16254390, 'd': 13966832,
            'e': 6670566518, 'f': 4125634219, 'g': 14424524, 'h': 5166165,
            'i': 8024355222, 'j': 2065436, 'k': 3293208, 'l': 1830098844,
            'm': 19340776, 'n': 11823066, 'o': 13753006196, 'p': 6262895,
            'q': 149430, 'r': 6011200185, 's': 155349948, 't': 2302659749,
            'u': 2706168901, 'v': 807297, 'w': 6451511, 'x': 812116,
            'y': 256535008, 'z': 263860},
    'g': 
            {'a': 4175274057, 'b': 13944852, 'c': 6455066, 'd': 89087728,
            'e': 10861045622, 'f': 33962536, 'g': 697999944, 'h': 6414827751,
            'i': 4275639800, 'j': 1093028, 'k': 7338894, 'l': 1709752272,
            'm': 277966576, 'n': 1850801359, 'o': 3725558729, 'p': 11612944, 
            'q': 345624, 'r': 5548472398, 's': 1443474876, 't': 434302509, 
            'u': 2418410978, 'v': 1192366, 'w': 18260884, 'x': 557030, 
            'y': 731420025, 'z': 3431194}, 
    'h': 
            {'a': 26103411208, 'b': 123778334, 'c': 34631551, 'd': 80544316,
            'e': 86697336727, 'f': 63249924, 'g': 7789748, 'h': 14730425, 
            'i': 21520845924, 'j': 1282370, 'k': 6595610, 'l': 355049620, 
            'm': 359316447, 'n': 726288117, 'o': 13672603513, 'p': 16696129, 
            'q': 11925353, 'r': 2379584978, 's': 414044112, 't': 3670802795, 
            'u': 2077887429, 'v': 6292998, 'w': 134615178, 'x': 263997, 
            'y': 1412343465, 'z': 10729982}, 
    'i': 
            {'a': 8072199471, 'b': 2780268452, 'c': 19701195496, 'd': 8332214014, 
            'e': 10845731320, 'f': 5731148470, 'g': 7189051323, 'h': 58966344, 
            'i': 642384029, 'j': 31324465, 'k': 1209994695, 'l': 12167821320, 
            'm': 8959759181, 'n': 68595215308, 'o': 23542263265, 'p': 2515455253, 
            'q': 318727904, 'r': 8886799024, 's': 31817918249, 't': 31672532308, 
            'u': 490874936, 'v': 8116349309, 'w': 17611969, 'x': 621227893, 
            'y': 6247588, 'z': 1814164135}, 
    'j': 
            {'a': 729206855, 'b': 2126115, 'c': 3447571, 'd': 2615147,
            'e': 1463052212, 'f': 2421784, 'g': 1034900, 'h': 3541869,
            'i': 77899882, 'j': 2979950, 'k': 1740133, 'l': 3192327,
            'm': 3659540, 'n': 4150888, 'o': 1516687319, 'p': 6129447,
            'q': 0, 'r': 6846578, 's': 3329038, 't': 2917850,
            'u': 1655210582, 'v': 1719726, 'w': 1165914, 'x': 161750,
            'y': 1120221, 'z': 220675},
    'k': 
            {'a': 478095427, 'b': 25406204, 'c': 6326022, 'd': 18894758,
            'e': 6027536039, 'f': 44759608, 'g': 72267691, 'h': 89811517,
            'i': 2759841743, 'j': 3471162, 'k': 12782664, 'l': 298033281,
            'm': 50449220, 'n': 1450401608, 'o': 171324962, 'p': 20492678,
            'q': 187242, 'r': 76743394, 's': 1339590722, 't': 29132180,
            'u': 85313841, 'v': 4414960, 'w': 61416538, 'x': 555422,
            'y': 167761726, 'z': 150760},
    'l': 
            {'a': 14874551789, 'b': 188643782, 'c': 333338045, 'd': 7122648226,
            'e': 23382173640, 'f': 1507867867, 'g': 171657388, 'h': 45643026,
            'i': 17604626629, 'j': 3169833, 'k': 555883002, 'l': 16257360474,
            'm': 649112313, 'n': 165509578, 'o': 10908830081, 'p': 536595562,
            'q': 3582930, 'r': 283411884, 's': 3990203351, 't': 3486149365,
            'u': 3811884104, 'v': 984229060, 'w': 356374125, 'x': 8612462,
            'y': 11983948242, 'z': 11767790},
    'm': 
            {'a': 15938689768, 'b': 2544901434, 'c': 121591374, 'd': 18929019,
            'e': 22360109325, 'f': 107664447, 'g': 34537023, 'h': 15033898,
            'i': 8957825538, 'j': 2923325, 'k': 3956883, 'l': 129888836,
            'm': 2708822249, 'n': 247850339, 'o': 9498813191, 'p': 6743935008,
            'q': 708424, 'r': 87580303, 's': 2617582287, 't': 38538709,
            'u': 3231856188, 'v': 8172535, 'w': 16465357, 'x': 994334,
            'y': 1753447198, 'z': 970282},
    'n': 
            {'a': 9790855551, 'b': 122258836, 'c': 11722631112, 'd': 38129777631,
            'e': 19504235770, 'f': 1894270041, 'g': 26871805511, 'h': 306883963,
            'i': 9564648232, 'j': 312598990, 'k': 1455100124, 'l': 1798491132,
            'm': 782441941, 'n': 2051719074, 'o': 13099447521, 'p': 170186564,
            'q': 167770304, 'r': 258048421, 's': 14350320288, 't': 29359771944,
            'u': 2217508482, 'v': 1466426243, 'w': 163456000, 'x': 73899576,
            'y': 2760941827, 'z': 123192934},
    'o': 
            {'a': 1620913259, 'b': 2725791138, 'c': 4692062395, 'd': 5511014957,
            'e': 1089254517, 'f': 33130341561, 'g': 2651165734, 'h': 602121281,
            'i': 2474275212, 'j': 196696657, 'k': 1813376076, 'l': 10305660447,
            'm': 15402602484, 'n': 49570981965, 'o': 5928601045, 'p': 6313536754,
            'q': 29227658, 'r': 35994097756, 's': 8176085241, 't': 12465822481,
            'u': 24531132241, 'v': 5021440160, 'w': 9318366591, 'x': 523764012,
            'y': 1020190223, 'z': 97904996},
    'p': 
            {'a': 9123652775, 'b': 36901495, 'c': 33156666, 'd': 33798376,
            'e': 13477683504, 'f': 41022263, 'g': 13354952, 'h': 2661480326,
            'i': 3470838749, 'j': 2810773, 'k': 23099462, 'l': 7415349106,
            'm': 449910017, 'n': 33536129, 'o': 10189505383, 'p': 3850125519,
            'q': 1075049, 'r': 13378480175, 's': 1538723474, 't': 2982699529,
            'u': 2947681332, 'v': 6222096, 'w': 34037460, 'x': 1473468,
            'y': 331698156, 'z': 6382200},
            'q': 
            {'a': 4298294, 'b': 1083443, 'c': 1127399, 'd': 519921,
            'e': 572443, 'f': 947879, 'g': 0, 'h': 263509,
            'i': 8954617, 'j': 236928, 'k': 0, 'l': 6708919,
            'm': 989868, 'n': 1859810, 'o': 1324363, 'p': 272180,
            'q': 1712219, 'r': 1744325, 's': 4448602, 't': 1385505,
            'u': 4160167957, 'v': 635514, 'w': 163292, 'x': 159505,
            'y': 0, 'z': 0},
    'r': 
            {'a': 19332539912, 'b': 753194669, 'c': 3422694015, 'd': 5338083783,
            'e': 52285662239, 'f': 909634941, 'g': 2813274913, 'h': 426095630,
            'i': 20516398905, 'j': 15598009, 'k': 2736041446, 'l': 2432373251,
            'm': 4938158020, 'n': 4521640992, 'o': 20491179118, 'p': 1173542093,
            'q': 28152573, 'r': 3404547067, 's': 11180732354, 't': 10198055461,
            'u': 3618438291, 'v': 1953555667, 'w': 359714599, 'x': 32990613,
            'y': 6985436186, 'z': 17993128},
    's': 
            {'a': 6147356936, 'b': 223212317, 'c': 4363410770, 'd': 148275222,
            'e': 26282488562, 'f': 483979931, 'g': 69588685, 'h': 8888705287,
            'i': 15509759748, 'j': 7621847, 'k': 1112771273, 'l': 1575646777,
            'm': 1838392669, 'n': 258702825, 'o': 11214705934, 'p': 5392724233,
            'q': 209894196, 'r': 168896339, 's': 11421755201, 't': 29704461829,
            'u': 8774129154, 'v': 35005005, 'w': 663415953, 'x': 503772,
            'y': 1602829285, 'z': 7041052},
    't': 
            {'a': 14941000711, 'b': 71746167, 'c': 736955048, 'd': 36539510,
            'e': 33973261529, 'f': 159626603, 'g': 55522877, 'h': 100272945963,
            'i': 37856196209, 'j': 3169658, 'k': 13081991, 'l': 2775935006,
            'm': 746621025, 'n': 282266629, 'o': 29360205581, 'p': 121089391,
            'q': 2517400, 'r': 12006693396, 's': 9516029773, 't': 4812693687,
            'u': 7187510085, 'v': 32805751, 'w': 2322619238, 'x': 3328898,
            'y': 6408447994, 'z': 108527540},
            'u': 
            {'a': 3844138094, 'b': 2497666762, 'c': 5291161134, 'd': 2577213760,
            'e': 4158448570, 'f': 522547858, 'g': 3606562400, 'h': 30097154,
            'i': 2852182384, 'j': 14548024, 'k': 129819900, 'l': 9751225781,
            'm': 3901923211, 'n': 11121118166, 'o': 300484143, 'p': 3835093459,
            'q': 7235727, 'r': 15303657594, 's': 12808517567, 't': 11423899818,
            'u': 22006895, 'v': 82252351, 'w': 7824504, 'x': 110947766,
            'y': 128782521, 'z': 53873803},
    'v': 
            {'a': 3946966167, 'b': 2496014, 'c': 6570845, 'd': 8430332,
            'e': 23270129573, 'f': 1550317, 'g': 2960268, 'h': 2691078,
            'i': 7600241898, 'j': 724370, 'k': 337545, 'l': 11621019,
            'm': 3178223, 'n': 4317772, 'o': 2004982879, 'p': 5510046,
            'q': 212856, 'r': 24701238, 's': 16263248, 't': 6181932,
            'u': 62384927, 'v': 2622571, 'w': 742188, 'x': 449854,
            'y': 138085211, 'z': 501189},
    'w': 
            {'a': 10865206430, 'b': 29929113, 'c': 19008254, 'd': 99767462,
            'e': 10176141608, 'f': 45330551, 'g': 2751783, 'h': 10680697684,
            'i': 10557401491, 'j': 914179, 'k': 30095733, 'l': 429185823,
            'm': 30732232, 'n': 2227183930, 'o': 6252724050, 'p': 20982546,
            'q': 0, 'r': 867361010, 's': 989253674, 't': 184446342,
            'u': 19601657, 'v': 389123, 'w': 7377619, 'x': 150637,
            'y': 68368953, 'z': 0},
    'x': 
            {'a': 834649781, 'b': 2164724, 'c': 746076293, 'd': 168263,
            'e': 614533122, 'f': 52374239, 'g': 542548, 'h': 117618666,
            'i': 1111463633, 'j': 511074, 'k': 281255, 'l': 16728256,
            'm': 6569222, 'n': 1613611, 'o': 76097183, 'p': 1885334638,
            'q': 8225536, 'r': 907409, 's': 1804740, 't': 1315669490,
            'u': 134528161, 'v': 55076715, 'w': 6292525, 'x': 79068246,
            'y': 72645837, 'z': 136521},
            'y': 
            {'a': 444542870, 'b': 121220723, 'c': 380670476, 'd': 192245315,
            'e': 2612941418, 'f': 21246637, 'g': 73102462, 'h': 14682887,
            'i': 812619095, 'j': 561334, 'k': 9292584, 'l': 416082307,
            'm': 667551857, 'n': 372595315, 'o': 4226720021, 'p': 702499946,
            'q': 384882, 'r': 219696469, 's': 2730343336, 't': 470429861,
            'u': 37436235, 'v': 5115763, 'w': 95070267, 'x': 4211192,
            'y': 1993017, 'z': 51097953},
    'z': 
            {'a': 702199296, 'b': 5858211, 'c': 2100797, 'd': 1415016,
            'e': 1402290616, 'f': 608389, 'g': 4726653, 'h': 18782710,
            'i': 341671190, 'j': 309029, 'k': 906537, 'l': 35456851,
            'm': 4713608, 'n': 4300522, 'o': 202480511, 'p': 1361846,
            'q': 913036, 'r': 5320518, 's': 8395904, 't': 6627349,
            'u': 60692846, 'v': 4618705, 'w': 6279286, 'x': 108224,
            'y': 66473188, 'z': 75012595}}


def generate_cell(adjacent):
    values = {}
    for i in adjacent:
        values = Counter(values) + Counter(ngrams[i])

    return random.choices(tuple(values.keys()), weights = tuple(values.values()),
                          k=1)[0]

def build_board(rows, columns):
    
    board = [['' for c in range(columns)] for r in range(rows)]
    board[0][0] = random.choice('abcdefghijklmnopqrstuvwxyz')

    for r in range(rows):
        for c in range(columns):
            if board[r][c]:
                continue
                
            adjacent = []
            if r >=1 and c >= 1:
                adjacent.append(board[r-1][c-1])
            if r >=1:
                adjacent.append(board[r-1][c])
            if r >=1 and c < (columns -1):
                adjacent.append(board[r-1][c+1])
            if c >= 1:
                adjacent.append(board[r][c-1])
            board[r][c]= generate_cell(''.join(adjacent))
    return board
