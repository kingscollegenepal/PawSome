from django.db import models

# Create your models here;
class CatGuide(models.Model):
    guide_title = models.CharField()
    guide_content = models.CharField()
    pet_type = models.CharField()
    image = models.ImageField()
    
    def __str__(self) -> str:
        return self.guide_title
    
    class Meta:
        db_table = "catguide_model"
        
        
        