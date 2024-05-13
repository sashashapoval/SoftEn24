
from random import randint
import numpy as np

class game_of_one_hundred():
    
    def __init__(self, goal=100, number_max_avail=10, number_cur=0):
        self.goal = goal
        self.number_cur = number_cur
        self.number_magic = number_max_avail+1

    #check the existence of the winning strategy at current number number_cur
    def is_win_state(self):
        return (self.goal - self.number_cur) % self.number_magic != 0
    
    #winning move; assumed that it exists
    def move_to_win(self):
        move = (self.goal-self.number_cur) % self.number_magic
        self.number_cur += move
        return self.number_cur, move

    def move_rnd(self):
        move_max = min(self.number_magic-1, self.goal-self.number_cur)
        move = randint(1, move_max)
        self.number_cur += move
        return self.number_cur, move
    
     # computer move
    def comp_move (self):
        number_cur, goal, number_magic = self.number_cur, self.goal, self.number_magic
        if self.is_win_state():
            number_cur, move = self.move_to_win()
        else:
            number_cur, move = self.move_rnd()
        print('I added ', move, '. The current sum is ', number_cur, sep = '')
        return
    
    def human_move(self):
        number_cur, goal, number_magic = self.number_cur, self.goal, self.number_magic
        affordable = np.linspace(1, number_magic-1, number_magic-1)#creates np.array [1,...,(number_magic-1)]
        num_err_move = 0
        num_err_move_max = 5 #maximal number of error attempts to make an eligible move
        is_err_move = True
        for i in range(num_err_move_max):
            if i > 0:
                print(f'Try again; your number MUST be an integer between 1 and {number_magic-1}')
            #to imporve
            try:
                human_move = int(input(f'Hey, your move: add integer up to {number_magic-1}: '))
                if human_move in affordable:
                    is_err_move = False
                    break;
            except:
                pass
        if is_err_move: #Player failed to choose a correct number
            human_move = 1
        number_cur += human_move
        print('You added ', human_move, '. The current sum is ', number_cur, sep = '')
        return number_cur, is_err_move       
    
    def is_end_game(self, is_human_move):
        if self.number_cur > self.goal:
            print(f'Ha! Added too much! The current sum is {self.number_cur} instead of {self.goal}')
            print("Let's play again and avoid elementray errors")
            return True
        elif self.number_cur == self.goal and is_human_move:
            print('Congratulation! You win!')
            return True
        elif self.number_cur == self.goal and not is_human_move:
            print('You lost! Thank you for the game!')
            return True
        else:
            return False
        
    def play(self):
        is_human_move = bool(int(float(input(f'If you want to start type 1. Otherwise, type 0: '))))
        if not is_human_move:
            self.comp_move() #self.number_cur is changed inside the function
            if not self.is_end_game(is_human_move):
                is_human_move = True
        while self.number_cur < self.goal:
            self.number_cur, is_err_move = self.human_move()
            if is_err_move:
                print('Sorry, you failed to choose a correct move')
            if not self.is_end_game(is_human_move):
                is_human_move = False
                self.comp_move()
                if not self.is_end_game(is_human_move):
                    is_human_move = True

