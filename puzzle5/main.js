function intToBoard(int) {
    bin = int.toString(2);

    board = [];
    do {board.push(bin.substring(0, 24))} 
    while ((bin = bin.substring(24, bin.length)) != "");

    board.reverse();

    _board = [];
    for(let row of board) {
        var _row = [];
        do {_row.push(row.substring(0, 2))} 
        while((row = row.substring(2, row.length)) != "");

        _row.reverse();

        _row = _row.map((x) => parseInt(x, 2));

        _board.push(_row);
    }

    return _board;
}

var player_pos;
var board_int;
var board_int;

instance.methods.getPlayerPos().call().then((x) => {
    player_pos = x;

    instance.methods.getBoard().call().then((x) => {
        board_int = x;
        board = intToBoard(board_int);

        player_pos_row = Array(10).fill(0);
        player_pos_row[player_pos] = "x";

        board.push(player_pos_row);
    });    
});

