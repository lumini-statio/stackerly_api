from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from datetime import date, datetime

from api.managers import CustomUserManager


class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    objects = CustomUserManager()

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser

    def __str__(self):
        return f'{self.username} - {self.email}'


class Location(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return str(self.name)
    

class BalanceBox(models.Model):
    current_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    last_updated = models.DateTimeField(auto_now=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='balances')

    def calculate_amount(self) -> float:
        amount_spent = Purchase.objects.filter(
            related_store__balance=self).aggregate(total=models.Sum('spent'))['total'] or 0
        
        return float(amount_spent)

    def __str__(self):
        return f'Balance: {self.current_amount} (Last updated: {self.last_updated.strftime("%Y-%m-%d %H:%M:%S")})'


class Store(models.Model):
    name = models.CharField(max_length=100)
    balance_box = models.ForeignKey(BalanceBox, on_delete=models.CASCADE, related_name='stores')
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='stores')

    def __str__(self):
        return f'{self.name} - {self.location}'
    

class ProfitLossRecord(models.Model):
    RECORD_TYPE_CHOICES = [
        ('INCOME', 'Income'),
        ('EXPENSE', 'Expense')
    ]

    date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    record_type = models.CharField(max_length=7, choices=RECORD_TYPE_CHOICES)
    related_store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='profit_loss_record')

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f'{self.record_type} of ${self.amount} on {self.date}'
    

class Purchase(models.Model):
    purchased_item = models.CharField(max_length=50)
    spent = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField()
    related_store = models.ForeignKey(Store, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        is_new = self.pk is None

        super().save(*args, **kwargs)

        if is_new:
            bb = self.related_store.balance_box
            bb.current_amount -= self.spent
            bb.save()

            ProfitLossRecord.objects.create(
                date=datetime.now(),
                amount=self.spent,
                record_type=ProfitLossRecord.RECORD_TYPE_CHOICES[1][0],
                related_store=self.related_store
            )
    
    def __str__(self):
        return f'purchase {self.id} - spent {self.spent} for {self.purchased_item}'

    class Meta:
        ordering = ['-date']
    

class ProductState(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def builder(cls):
        state = cls.objects.get_or_create(name='Available')
        return state

    def __str__(self):
        return self.name
    

class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(max_length=50)
    model = models.CharField(max_length=50, blank=True, null=True)
    quantity = models.PositiveIntegerField()
    related_store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='products')
    state = models.ForeignKey(ProductState, on_delete=models.CASCADE)
    last_updated_state = models.DateField(auto_now=True)

    def can_change_state(self):
        if self.state.name == 'Delivered':
            time_diff = self.last_updated_state - date.today()

            if time_diff.days > 30:
                return False
        
        return True
    
    def change_state(self, new_state):
        if self.can_change_state():
            self.state = new_state
            self.last_updated_state = date.today()
            self.save()
        else:
            raise ValueError("Cannot change state due to restrictions.")
        
    def save(self, *args, **kwargs):
        is_new = self.pk is None

        super().save(*args, **kwargs)

        if is_new:
            Purchase.objects.create(
                purchased_item=self.name,
                spent=self.price*self.quantity,
                date=datetime.now(),
                related_store=self.related_store
            )

    def __str__(self):
        return f'{self.name} - {self.state}'
    

class UserPurchase(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    
    def if_can_subtract_then_do_it(self, quantity):
        """
        check if you can subtrack product quantity with user purchase quantity
        """
        if (quantity - self.quantity) < 0:
            raise ValueError("Stock quantity can't be less than 0")
        else: quantity - self.quantity

    def save(self, *args, **kwargs):
        """
        Modify the balance box, quantity ,product state, register a balance.
        """
        if self.product.quantity < self.quantity:
            raise ValueError("No hay suficiente stock disponible.")
        self.product.quantity -= self.quantity

        if self.product.quantity == 0:
            self.product.state = ProductState.objects.get_or_create(name='Not Available')[0]

        self.product.save()

        bb = self.product.related_store.balance_box
        bb.current_amount += self.product.price * self.quantity
        bb.save()

        ProfitLossRecord.objects.create(
            date=datetime.now(),
            amount=self.product.price * self.quantity,
            record_type=ProfitLossRecord.RECORD_TYPE_CHOICES[0][0],
            related_store=self.product.related_store
        )

        super().save(*args, **kwargs)
        

    def __str__(self):
        return f'Product: {self.product}'
    

class Order(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    date = models.DateTimeField()

    def __str__(self):
        return f'Order:{self.id} - {self.date.strftime("%Y-%m-%d %H:%M")}'
