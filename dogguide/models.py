from django.db import models

# Create your models here;
class DogGuide(models.Model):
    guide_title = models.CharField()
    guide_content = models.CharField()
    pet_type = models.CharField()
    image = models.ImageField()
    
    def __str__(self) -> str:
        return self.guide_title
    
    class Meta:
        db_table = "dogguide_model"
        
        
        