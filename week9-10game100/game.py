
# computer move
def comp_move (goal, number_cur, number_magic):
    from random import randint
    #check the existence of the winning strategy at current number number_cur
    def is_win_state(goal, number_cur, number_magic):
        return (goal - number_cur) % number_magic != 0

    def move_to_win(goal, number_cur, number_magic):
        move = (goal-number_cur) % number_magic
        number_cur += move
        return number_cur, move
     
    def move_rnd(goal, number_cur, number_magic):
        move_max = min(number_magic-1, goal-number_cur)
        move = randint(1, move_max)
        number_cur += move
        return number_cur, move

    if is_win_state(goal, number_cur, number_magic):
        number_cur, move = move_to_win(goal, number_cur, number_magic)
    else:
        number_cur, move = move_rnd(goal, number_cur, number_magic)
    print('I added ', move, '. The current sum is ', number_cur, sep = '')
    return number_cur
 
# human move
def human_move(number_cur, number_magic):
    import numpy as np
    affordable = np.linspace(1, number_magic-1, number_magic-1)
    num_err_move = 0
    num_err_move_max = 5
    is_err_move = True
    for i in range(num_err_move_max):
        if i > 0:
            print(f'Try again; your number MUST be an integer betwee 1 and {number_magic-1}')
        move = int(float(input(f'Hey, your move: add integer up to {number_magic-1}: ')))
        if move in affordable:
            is_err_move = False
            break;
    number_cur += move
    print('You added ', move, '. The current sum is ', number_cur, sep = '')
    return number_cur, is_err_move 
    
def is_end_game(goal, number_cur, is_human_move):
    if number_cur > goal:
        print(f'Ha! Added too much! The current sum is {number_cur} instead of {goal}')
        print("Let's play again and avoid elementray errors")
        return 1
    elif number_cur == goal and is_human_move:
        print('Congratulation! You win!')
        return 1
    elif number_cur == goal and not is_human_move:
        print('You lost! Thank you for the game!')
        return 1
    else:
        return 0
        
