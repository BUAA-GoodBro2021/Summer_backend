# Generated by Django 4.0.6 on 2022-08-07 09:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0008_alter_document_creator_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='project_id',
            field=models.IntegerField(default=0, verbose_name='项目id'),
        ),
    ]
