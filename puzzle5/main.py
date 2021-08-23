from web3 import Web3
from solcx import compile_source

import string
import collections

DIGITS = string.digits + string.ascii_letters
CONTRACT_ADDRESS = "0x98CD3B326E1248061d684Ae230F580b74195dD86"
PROVIDER_URL = "https://ropsten.infura.io/v3/ad31d30c3c96492d9a7fc9324f4ddfde"
SOURCE = open("contract.sol").read()


def find_monkey_position(B):
    """
    Args:
        B (tuple): board configuration
    Output:
        int: column position of the monkey in B
    """
    for i, x in enumerate(B[-1]):
        if x == "x":
            return i

    assert False


def num_balloons(B):
    """
    Args:
        B (tuple): board configuration
    Output:
        int: number of balloons on the board
    """
    ret = 0
    for r in B[:-1]:
        for c in r:
            if c != 0:
                ret += 1
    return ret


def make_move(B, cur_monkey_pos, cur_num_balloons, cur_num_lives, move):
    """
    Args:
        B (tuple): board configuration
        cur_monkey_pos (int): current column position of the monkey
        cur_num_balloons (int): current number of balloons on the board
        cur_num_lives (int): current number of lives remaining
        move (str): the proposed move (one of 'left', 'right', 'shoot')
    Output:
        (tuple, int, int, int): A tuple consisting of the board configuration after the move,
                                the new monkey position, the new number of balloons on the map,
                                and the new number of lives left
                                (or None if invalid move or if the monkey gets hit)
    """

    def check_lose(B, cur_monkey_pos):
        """
        Args:
            B (tuple): board configuration
            cur_monkey_pos (int): current column position of the monkey
        Output:
            bool: True if a balloon will hit the monkey when the balloons shift down; False otherwise
        """
        assert B[-1][cur_monkey_pos] == "x"
        if B[-2][cur_monkey_pos] != 0:
            return True
        return False

    def shift_down(B, cur_monkey_pos, cur_num_lives):
        """
        Just performs the shift of all the balloons downwards.
        Args:
            B (tuple): board configuration
            cur_monkey_pos (int): current column position of the monkey
            cur_num_lives (int): current number of lives in this configuration
        Output:
            (tuple, int): tuple consisting of the board configuration after balloons have all moved
                          down by 1 and the new number of lives (or None if the monkey gets hit)
        """

        # if check_lose(B, cur_monkey_pos):
        #     return None

        new_board = []
        new_num_lives = cur_num_lives

        # construct the top row: if the balloon hits the ground, it respawns with +1 and we lose a life
        new_num_lives -= sum(1 for b in B[-2] if b > 0)
        top_row = tuple((b + 1 if 0 < b < 2 else b) for b in B[-2])
        # top_row = B[-2]
        new_board.append(top_row)

        # move all the middle rows down
        new_board.extend([r for r in B[:-2]])

        # add the ground row: nothing changes
        new_board.append(B[-1])

        return (tuple(new_board), new_num_lives)

    def partial_move(B, cur_monkey_pos, cur_num_balloons, move):
        """
        Just performs the move, without the shift downwards
        Args:
            B (tuple): board configuration
            cur_monkey_pos (int): current column position of the monkey
            cur_num_balloons (int): current number of balloons on the board
            move (str): the proposed move (one of 'left', 'right', 'shoot')
        Output:
            (tuple, int, int): A tuple consisting of the board configuration after the move,
                               the new monkey position, and the new number of balloons on the map
                               (or None if invalid move)
        """

        assert B[-1][cur_monkey_pos] == "x"
        R = len(B)
        C = len(B[0])

        new_board = [r for r in B[:-1]]
        new_bottom_row = [0 for _ in range(C)]
        new_monkey_pos = cur_monkey_pos
        new_num_balloons = cur_num_balloons

        if move == "left":
            if new_monkey_pos == 0:
                return None
            new_monkey_pos -= 1
        elif move == "right":
            if new_monkey_pos == C - 1:
                return None
            new_monkey_pos += 1
        elif move == "shoot":
            # simulate the dart
            for row in range(R - 2, -1, -1):
                if B[row][new_monkey_pos] != 0:
                    new_row = list(B[row])
                    new_row[new_monkey_pos] -= 1
                    if new_row[new_monkey_pos] == 0:
                        new_num_balloons -= 1
                    new_board[row] = tuple(new_row)
                    break
        else:
            assert False, "invalid move: " + move

        new_bottom_row[new_monkey_pos] = "x"
        new_board.append(tuple(new_bottom_row))
        return (tuple(new_board), new_monkey_pos, new_num_balloons)

    # make the move
    move_res = partial_move(B, cur_monkey_pos, cur_num_balloons, move)
    if move_res is None:  # invalid move
        return None
    move_board, new_monkey_pos, new_num_balloons = move_res  # unpack

    # shift all the balloons down
    shift_res = shift_down(move_board, new_monkey_pos, cur_num_lives)
    if shift_res is None:  # check if a balloon hit the monkey
        return None
    new_board, new_num_lives = shift_res  # unpack
    return (new_board, new_monkey_pos, new_num_balloons, new_num_lives)


def fast_solve(B_, init_lives):
    q = collections.deque([((B_, find_monkey_position(B_), num_balloons(B_), init_lives),0)])
    seen = {}
    while len(q) > 0:
        (B, pos, balloons, lives), moves = q.popleft()
        if B in seen:
            continue
        else:
            seen[B]=True
        if balloons == 0:
            return moves, lives
        valid = [make_move(B, pos, balloons, lives, 'left'), make_move(B, pos, balloons, lives, 'right'), make_move(B, pos, balloons, lives, 'shoot')]
        q.extend([(item,moves+1) for item in valid if item is not None and item[-1]>0])
    return None, None


def get_neighbors(config):
    possible_list = set()
    B, monkey_index, balloons, num_lives = config
    if num_lives == 0:
        return possible_list

    for move in ['left', 'right', 'shoot']:
        try_move = make_move(B, monkey_index, balloons, num_lives, move)
        if try_move and try_move[3] > 0:
            possible_list.add((try_move, move))

    return possible_list


def solve(B, init_lives):
    """
    Args:
        B (tuple): the initial board configuration.
        init_lives (int): starting number of lives

    Output:
        int: the minimum number of moves to pop all the balloons (or None if it's not possible).
    """

    if num_balloons(B) == 0:
        return 0

    previous = set()
    queue = [[((B, find_monkey_position(B), num_balloons(B), init_lives), None)]]
    pointer = 0

    while queue and pointer < len(queue):
        path = queue[pointer]
        node = path[-1]

        if node not in previous:
            neighbors = get_neighbors(node[0])
            for neighbor in neighbors:
                new_board, move = neighbor
                if neighbor not in previous:
                    new_path = list(path)
                    new_path.append(neighbor)
                    queue.append(new_path)

                    if new_board[2] == 0:
                        print('lives left: ', new_board[3])
                        tracked_moves = []
                        tracked_states = []
                        for state in new_path:
                            if state[1]:
                                tracked_moves.append(state[1])
                        return tracked_moves, new_board[3]

            previous.add(node)
        pointer += 1
    return None


# function pad(bin, size = 24) {
#     if(bin.length >= size)
#         return bin
#     return ("0".repeat(size-bin.length)) + bin
# }
def pad(bin, size=24):
    if len(bin) >= size:
        return bin
    return ("0" * (size - len(bin))) + bin


def int2base(x, base):
    if x < 0:
        sign = -1
    elif x == 0:
        return DIGITS[0]
    else:
        sign = 1

    x *= sign
    digits = []

    while x:
        digits.append(DIGITS[x % base])
        x = x // base

    if sign < 0:
        digits.append('-')

    digits.reverse()

    return ''.join(digits)


# The uint256 variable board  stores the game board in a flattened row major order, with each board slot occupying 2 bits.
# board = 0b0000...row5,row4,row3,row2, row1, row0
# rowN = col11,...,col0 
# function boardToInt(board){
#     const rows = []
#     for(let row of board){
#         row = row.map((x)=>parseInt(x,10))
#         row = row.map((x)=>x.toString(2))
#         row = row.map((x)=>pad(x,2))
#         row.reverse()
#         rows.push(row.join(''))
#     }
#     rows.reverse()
#     const bin = '0b' + rows.join('')

#     return web3.utils.toBN(BigInt(bin).toString(10))
# }
def boardToInt(board):
    rows = []
    for row in board:
        # row = list(map(lambda x: int(x, 10), row))
        row = list(map(lambda x: int2base(x, 2), row))
        row = list(map(lambda x: pad(x, 2), row))
        row = list(reversed(row))
        rows.append(''.join(row))
    rows = reversed(rows)

    bin = '0b' + ''.join(rows)

    return bin


def intToBoard(board: str):
    # board = board[2:]
    board = [board[i : i + 24] for i in range(0, len(board), 24)]
    board = list(reversed(board))

    _board = []
    for row in board:
        row = [row[i : i + 2] for i in range(0, len(row), 2)]
        row = list(reversed(row))
        row = [int(x, 2) for x in row]

        _board.append(row)

    return _board


compiled_sol = compile_source(SOURCE)
contract_id, contract_interface = compiled_sol.popitem()
abi = contract_interface["abi"]
w3 = Web3(Web3.HTTPProvider(PROVIDER_URL))
contract = w3.eth.contract(CONTRACT_ADDRESS, abi=abi)

player_position = contract.functions.getPlayerPos().call()

# board_int = contract.functions.getBoard().transact()
# board_int = 882893299950477527990625818533691396

board_int = contract.functions.getBoard().call()
board_bin = int2base(board_int, 2)
board = intToBoard(board_bin)

print(player_position)
print(board)

board.append(["x" if i == player_position else 0 for i in range(len(board[0]))])

board = tuple(map(tuple, board))

print(fast_solve(board, 60))

# wrapper = {
#     "left": contract.functions.left,
#     "right": contract.functions.right,
#     "shoot": contract.functions.shoot,
# }

# for step in steps:
#     wrapper[step]().call()

# print(contract.functions.getBoard().call())
