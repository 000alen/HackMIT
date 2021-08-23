pragma solidity >=0.5.0 <0.9.0;

contract ChadPuzzle {
    uint constant rows = 6;
    uint constant cols = 12;
    uint constant length = rows * cols * 2;
    uint constant padding = 256 - length;
    uint constant left_mask = ((1<<(cols*2+1)) - 1) << (length - cols * 2);

    uint256 private board;
    int8 private livesLeft = 60;
    uint16 private moves = 0;
    uint8 private player_pos = 6;

   modifier move {
      require(livesLeft > 0, "Ran out of lives");
      _;
      moves++;
      fall();
   }

    // This is always called by our factory
    constructor(uint _board) public {
        board = _board;
    }

   function fall() private{
      uint top = (board & left_mask) >> (length - cols * 2);

      int8 lost = 0;
      uint i;
      for(i=0;i<cols;i++){
        //   bool res = (top & (3 << (2*i))) == 0;
        //   if(i==player_pos && res){
        //       movesLeft=0;
        //       return false;
        //   }
        //   else if(res){
        //       lost++;
        //   }
        uint res = top & (3 << (2*i));
        if(res != 0)
            lost++;
        if(res>>(2*i)==1){
            top = top ^ (3 << (2*i));
        }

      }
      livesLeft -= lost;
      board = ((board << (padding + 2*cols)) >> padding) | top; 
    }

    function left() public  move {
        require(player_pos > 0, "Can't go more left");
        player_pos--;
    }

    function right() public move {
        require(player_pos < cols-1, "Can't go more right");
        player_pos++;
    }
    
    function shoot() public move{        
        uint bullet = 3 << (2*(player_pos) + (rows-1)*cols*2 );
        // uint curBoard = board;
        while(bullet!=0){
            uint res = board & bullet;
            if(res !=0 ){

                // 2 -> 1
                if(res>(bullet>>1)){
                    board = board ^ bullet;
                }
                // 1 -> 0
                else{
                    board = board & (~bullet);
                }
                break;
            }
            bullet = bullet >> (2 * cols);
            // curBoard = curBoard >> (2 * cols);
        }
    }

    function getBoard() public view returns (uint) {
        return board;
    }

    function getMoves() public view returns (uint16) {
        return moves;
    }

    function getLives() public view returns (int8) {
        return livesLeft;
    }

    function getPlayerPos() public view returns (uint){
        return player_pos;
    }

}

contract ChadFactory {
    event PuzzleInstance(address instance);

    function createInstance(uint256 board)  public{
        ChadPuzzle instance = new ChadPuzzle(board);
        emit PuzzleInstance(address(instance));
    }
    
}
