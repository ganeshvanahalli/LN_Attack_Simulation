from node import Node

class Network:
    def __init__(
                self,
                name = None
            ):
        self.name = name
        self.total_transactions = 0
        self.successfull_transactions = 0
        self.graph = {}

    def update_graph(
                self, 
                route=None
            ):
        for index in range(len(route)-1):
            node = route[index]
            next_node = route[index+1] 
            self.graph[node.name][next_node.name] = node.payment_channels[next_node]
            self.graph[next_node.name][node.name] = next_node.payment_channels[node]

    def register_node(
                self, 
                name=None, 
                routing_fee=None
            ):
        node = Node(name, routing_fee, self)
        self.graph[name] = {}
        return node

    def validate_route(
                self, 
                route=None, 
                amount=None
            ):
        
        # check if the following node is in current node's channel list
        for index in range(len(route)-1):
            node = route[index]
            next_node = route[index+1] 
            if next_node not in node.payment_channels:
                return -1
        
        # check if the nodes have enough balance in there payment channels
        for index in range(len(route)-2, 0, -1):
            node = route[index]
            next_node = route[index+1] 
            if node.payment_channels[next_node] < amount:
                return -1
            # add the current node's routing fees to the amount 
            # that the previous node is supposed to send with 
            amount += node.routing_fee
        return amount
    
    def instant_transfer(
                self, 
                route=None, 
                amount=None
            ):
        for index in range(len(route)-1):
            node = route[index]
            next_node = route[index+1] 
            node.payment_channels[next_node] -= amount
            next_node.payment_channels[node] += amount
            amount -= next_node.routing_fee

    def post_transaction(
                self, 
                route=None, 
                amount=None
            ):
        self.total_transactions += 1
        amount = self.validate_route(route, amount)
        if amount == -1:
            return False
        self.instant_transfer(route, amount)
        self.successfull_transactions += 1
        return True
