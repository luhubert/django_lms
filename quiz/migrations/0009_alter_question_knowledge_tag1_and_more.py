# Generated by Django 4.2.3 on 2023-08-05 10:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0008_alter_question_knowledge_tag_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='knowledge_tag1',
            field=models.CharField(blank=True, default='', max_length=100, verbose_name='知識點2'),
        ),
        migrations.AlterField(
            model_name='question',
            name='knowledge_tag2',
            field=models.CharField(blank=True, default='', max_length=100, verbose_name='知識點3'),
        ),
    ]
