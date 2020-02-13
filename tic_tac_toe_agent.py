import json, random
import math


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

    PRINT_AVAILABLE_PLAYS_SCORE = False                  # :bool: Enables play evaluation on screen printing.
    PRINT_POSSIBILITY_TREE = False                       # :bool: Enables possibility tree on screen printing.
    RANDOM_INITIAL_MOVES = False                         # :bool: First move of agent is random despite playing order.
    VICTORY_CONDITIONS = [                               # :list: Board formations indicating victory.
        ('1', '2', '3'), ('1', '4', '7'),
        ('1', '5', '9'), ('2', '5', '8'),
        ('3', '5', '7'), ('3', '6', '9'),
        ('4', '5', '6'), ('7', '8', '9')
    ]

    def __init__(self, board: dict, agent_symbol: str, accuracy: float = 1):
        """
        Agent constructor, stores given board situation and general states.
        :param board: Given board situation.
        :param agent_symbol: Symbol to be assigned to agent.
        :param accuracy: Limits calculated branch levels as a percent of the maximum number of branch levels.
        """

        self.board = dict(board)                                 # :dict: Given board situation.
        self.agent_symbol = agent_symbol                         # :str: Agent symbol on board.
        self.opponent_symbol = self.__get_opponent_symbol()      # :str: Opponent symbol on board.
        self.accuracy = accuracy                                 # :float: Desired agent accuracy (0-1).
        self.maximum_branch_depth = None                         # :int: Current possible branch depth.
        self.limit_branch_depth = None                           # :int: Limit branch depth to be calculated.

    def get_move(self) -> str:
        """
        Selects position choice criteria and returns chosen position.
        :return: Chosen board position.
        """

        # Returns random movement selection for first movement if applicable.
        if (self.RANDOM_INITIAL_MOVES and self.__is_initial_move(2)) or self.__is_initial_move(1):
            return self.__get_random_move()

        # Returns calculated movement choice.
        else:
            return self.__get_agent_move()

    def __get_random_move(self):
        """
        Returns random movement for agent.
        """

        # Generates random movement considering free board positions.
        movement = random.choice([k for k, v in self.board.items() if not v.strip()])
        if self.PRINT_AVAILABLE_PLAYS_SCORE:
            print()
            print(f'Random chosen move: {movement}')

        # Updates internal board and returns move.
        self.board[movement] = self.agent_symbol
        return movement

    def __get_agent_move(self) -> str:
        """
        Triggers movement selection logic and returns result.
        :return: Integer denoting result.
        """

        # Updates current board's branch depth values.
        self.__update_branch_depths()

        # Recursively calculates complete possibility tree and logs result if required.
        possibility_tree = self.__get_possibility_tree(board=self.board)
        if self.PRINT_POSSIBILITY_TREE:
            print(json.dumps(possibility_tree, indent=4, sort_keys=False))

        # Evaluates each position's branch score.
        best_moves = []
        for move, branch in possibility_tree.items():
            branch_score = self.__evaluate_moves({move: branch})
            best_moves.append({
                'move': move,
                'branch_score': round(branch_score, 7)
            })

        # Sorts by best score and displays results if required.
        best_moves = sorted(best_moves, key=lambda k: k['branch_score'], reverse=True)
        if self.PRINT_AVAILABLE_PLAYS_SCORE:
            print()
            for x in best_moves:
                print(f"-> Move: {x.get('move')} | Branch score: {x.get('branch_score')}")

        # Randomizes chosen move amongst equally scored best moves.
        best_move_score = best_moves[0].get('branch_score')
        chosen_move = random.choice([x.get('move') for x in best_moves if x.get('branch_score') == best_move_score])
        if self.PRINT_AVAILABLE_PLAYS_SCORE:
            print(f"Chosen move: {chosen_move}")

        # Updates internal board with new position and returns choice.
        self.board[chosen_move] = self.agent_symbol
        return chosen_move

    def __get_possibility_tree(self, board: dict, possibility_tree: dict = None, agent_turn: bool = True,
                               branch_level: int = 0) -> dict:
        """
        Recursively builds the possibilities tree.
        :param board: Dictionary containing current board situation.
        :param possibility_tree: Possibility tree under construction.
        :param agent_turn: Boolean stating if it's the agent's turn or not.
        :param branch_level: Current score multiplier.
        :return: Dictionary containing possibility tree.
        """

        # Initializes possibility tree if none was provided.
        if not possibility_tree: possibility_tree = {}

        # Gets available board positions for this branch.
        available_plays = [k for k, v in board.items() if not v.strip()]

        # If no positions are left, returns empty branch.
        if len(available_plays) == 0: return {}

        # Updates current branch level value.
        branch_level += 1

        # If maximum branch level has been exceeded, returns empty branch.
        if branch_level > self.limit_branch_depth: return {}

        # Iterates on available board positions.
        for play in available_plays:

            # Creates updated board with current iteration's position. (Passing a copy is needed)
            updated_board = dict(board)
            updated_board[play] = self.agent_symbol if agent_turn else self.opponent_symbol

            # Evaluates current move score.
            victory, score = self.__check_victory(updated_board)
            if victory:
                score /= 10**(branch_level-1) if victory == self.agent_symbol else -(10**(branch_level-1))

            # Creates node for currently analyzed position.
            possibility_tree[str(play)] = PlayNode(score, agent_turn).__dict__

            # Populates current branch and adds new node to the sub-branch if victory hasn't been achieved.
            if not victory:
                possibility_tree[str(play)]['branch'] = \
                    self.__get_possibility_tree(
                        board=updated_board,
                        possibility_tree=possibility_tree[str(play)]['branch'],
                        agent_turn=not agent_turn,
                        branch_level=branch_level
                    )
            else:
                possibility_tree[str(play)]['branch'] = {}

        return possibility_tree

    @classmethod
    def __evaluate_moves(cls, moves: dict, branch_score: float = 0) -> float:
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
    def __check_victory(cls, board: dict) -> (str, int):
        """
        Checks victory conditions.
        :param board: Dictionary containing board to be analyzed.
        :return: Symbol of winner or None case no winners.
        """

        for a, b, c in cls.VICTORY_CONDITIONS:
            if board[a] == board[b] == board[c] != ' ':
                return board[a], 10

        return None, 0

    def __is_initial_move(self, move: int = 2) -> bool:
        """
        Checks if it's an initial move. Might be first of second board move.
        :return: Boolean denoting if it's first or second move.
        """

        return 9-[v for k, v in self.board.items()].count(' ') < move

    def __get_opponent_symbol(self) -> str:
        """
        Deduces opponent symbol.
        :return: String containing opponent symbol.
        """

        if self.agent_symbol == 'X': return 'O'
        else: return 'X'

    def __update_branch_depths(self):
        """
        Updates current and maximum branch numbers of board.
        :return: void.
        """

        self.maximum_branch_depth = len([v for k, v in self.board.items() if not v.strip()])
        if self.accuracy <= 0: self.limit_branch_depth = 2
        elif self.accuracy > 1: self.limit_branch_depth = self.maximum_branch_depth
        else:
            self.limit_branch_depth = math.ceil(self.maximum_branch_depth * self.accuracy)
            if self.limit_branch_depth < 2: self.limit_branch_depth = 2

    def print_board(self):
        """
        Prints current internal board.
        :return: void.
        """

        b = self.board
        print(f"{b['7']}|{b['8']}|{b['9']}")
        print("-+-+-")
        print(f"{b['4']}|{b['5']}|{b['6']}")
        print("-+-+-")
        print(f"{b['1']}|{b['2']}|{b['3']}")

    def get_board(self) -> dict:
        """
        Exposes current internal board.
        :return: Dictionary containing current internal board.
        """

        return self.board


if __name__ == "__main__":

    current_board = {'7': 'O', '8': 'X', '9': ' ',
                     '4': 'X', '5': 'O', '6': 'O',
                     '1': ' ', '2': ' ', '3': 'X'}

    TicTacToeAgent.PRINT_POSSIBILITY_TREE = True
    TicTacToeAgent.PRINT_AVAILABLE_PLAYS_SCORE = True

    agent_symbol = 'X'
    max_branch_depth = 1

    agent = TicTacToeAgent(current_board, agent_symbol, max_branch_depth)
    this_move = agent.get_move()

    print(f"Agent symbol: {agent_symbol}")
    print(f'Chosen move: {this_move}')
    print('Final test board:')
    agent.print_board()
