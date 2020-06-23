######################################################
################## load libraries ####################
######################################################
import sys
import math
import time
import random
import numpy as np



######################################################
################## Global Variables ##################
######################################################
#dictionary to keep track of Humans
current_strategy_score = 0
current_strategy = []
score = 0
random_human_bool = False
time_limit = 1
n_main_turn = 0
######################################################
################## Define Classes ####################
######################################################

class Game_Simulator():
    def __init__(self,arr_zombies,arr_zombies_next,arr_humans):
        #initialising game
        self.init_zombies = arr_zombies #id, x, y
        self.init_humans = arr_humans #id, x, y #first one is always ash.
      

        self.init_n_zombies = len(arr_zombies)
        self.init_n_humans =  len(arr_humans)-1

        #game constants:
        self.game_dim_x = 16000
        self.game_dim_y = 9000
        self.gun_radius = 2000
        self.gun_radius_squared = 4000000
        self.speed_ash = 1000
        self.speed_zombie = 400

        #store best score and action
        self.best_score = 0
        self.best_action = arr_humans[1,1:3] #x, y 


    def get_next_game_state(self,current_state):
      '''Output: next state'''
      id_zombie = 0
      id_human = 1

      arr_current_zombie = current_state[id_zombie]
      arr_current_human = current_state[id_human]
      #calculate distance squared to all humans, find minimum.
      arr_dist_squared = m_distance_squared(arr_current_zombie[:,1:3],
                                            arr_current_human[:,1:3])
      
      #### Check dead zombies ####      
      #check if any zombies are within ash range. 
      bool_c_zombies=arr_dist_squared[:,0] > self.gun_radius_squared

      #update distance array
      arr_dist_squared=arr_dist_squared[bool_c_zombies]

      #update zombie array
      arr_current_zombie=arr_current_zombie[bool_c_zombies]

      #update n zombies      
      zombies_left = sum(bool_c_zombies)
      #get kills this turn
      self.n_kills = self.n_zombies - zombies_left
      #update remaining zombies. 
      self.n_zombies = zombies_left
      if self.n_zombies == 0:
          return False

      ### check score ###

      #### Find Next ZOMBIE location ####
      #get ids of minimum distance human.
      arr_chuman_ids = np.argmin(arr_dist_squared, axis=1)
      
      #get real distance of min dist humans. need to take square root.
      arr_zh_distance = np.sqrt(np.min(arr_dist_squared, axis=1))

      #get zombie destinations
      arr_zombie_dest = current_state[id_human][arr_chuman_ids,1:3] #  closest human[x,y]       
      next_arr_zombies = arr_current_zombie
      #find next locations for zombies
      next_arr_zombies[:,1:3] = m_get_next_locations(speed = self.speed_zombie,
                                              distance = arr_zh_distance,
                                              start_loc = arr_current_zombie[:,1:3],
                                              dest_loc = arr_zombie_dest)
      #convert array to int
      #next_arr_zombies = next_arr_zombies.astype(int)
      #next_arr_zombies = next_arr_zombies
      #### Check dead humans ####

      #check for dead humans. update human array    
      dead_ids = arr_chuman_ids[arr_zh_distance < self.speed_zombie]
      #print("dead human ids", dead_ids)
      next_arr_humans = np.delete(arr_current_human, dead_ids, axis=0)

      #update number of live humans
      self.n_humans -= len(dead_ids)


      #### Find Next ASH location ####
      #get ash location. 
      self.get_action(next_arr_zombies,arr_current_human)

      # get new ash_loc
      ash_loc=np.array([arr_current_human[0,1:3]])
      #print(["ash_loc",ash_loc,"self.action",self.action], file=sys.stderr)
      next_ash_loc = get_next_locations(speed = self.speed_ash,
                                        distance = m_distance(ash_loc,self.action),
                                        start_loc = ash_loc,
                                        dest_loc = self.action) 
            
      #update arr humans with ash loc. 
      #next_arr_humans[0,1:3] = next_ash_loc.astype(int)
      next_arr_humans[0,1:3] = next_ash_loc

      
      #### Generate  next state ####
      next_state = [next_arr_zombies,next_arr_humans]

      return next_state
    
    def get_action(self,zombie_array,human_array):
      #random x, y
      #check if at the action locatiion 
      if self.game_turn < self.n_random_moves:
          move_x = random.randrange(0,self.game_dim_x+1,1)
          move_y = random.randrange(0,self.game_dim_y+1,1)
          self.action=[move_x,move_y]
      elif self.target == True:
          self.action = self.action
      elif self.best_score == 0:
          human_id=random.randrange(0,len(human_array),1)
          move_x = human_array[human_id,1]
          move_y = human_array[human_id,2]
          self.target = True
          self.action=[move_x,move_y]
      else:
          zom_id=random.randrange(0,len(zombie_array),1)
          move_x = zombie_array[zom_id,1]
          move_y = zombie_array[zom_id,2]
          self.action=[move_x,move_y]
      #return action 

    #def get_reward(self):
    #  self.total_reward += score
    #  return score

    def check_game_end(self,n_turns):
      #if all humans dead
      if self.n_humans  == 0:
        self.total_score = 0 
        return True
      elif self.n_zombies == 0:
        return True
      else:
        return False

    def simulate_n_turns(self,random_moves,n_turns):
      ### reset_game 
      game_over = False
      self.target = False
      self.total_score = 0
      self.game_turn = 0
      self.actions = []
      self.n_random_moves = random_moves
      ### get first state
      self.n_zombies = self.init_n_zombies
      self.n_humans = self.init_n_humans
           
      current_state = [self.init_zombies,self.init_humans]

      while game_over == False:
        #print("start game over",game_over)
        reward = 0
        self.n_kills = 0
        start_turn_humans = len(current_state[1])-1
       
        #get ash action
        #action = self.get_action()
        #action = current_state[1][1,1:3]
        #actions.append(action)

        #update ash_loc next location ash
        next_state = self.get_next_game_state(current_state)

        #check kills get reward
        reward=total_turn_score(start_turn_humans,self.n_kills)
        self.action_reward=self.action[:]
        self.action_reward.append(reward)
        self.actions.append(self.action_reward)
        #self.scores.append(reward)
        self.total_score +=reward

        #check if game over
        game_over = self.check_game_end(n_turns)
        if self.game_turn >= n_turns:
          game_over = True

        if game_over:
            
            if self.best_score < self.total_score:
                self.best_score = self.total_score
                self.best_actions = self.actions
                self.best_action = self.actions[0]
          

        else:
          #update state
          current_state = next_state
        
        self.game_turn+=1
        

######################################################
################## Functions #########################
######################################################

#get distances for two points
def distance_squared(x1,y1,x2,y2):
    return (x1 - x2)**2 + (y1 - y2)**2

def distance(x1,y1,x2,y2):
    return maths.sqrt((x1 - x2)**2 + (y1 - y2)**2)

#get distances for arrays.  
def m_distance_squared(arr_origin,arr_destination):
    arr_squared=np.square(arr_origin[:,None]-arr_destination)
    return np.sum(arr_squared,axis=2)

def m_distance(arr_origin,arr_destination):
    arr_squared=np.square(arr_origin[:,None]-arr_destination)
    arr_sum=np.sum(arr_squared,axis=2)
    return np.sqrt(arr_sum)


def get_turn_distance(distance_in,speed,gun_radius):
    distance=distance_in - gun_radius
    if distance < 0:
      return 0
    else:
      return distance/speed#math.ceil(distance/speed)

def get_next_locations (speed,distance, start_loc,dest_loc):
    if speed/distance > 1:
      return np.array(dest_loc)
    else:
      output = start_loc + speed / distance * (dest_loc - start_loc)
      return output.astype(int)

def m_get_next_locations (speed,distance, start_loc,dest_loc):
    s_d = speed / distance
    output = start_loc + s_d[:,None] * (dest_loc - start_loc)
    
    #check if speed bigger than distance
    bool_sd=s_d > 1
    #replace output loc, with destination loc if speed bigger than distance. 
    output[bool_sd]=dest_loc[bool_sd]
    
    return output.astype(int)



fibonacci_list =  [0, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987, 1597, 2584, 4181, 6765, 10946, 17711, 28657, 46368, 75025,
 121393, 196418, 317811, 514229, 832040, 1346269, 2178309, 3524578, 5702887, 9227465, 14930352, 24157817, 39088169, 63245986]

#takes the value of killed zombies this turn.
def fibonacci(z_killed):
    n1,n2=0,1
    nth=0
    nth_value = z_killed
    f_counter=0
    #for nth_value in range(get_nth_value):
    while f_counter < nth_value:
        nth = n1 + n2
        # update values
        n1 = n2
        n2 = nth
        f_counter += 1
    return nth


#calculate worth of killing zombie. inputs are currently alive humans and zombies killed this turn.
def zombie_worth(alive_humans,z_killed):
    base_worth=10*alive_humans**2 
    #return base_worth * fibonacci(z_killed)
    return base_worth * fibonacci_list[z_killed] #fibonacci(z_killed)



#calculate total worth for all zombies
def total_turn_score(alive_humans,total_killed):
    turn_score = 0
    for current_zombie in range(1,total_killed+1):
        turn_score += zombie_worth(alive_humans,current_zombie)
    return turn_score

# game loop
while True:
    start_time = time.time()
    #print(["start turn score",score], file=sys.stderr)
    #make empty lists for humans and zombies.
    arr_humans = []
    arr_zombies = []

    x, y = [int(i) for i in input().split()]
    #add ash as first person in humans. 
    arr_humans.append([0,x,y])

    human_count = int(input())
    for i in range(human_count):
        human_id, human_x, human_y = [int(j) for j in input().split()]
        arr_humans.append([(human_id+1), human_x, human_y]) 
    #add humans turn to np array. 
    arr_humans=np.array(arr_humans)

    zombie_count = int(input())
    for i in range(zombie_count):
        zombie_id, zombie_x, zombie_y, zombie_xnext, zombie_ynext = [int(j) for j in input().split()]
        arr_zombies.append([zombie_id, zombie_x, zombie_y, zombie_xnext, zombie_ynext])
    #add zombies turn into array. 
    arr_zombies=np.array(arr_zombies)

    #simulate game.     
    game_sim = Game_Simulator(arr_zombies[:,0:3],arr_zombies[:,3:5],arr_humans[:,0:3])
    
    current_time = time.time()
    elapsed_time = current_time - start_time
    n_loop=0
    while elapsed_time < time_limit:
        n_loop+=1
        game_sim.simulate_n_turns(5,30)
        current_time = time.time()
        elapsed_time = current_time - start_time
    time_limit = 0.0999
    #n_main_turn +=1
    print(["loops",n_loop], file=sys.stderr)
    print(["game_sim.best_score",game_sim.best_score], file=sys.stderr)
    
    #output best action from game simlator.
    
    if (game_sim.best_score + score) > current_strategy_score:
        #if (game_sim.best_score) > sum(np.array(current_strategy)[:,2]):
        current_strategy_score = game_sim.best_score
        current_strategy = game_sim.best_actions
    if len(current_strategy) == 0:
        if random_human_bool == False:
            random_human=random.randint(1,human_count)
            print(["random_human",random_human], file=sys.stderr)
            random_human_bool = True
            human_x_1=arr_humans[random_human,1] 
            human_y_1=arr_humans[random_human,2]

        current_strategy = np.array([[human_x_1, human_y_1, 0]])

    print(["current_strategy_score",current_strategy_score], file=sys.stderr)
    print(["current_strategy",current_strategy], file=sys.stderr)
    print(["current_strategy",sum(np.array(current_strategy)[:,2])], file=sys.stderr)
    next_move = current_strategy[0]
    current_strategy=np.delete(current_strategy,0,axis=0)
    print(["next_move",next_move],file=sys.stderr)
    
    print(str(next_move[0]) +" " + str(next_move[1])) 
    #score += current_strategy[1][2] 
    print(["end turn score",score], file=sys.stderr)

    #print(str(game_sim.best_action[0]) +" " + str(game_sim.best_action[1]))
    # Your destination coordinates

