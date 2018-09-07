import generators

debug = True


class Board:
    """A Boggle-style gameboard"""
    cells = []
    height = 0
    width = 0

    def __init__(self, height=5, width=5, generator=generators.Dice):
        """initialise the board"""
        (self.height, self.width) = (height, width)
        #self.set_board()
        self.cells = generator().build_board(height, width)


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
