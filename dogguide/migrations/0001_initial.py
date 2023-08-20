# Generated by Django 4.2.3 on 2023-08-20 04:14

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PetGuide',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('guide_title', models.CharField()),
                ('guide_content', models.CharField()),
                ('pet_type', models.CharField()),
                ('image', models.ImageField(upload_to='')),
            ],
            options={
                'db_table': 'petguide_guidemodel',
            },
        ),
    ]
