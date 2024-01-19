import grpc
from concurrent import futures
import order_pb2
import order_pb2_grpc
import time

class OrderServicer(order_pb2_grpc.OrderServicer):
    def CreateOrder(self, request, context):
        # Extract information from request
        name = request.name
        surname = request.surname
        phone = request.phone
        address = request.address
        items = request.items  # This is a list of OrderItem
        # TODO: Store order in the database
        # For now, let's just print the order details
        print(f"Creating order for {name} {surname}")
        for item in items:
            print(f"Item ID: {item.itemId}, Quantity: {item.quantity}, Price: {item.price}")

        # Return a response
        return order_pb2.OrderResponse(
            orderId="12345",
            success=True,
            message="Order created successfully"
        )

def GetOrder(self, request, context):
    # Implement logic to retrieve an order
    # For now, let's just return a placeholder response
    return order_pb2.OrderResponse(
        orderId=request.orderId,
        success=True,
        message="Order retrieved successfully"
    )

def UpdateOrder(self, request, context):
    # Implement logic to update an order
    # For now, let's just return a placeholder response
    return order_pb2.OrderResponse(
        orderId=request.orderId,
        success=True,
        message="Order updated successfully"
    )


def DeleteOrder(self, request, context):
    # Implement logic to delete an order
    # For now, let's just return a placeholder response
    return order_pb2.OrderResponse(
        orderId=request.orderId,
        success=True,
        message="Order deleted successfully"
    )

    # Add more methods as needed

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    order_pb2_grpc.add_OrderServicer_to_server(OrderServicer(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == "__main__":
    serve()