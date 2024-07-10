cutscene_dialogues = {
    -1 : """
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
""",
    1 : """
Another day on the job, in the black
void of space, with my trusty paintball
gun and these beautiful, colourful stars. \t
""",
    2 : """
IT'S SO BORING! All I do all day is sit
in this tin can playing AFK Arena, waiting
for someone to need my damn paint.
""",
    3 : """
Don't worry! You still have me! I'm
powered by colour so I'll always stay with
you. \t\tUnless something really bad happens.
""",
    4 : """
What the hell just happened?
It's like the colour of well, everything is
just gone.
""",
    5 : """
Hold on... don't you run on colour?
""",
    6 : """
\t.\t.\t. \t\t\t\tyeah.
"""
}

#removing initial and last \n from the triple quotes
for num in cutscene_dialogues:
    cutscene_dialogues[num] = cutscene_dialogues[num][1:-1]