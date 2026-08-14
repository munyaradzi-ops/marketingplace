from django.db import models
from products.models import Product

class StockAuditLog(models.Model):
    AUDIT_TYPES = (
        ('RESTOCK', 'Manual Restock Inflow'),
        ('CORRECTION', 'Inventory Audit Adjustment'),
        ('DAMAGE', 'Damaged/Loss Write-off'),
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='audit_logs')
    change_quantity = models.IntegerField(help_text="Positive for additions, negative for reductions")
    reason = models.CharField(max_length=20, choices=AUDIT_TYPES, default='RESTOCK')
    cost_per_unit = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Wholesale purchase cost")
    logged_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.reason} - {self.product.name} ({self.change_quantity})"

class OperationalExpense(models.Model):
    title = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    category = models.CharField(max_length=100, choices=(('SHIPPING', 'Logistics'), ('SERVER', 'Hosting/IT'), ('MARKETING', 'Ads/Promo'), ('MISC', 'Other overheads')))
    date_incurred = models.DateField()
    


    def __str__(self):
        return f"{self.title} - ${self.amount}"
    
    
class DeveloperPayout(models.Model):
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, help_text="Amount sent to the developer")
    payout_date = models.DateField(help_text="Date the transaction was executed")
    # Changed placeholder to help_text below:
    reference_note = models.CharField(max_length=255, blank=True, null=True, help_text="e.g. Bank Transfer Ref / EcoCash ID")

    def __str__(self):
        return f"Payout of ${self.amount_paid} on {self.payout_date}"

    
    
