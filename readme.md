Team Members: Rosalyn Tan, Nancy McNamara

This repository is for our CSE 30332 Programming Paradigms final project.

The game that we created is a game that can be played by two players on different computers. The program is functional when played across the student machines, but is not very fast. To run it on the student machines, first log in to two instances of the student machine student02, then comment out the 23rd line (put a # at the front) and uncomment the 24th line (remove the #) in p2.py and adhere to the following steps. If you wish to run the game on localhost, in order to see the game running at full speed, simply leave the server settings as they are in p2.py and follow the steps below.

The first player initializes the game by typing "python p1.py" on the command line. The seconds player then opens their program in a different window by similarly typing "python p2.py" on the command line. Player 2's window will remain in a waiting state and display a waiting message until Player 1 has selected the mode in which he or she wishes to play. This is done by clicking one of the four icons on the opening screen for Player 1. A status message on the screen will inform Player 1 whether Player 2 has connected yet. Once Player 2 is connected and Player 1 has selected a mode, the game begins. The two players are playing against each other with the goal of scoring as many points as possible as quickly as possible. In all four modes, Player 1 uses the arrow keys to move his/her character from left to right in an attempt to catch as many falling items as possible. For each item that Player 1 catches, a point is awarded. At the same time, Player 2 is playing as a character on the side of the screen and is attempting to shoot these same items for his/her own points before his/her opponent (Player 1) can catch them. Player 2 does so by moving the mouse to aim and clicking to fire. For every three items that Player 2 destroys, a point is awarded. Player 2's "bullets" pick up any number of falling items, but there can only be one on the screen at a time. The points are displayed on both screens with the higher score always being moved to the top. Player 1's score is pink, while Player 2's score is white. The game ends when either player exceeds 20 points, and both players receive a notification telling them whether they have won or lost. Either player can exit the game at any time by closing the window.

The four modes include:
	-Basketball: Player 1 plays as Kobe Bryant, tipping the falling basketballs into a hoop on the Lakers' court. Player 2 plays as LeBron James, who is blowing bubblegum bubbles at the basketballs to prevent Kobe from scoring.
	-Oliver Twist: Player 1 plays as Oliver, holding his bowl out to catch the falling heaps of porridge in the cafeteria of the orphanage. Player 2 plays as Mr. Bumble, hurling a tangle of ladles to prevent Oliver from getting any "more."
	-Pirates: Player 1 plays as a greedy pirate attempting to stuff his treasure chest with falling gold coins on an abandoned beach. Player 2 operates a cannon to blast the treasure away before the pirate can get his hands on it.
	-Sesame Street: Player 1 plays as Cookie Monster, who thankfully has a jar on hand to catch all the cookies falling from the sky on Sesame Street. Ever the healthy lifestyle advocate, Michelle Obama is there for Player 2 to help throw the cookies awry with heads of lettuce.

The GitHub repository is linked below and demonstrates incremental (albeit slow) progress:
https://github.com/rosalyntan/cse30332-final-project

All of the images used in the game are credited below:

PENNY IMAGE:
https://upload.wikimedia.org/wikipedia/commons/5/52/1909-S_VDB_Lincoln_cent_obverse_transparent_background.png

CANNON IMAGE:
https://cdn0.rubylane.com/shops/mygrandmotherhadone/cl004170.1L.jpg

CANNONBALL IMAGE:
http://vignette2.wikia.nocookie.net/fallout/images/f/fa/Cannonball.png/revision/20151210003937

PIRATE IMAGE:
http://www.clipartlord.com/wp-content/uploads/2015/11/pirate10.png

TREASURE CHEST IMAGE:
http://gallery.yopriceville.com/Free-Clipart-Pictures/Money-PNG/Treasure_Chest_PNG_Clipart_Picture#.VyRZVJMrJsN

PIRATE BACKGROUND IMAGE:
https://s-media-cache-ak0.pinimg.com/736x/05/4e/8d/054e8d3ca8f3c51e397fd5f6fda625c6.jpg

BASKETBALL IMAGE:
http://image.fg-a.com/sports/large-basketball.gif

BASKETBALL HOOP IMAGE:
http://cdn.shopify.com/s/files/1/0546/0157/products/Net_White.png?v=1448163544

LEBRON BODY:
http://assets.nydailynews.com/polopoly_fs/1.1987042.1414290626!/img/httpImage/image.jpg_gen/derivatives/article_307/netsweight26s-lebron3-web.jpg

LEBRON HEAD:
https://c0bf49af09dabaaf4f81-3c5c7cf439b200c763d8c176f7f8a124.ssl.cf2.rackcdn.com/images/images/4155/photos/large/lebron-james-profile-mouthpiece.jpg_f0046628855ad76148e40fdc9251455a?1371077377

LAKERS COURT IMAGE:
http://i45.tinypic.com/osyb61.png

KOBE IMAGE:
http://i.imgur.com/ZZFIWZ9.png

BUBBLEGUM:
http://wac.450f.edgecastcdn.net/80450F/wyrk.com/files/2011/12/Gum-Bubble.jpg

PORRIDGE IMAGE:
http://www.xteddy.org/porridge/bowl-of-cooked-porridge.jpg

OLIVER IMAGE:
http://www.jonathankettleborough.com/wp-content/uploads/2012/12/Please-sir-may-I-have-some-more.jpg

BOWL IMAGE:
https://cdn0.rubylane.com/shops/741898/Wx2e763.1L.jpg

ORPHANAGE IMAGE:
https://matthaslam.files.wordpress.com/2012/11/roman-polanski-oliver-twist-ben-kingsley.jpg

SESAME STREET IMAGE:
http://www.trbimg.com/img-552d873c/turbine/la-et-st-sesame-street-new-sets-for-46th-season-20150414

COOKIE JAR IMAGE:
http://images.clipartpanda.com/cookie-jar-clipart-cookie.png

COOKIE MONSTER IMAGE:
http://cliparts.co/cliparts/6ip/6Kd/6ip6KdxpT.png

COOKIE IMAGE:
https://www.hamptoncreek.com/img/p-just-cookies/panel-cookie-choc-cookie.png

MICHELLE OBAMA BODY IMAGE:
http://6uh9u7hhy8-flywheel.netdna-ssl.com/wp-content/uploads/2012/09/michelle-obama-dnc-2012-j-crew-tracy-reese.jpg

MICHELLE OBAMA ARM IMAGE:
https://sassandglam.files.wordpress.com/2012/09/michelle-pointing-keivom.jpg

LETTUCE IMAGE:
http://1.bp.blogspot.com/_d5Vg_x-C0_o/SwYi6AJkVAI/AAAAAAAAAC8/VL0iP_dqRAs/s1600/lettuce+myonlineorganic.com.jpg

All code pages used are below (as well as the pygame and python manual pages):

CODE ABOUT GETTING THE ROTATION TO WORK:
http://stackoverflow.com/questions/35272863/pygame-border-of-image-get-cut-while-rotating/35274863

CODE ABOUT GETTING BACKGROUND IMAGE:
http://stackoverflow.com/questions/28005641/how-to-add-a-background-image-into-pygame

CODE ABOUT WRITE FUNCTION PROTOTYPING WE USED INSTEAD OF DEFERRED QUEUE:
http://stackoverflow.com/questions/12469827/sending-pygames-event-data-to-a-twisted-server

CODE ABOUT TEXT ON SCREEN:
https://pythonprogramming.net/displaying-text-pygame-screen/
