import threading
import time
import random
import numpy as np
from matplotlib import pyplot
from matplotlib.animation import FuncAnimation
from network import Network

# create the payment channel network
Lightning_Network = Network("Lightning")

# create routing nodes R1, R2, R3, R4
R1 = Lightning_Network.register_node("R1", 1)
R2 = Lightning_Network.register_node("R2", 1)
R3 = Lightning_Network.register_node("R3", 1)
R4 = Lightning_Network.register_node("R4", 1)

# create channels among routing nodes in a loop
R1.create_channel(R2, 30, 60)
R2.create_channel(R3, 30, 60)
R3.create_channel(R4, 30, 60)
R4.create_channel(R1, 30, 60)

# create attacker node and add channel to R1
Attacker_V1 = Lightning_Network.register_node("Attacker_V1", 0)
Attacker_V1.create_channel(R1, 100, 200)

# create two external nodes E1, E2
E1 = Lightning_Network.register_node("E1", 1)
E2 = Lightning_Network.register_node("E2", 1)
# connect E1 and E2 with all the routing nodes
E1.create_channel(R1, 100, 200)
E1.create_channel(R2, 100, 200)
E1.create_channel(R3, 100, 200)
E1.create_channel(R4, 100, 200)
E2.create_channel(R1, 100, 200)
E2.create_channel(R2, 100, 200)
E2.create_channel(R3, 100, 200)
E2.create_channel(R4, 100, 200)

# plot generation 
x_data, y_data = [0], [0]
figure = pyplot.figure()
line, = pyplot.plot(x_data, y_data, 'o-')

global total_transactions, successfull_transactions
total_transactions = 0
successfull_transactions = 0

def run_honest_node(
            start=None,
            end=None, 
            routers=None
        ):
    # time.sleep(5)
    global total_transactions, successfull_transactions
    direction = 1
    while True:
        index = random.randint(0, 3)
        route = [start, routers[index], routers[(index+1)%4], routers[(index+2)%4], end]
        # # reverse the direction of payment with 50% probability
        amount = 5
        if not direction%6:
            amount = 20
            route = route[::-1]
        direction += 1
        if start.pay(route, amount):
            successfull_transactions += 1
        total_transactions += 1
        print("# Total Transactions = ", total_transactions)
        print("# Successfull Transactions = ", successfull_transactions)
        
        # plotting the graph
        x_data.append(total_transactions)
        y_data.append(total_transactions-successfull_transactions)
        
        time.sleep(2)

def run_attacker_node(
            node=None, 
            routers=None
        ):
    time.sleep(5)
    route = [node] + routers + [routers[0]] + [node]
    while True:
        val = 1000
        for index in range(len(route)-1):
            node = route[index]
            next_node = route[index+1]
            val = min(val, node.payment_channels[next_node])
        if val > 5:
            print("##### Attempting payment From: Attacker ##### ", val)
            node.pay(route, val-5)
            print(Lightning_Network.graph)
    return    

routers = [R1, R2, R3, R4]
honest_transactions = threading.Thread(
    target = run_honest_node,
    args = (E1, E2, routers,)
)
malicious_transactions = threading.Thread(
    target = run_attacker_node,
    args = (Attacker_V1, routers,)
)
honest_transactions.start()
malicious_transactions.start()

def update(frame):
    line.set_data(x_data, y_data)
    figure.gca().relim()
    figure.gca().autoscale_view()
    return line,

animation = FuncAnimation(figure, update, interval=200)
pyplot.show()