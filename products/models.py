from django.db import models

# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=120)
    image = models.ImageField(upload_to='products',default='no_image.jpg')
    price = models.FloatField(help_text='In USD $')
    description = models.TextField(default = 'This is awesome', help_text='Add product description')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.name}-{self.created.strftime('%d/%m%Y')}"
        