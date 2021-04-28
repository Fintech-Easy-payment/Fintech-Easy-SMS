from django.db import models


class Product(models.Model):
    product_id = models.SmallIntegerField(primary_key=True)
    product_name = models.CharField(max_length=50, blank=True, null=True)
    price = models.IntegerField(blank=True, null=True)


class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    email = models.CharField(max_length=50, blank=True, null=True)
    password = models.CharField(max_length=30, blank=True, null=True)
    name = models.CharField(max_length=30, blank=True, null=True)
    phone = models.CharField(max_length=11, blank=True, null=True)
    access_token = models.TextField(blank=True, null=True)
    refresh_token = models.TextField(blank=True, null=True)
    user_seqnum = models.CharField(max_length=50, blank=True, null=True)


class UserProduct(models.Model):
    user_product_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="user",
                                db_index=True)
    product_id = models.ForeignKey(Product, null=True, blank=True, on_delete=models.SET_NULL, related_name="product",
                                   db_index=True)
    start_date = models.DateField(blank=True, null=True)
    exr_date = models.DateField(blank=True, null=True)
