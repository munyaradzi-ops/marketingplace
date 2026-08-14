from django.db import models
from products.models import Product

class Order(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    address = models.CharField(max_length=250)
    postal_code = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    paid = models.BooleanField(default=False)
    # ENSURE THIS EXACT FIELD LINE IS INSIDE THE ORDER CLASS HERE:
    delivered = models.BooleanField(default=False, help_text="Designates if shipment has arrived at consumer address")

    

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return f'Order {self.id}'

    def get_total_cost(self):
        # Explicit conversion wrapper ensures template calculations never crash silently
        from decimal import Decimal
        return sum(Decimal(str(item.get_cost())) for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    paid = models.BooleanField(default=False)
    # ENSURE THIS EXACT FIELD LINE IS INSIDE THE ORDER CLASS HERE:
    delivered = models.BooleanField(default=False, help_text="Designates if shipment has arrived at consumer address")


    def __str__(self):
        return str(self.id)

    def get_cost(self):
        from decimal import Decimal
        # Fallback security ensures null prices evaluate safely to 0.00
        item_price = Decimal(str(self.price)) if self.price else Decimal('0.00')
        item_quantity = int(self.quantity) if self.quantity else 1
        return item_price * item_quantity
