class Node:
    def __init__(
                self, 
                name=None, 
                routing_fee=None,
                network=None
            ):
        self.name = name
        # payment_channels = {neighbor:current_balance}
        self.payment_channels = {}
        self.routing_fee = routing_fee
        self.network = network

    def create_channel(
                self, 
                node=None, 
                balance=None,
                capacity=None
            ):
        self.payment_channels[node] = balance
        node.payment_channels[self] = capacity-balance
        route = [self, node]
        self.network.update_graph(route)
    
    def pay(
                self, 
                route=None, 
                amount=None
            ):
        status = self.network.post_transaction(route, amount)
        if status:
            self.network.update_graph(route)
        print("Payment Status : ", status, " for :", route[0].name)
        return status