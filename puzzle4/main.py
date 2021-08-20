import client.exchange as exchange
import client.miner as miner

from multiprocessing import Process, Queue

MAX_PROCESS = 50

if __name__ == '__main__':

    welcome = """
    __ __          ____             __
   / //_/___  ____/ / /______  ____/ /
  / ,< / __ \/ __  / //_/ __ \/ __  / 
 / /| / /_/ / /_/ / ,< / /_/ / /_/ /  
/_/ |_\____/\__,_/_/|_|\____/\__,_/   
   /  |/  /  _/___  ___  _____        
  / /|_/ // // __ \/ _ \/ ___/        
 / /  / // // / / /  __/ /            
/_/  /_/___/_/ /_/\___/_/             
                                      
    """
    print(welcome)

    process_queue = Queue()
    process_pool = []

    for i in range(MAX_PROCESS):
        process_pool.append(Process(target=miner.run_miner, args=[nonce]))

    for p in process_pool:
        p.start()
    
    for p in process_pool:
        p.join()