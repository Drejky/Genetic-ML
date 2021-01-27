import random
from copy import deepcopy, copy
import timeit

adrMask = 63    #mask to get our addr bits
cmdMask = 192   #mask to get our command bits
stepLim = 500   #Limited num of instructions 

tourFlag = int(input("Input 1 for tournament, 0 for roulette"))
mixFlag = int(input("Input 1 for mixed children, 0 for halfnhalf"))
popLim = int(input("Input the ammount of individuals in each gen"))

#Commands:
#0 - increment 
#64 - decrement
#128 - jump
#192 - print

uwu = [
    ['b', 'b', 'b', 'b', 'b', 'b', 'b'],
    ['b', 'b', 'b', 'b', 'g', 'b', 'b'],
    ['b', 'b', 'g', 'b', 'b', 'b', 'b'],
    ['b', 'b', 'b', 'b', 'b', 'b', 'g'],
    ['b', 'g', 'b', 'b', 'b', 'b', 'b'],
    ['b', 'b', 'b', 'b', 'g', 'b', 'b'],
    ['b', 'b', 'b', 's', 'b', 'b', 'b']
]

#Finds number in 2D array
def findNum(arr, num):
    for i in arr:
        try:
            j = i.index(num)
            return j, arr.index(i)
        except ValueError:
            continue
#Counts the number of treasures in map
def getGc(arr):
    c = 0
    for i in arr:
        for j in i:
            if j == 'g':
                c += 1
    return c

startx, starty = findNum(uwu, 's')
gc = getGc(uwu)

class individual:
    def __init__(self):
        self.mem = []
        self.fitness = 100
    def randomize(self):
        for i in range(64):
            self.mem.append(random.randrange(0, 255))

#Opperations on memmory cells
def increment(x):
    if(x == 255):
        return 0
    return x + 1
def decrement(x):
    if(x == 0):
        return 255
    return x - 1
def addrUp(x):
    if x == 63:
        return 0
    return x + 1
def getCom(x):
    masked = x & 3
    if masked == 0:
        return 'H'
    elif masked == 1:
        return 'D'
    elif masked == 2:
        return 'P'
    else:
        return 'L'

#Checks if bot went out of bounds
def checkOutBounds(arr, x, y):
    if y < 0 or y >= len(arr):
        return True
    elif x < 0 or x >= len(arr[0]):
        return True
    else:
        return False

#Program for our individuals
def vm(x, prin):
    grid = deepcopy(uwu)
    stepCount = 0
    addr = 0
    posx = startx
    posy = starty
    while(stepCount < stepLim):
        stepCount += 1

        #Increment cell
        if x.mem[addr] & cmdMask == 0:
            x.mem[x.mem[addr] & adrMask] = increment(x.mem[x.mem[addr] & adrMask])
            addr = addrUp(addr) 
            continue

        #Decrement cell
        elif x.mem[addr] & cmdMask == 64:
            x.mem[x.mem[addr] & adrMask] = decrement(x.mem[x.mem[addr] & adrMask])
            addr = addrUp(addr)
            continue
            
        #Jump address
        elif x.mem[addr] & cmdMask == 128:
            addr = x.mem[addr] & adrMask
            continue

        #Do a step
        else:
            x.fitness -= 1
            masked = x.mem[x.mem[addr] & adrMask] & 3   #creating mask representing move direction
            if masked == 0:     #move up
                posy -= 1
            elif masked == 1:   #move down
                posy += 1
            elif masked == 2:   #move right
                posx += 1
            else:               #move left
                posx -= 1

            if checkOutBounds(grid, posx, posy):
                return x.fitness
            elif grid[posy][posx] == 'g':
                x.fitness += 100
                grid[posy][posx] = 'b'
            #If the prin flag is raised, print out individuals path
            if prin:
                print(getCom(x.mem[x.mem[addr] & adrMask]))
            addr = addrUp(addr)
    return x.fitness

#Breeding functions
def halfnhalf(par1, par2):
    child = individual()
    rand = random.randrange(64)
    for i in range(rand):
        child.mem.append(par1.mem[i])
    for i in range(rand, 64):
        child.mem.append(par2.mem[i])
    
    return child
def mixChild(par1, par2):
    child = individual()
    for i in range(64):
        if random.randrange(2) == 1:
            child.mem.append(par1.mem[i])
        else:
            child.mem.append(par2.mem[i])

    return child

#Selection functions
def roulete(gen):
    sum = 0
    rand = random.random()
    last = 0

    for i in gen:
        sum += i.fitness
    
    for i in gen:
        if rand < (last + (i.fitness/sum)):
            return i
        else:
            last += i.fitness/sum 
def roulMakeChild(gen):
    x = roulete(gen)
    y = roulete(gen)

    while(x == y):
        y = roulete(gen)

    if(mixFlag == 1):
        return mixChild(x, y)    
    else:
        return halfnhalf(x, y)
def tournament(gen):
    x = gen[random.randrange(0, popLim)]
    y = gen[random.randrange(0, popLim)]

    while(x == y):
        y = gen[random.randrange(0, popLim)]

    if(x.fitness > y.fitness):
        return x
    else:
        return y
def tournamentChild(gen):
    x = tournament(gen)
    y = tournament(gen)

    while(x == y):
        y = tournament(gen)
    
    if(mixFlag == 1):
        return mixChild(x, y)    
    else:
        return halfnhalf(x, y)

#Mutation
def mutate(indi):
    rand = random.random()
    #print(rand)
    if rand < 0.1:
        return indi
    elif rand > 0.9:
        indi.randomize()
        return indi
    else:
        for i in range(63):
            if random.randrange(0,40) == 1:
                indi.mem[i] = random.randrange(0, 255)
        return indi
    
def main():
    pop = 1
    gen = []
    newGen = []
    genLim = int(input("Input the ammount of generations"))
    
    #First individual set as elite
    gen.append(individual())
    gen[0].randomize()
    gen[0].fitness = vm(deepcopy(gen[0]), 0)
    elite = deepcopy(gen[0])

    #Populating first generation
    for i in range(1, popLim):
        gen.append(individual())
        gen[i].randomize()
        gen[i].fitness = vm(deepcopy(gen[i]), 0)
        if(gen[i].fitness > elite.fitness):
            elite = deepcopy(gen[i])
        
    #Creating new generations
    while pop <= genLim:
        print("=========================")
        sumFit = 0
        newGen.append(elite)
        for i in range(1, popLim):
            if(tourFlag):
                newGen.append(tournamentChild(gen))
            else:
                newGen.append(roulMakeChild(gen))
            newGen[i] = mutate(newGen[i])
            newGen[i].fitness = vm(deepcopy(newGen[i]), 0)
            #print(newGen[i].fitness)
            if(newGen[i].fitness > elite.fitness):
                elite = deepcopy(newGen[i])
            sumFit += newGen[i].fitness
            if(newGen[i].fitness > 100*gc):
                print(pop)
                vm(deepcopy(newGen[i]), 1)
                return
        print("Average {} gen: {}".format(pop, sumFit / popLim))
        gen.clear()
        gen = copy(newGen)
        newGen.clear()
        pop += 1

        if pop == genLim:
            if int(input("Write one for another 100 generations")):
                genLim += 100

start = timeit.default_timer()
main()
stop = timeit.default_timer()
print("It took {:.4f} to run.".format(stop - start))
