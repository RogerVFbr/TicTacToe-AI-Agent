import json, random


class PlayNode:
    """
    Node of play possibility.
    """

    def __init__(self, score, agent_turn):
        self.agent_turn = agent_turn
        self.score = score
        self.branch = {}


class TicTacToeAgent:
    """
    Tic tac toe playing AI Agent.
    """

    AGENT_SYMBOL = 'X'
    OPPONENT_SYMBOL = 'O'

    PRINT_AVAILABLE_PLAYS_SCORE = False
    PRINT_POSSIBILITY_TREE = False

    def __init__(self, board, agent_symbol):
        self.board = dict(board)
        type(self).AGENT_SYMBOL = agent_symbol
        type(self).OPPONENT_SYMBOL = self.__get_opponent_symbol()

    def get_move(self):
        """
        Triggers movement selection logic and returns result.
        :return: Integer denoting result.
        """

        # If board is empty, get special initial position, log, update internal board and return value.
        if self.is_board_empty():
            initial_move = self.get_initial_move()
            if self.PRINT_AVAILABLE_PLAYS_SCORE:
                print(f'0 -> Special initial move: {initial_move}')
            self.board[initial_move] = self.AGENT_SYMBOL
            return initial_move

        # Recursively calculates complete possibility tree and logs result if required.
        possibility_tree = self.__get_possibility_tree(board=self.board)
        if self.PRINT_POSSIBILITY_TREE:
            print(json.dumps(possibility_tree, indent=4, sort_keys=False))

        # Evaluates each position's branch score, sorts by best score and displays results if required.
        next_moves = []
        for move, node in possibility_tree.items():
            branch_score = self.__evaluate_moves({move: node})
            next_moves.append({
                'move': move,
                'branch_score': branch_score
            })
        next_moves = sorted(next_moves, key=lambda k: k['branch_score'], reverse=True)
        if self.PRINT_AVAILABLE_PLAYS_SCORE:
            for i, x in enumerate(next_moves):
                print(f"{i} -> Move: {x.get('move')} | Branch score: {x.get('branch_score')}")

        # Updates internal board with new position.
        this_move = next_moves[0].get('move')
        if this_move:
            self.board[this_move] = self.AGENT_SYMBOL

        # Returns movement choice or None if board has no available position.
        return this_move

    @classmethod
    def __get_possibility_tree(cls, board, possibility_tree: dict = None, agent_turn: bool = True,
                               score_multiplier: float = 10):
        """
        Recursively builds the position possibilities tree.
        :param board: Dictionary containing current board situation.
        :param possibility_tree: Possibility tree under construction.
        :param agent_turn: Boolean stating if it's the agent's turn or not.
        :param score_multiplier: Current score multiplier.
        :return: Dictionary containing possibility tree.
        """

        # Initializes possibility tree if none was provided.
        if not possibility_tree: possibility_tree = {}

        # Gets available board positions.
        available_plays = [k for k, v in board.items() if not v.strip()]

        # If no positions are left, returns empty branch.
        if len(available_plays) == 0:
            return {}

        # Updates score multiplier for current branch.
        score_multiplier = score_multiplier*0.1

        # Iterates on available board positions.
        for play in available_plays:

            # Updates board with current iteration's position.
            updated_board = dict(board)
            if agent_turn:
                updated_board[play] = cls.AGENT_SYMBOL
            else:
                updated_board[play] = cls.OPPONENT_SYMBOL

            # Evaluates current move score.
            score = 0
            victory = cls.__check_victory(updated_board)
            if victory:
                score = 10*score_multiplier if victory == cls.AGENT_SYMBOL else -10*score_multiplier

            # Creates node for currently analyzed position.
            possibility_tree[str(play)] = PlayNode(score, agent_turn).__dict__

            # Populates current node's branch with new node if victory hasn't been achieved.
            if not victory:
                possibility_tree[str(play)]['branch'] = \
                    cls.__get_possibility_tree(
                        board=updated_board,
                        possibility_tree=possibility_tree[str(play)]['branch'],
                        agent_turn=not agent_turn,
                        score_multiplier=score_multiplier
                    )
            else:
                possibility_tree[str(play)]['branch'] = {}

        return possibility_tree

    @classmethod
    def __evaluate_moves(cls, moves: dict, branch_score = 0):
        """
        Recursively evaluates current branch score.
        :param moves: Dictionary containing current position and associated node.
        :param branch_score: Current position score.
        :return:
        """

        for k, v in moves.items():
            branch_score += v.get('score')
            if v.get('branch'):
                branch_score = cls.__evaluate_moves(
                    moves=v.get('branch'),
                    branch_score=branch_score
                )

        return branch_score

    @classmethod
    def __check_victory(cls, board):
        """
        Checks victory conditions.
        :param board: Dictionary containing board to be analyzed.
        :return: Symbol of winner or None case no winners.
        """

        conditions = [
            ('1', '2', '3'),
            ('1', '4', '7'),
            ('1', '5', '9'),
            ('2', '5', '8'),
            ('3', '5', '7'),
            ('3', '6', '9'),
            ('4', '5', '6'),
            ('7', '8', '9'),
        ]

        for a, b, c in conditions:
            if board[a] == board[b] == board[c] != ' ':
                return board[a]

        return None

    @staticmethod
    def get_initial_move():
        return random.choice(['1', '3', '5', '7', '9'])

    def is_board_empty(self):
        """
        Checks if internal board is empty denoting first play.
        :return: Boolean denoting if internal board is empty or not.
        """

        return len({v for k, v in self.board.items()}) == 1

    def print_board(self):
        """
        Prints current internal board.
        :return: void.
        """
        print(self.board['7'] + '|' + self.board['8'] + '|' + self.board['9'])
        print('-+-+-')
        print(self.board['4'] + '|' + self.board['5'] + '|' + self.board['6'])
        print('-+-+-')
        print(self.board['1'] + '|' + self.board['2'] + '|' + self.board['3'])

    def get_board(self):
        """
        Exposes current internal board.
        :return: Dictionary containing current internal board.
        """

        return self.board

    def __get_opponent_symbol(self):
        """
        Deduces opponent symbol.
        :return:
        """

        if type(self).AGENT_SYMBOL == 'X':
            return 'O'
        else:
            return 'X'


if __name__ == "__main__":

    current_board = {'7': 'O', '8': 'X', '9': ' ',
                     '4': 'X', '5': 'O', '6': 'O',
                     '1': ' ', '2': ' ', '3': 'X'}

    TicTacToeAgent.PRINT_POSSIBILITY_TREE = True
    TicTacToeAgent.PRINT_AVAILABLE_PLAYS_SCORE = True
    agent_symbol = 'X'

    agent = TicTacToeAgent(current_board, agent_symbol)
    chosen_move = agent.get_move()

    print(f"Agent symbol: {agent_symbol}")
    print(f'Chosen move: {chosen_move}')
    print('Final test board:')
    agent.print_board()
