from django.db import models

# Create your models here.
class Config(models.Model):
    name = models.CharField(max_length=255)
    image = models.FileField(upload_to='')
    #json = models.CharField(max_length=255)
    upload_time = models.DateTimeField(auto_now_add=True)

    #def __str__(self):
    #    return "Config: name={}, image={}, upload_time={}".format(self.name, self.image, self.upload_time)