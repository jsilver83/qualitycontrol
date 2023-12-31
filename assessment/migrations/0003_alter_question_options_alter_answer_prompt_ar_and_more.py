# Generated by Django 4.2.1 on 2023-05-24 10:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assessment', '0002_assessment_created_for'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='question',
            options={'ordering': ('assessment', 'display_order')},
        ),
        migrations.AlterField(
            model_name='answer',
            name='prompt_ar',
            field=models.TextField(blank=True, verbose_name='Prompt (AR)'),
        ),
        migrations.AlterField(
            model_name='answer',
            name='weight',
            field=models.FloatField(blank=True, default=1, help_text='Empty wight indicate N/A answers which are not going to be calculated in the total score', null=True, verbose_name='Weight'),
        ),
        migrations.AlterField(
            model_name='evidence',
            name='type',
            field=models.CharField(choices=[('PICTURE', 'Picture'), ('VIDEO', 'Video'), ('misc', 'Miscellaneous')], max_length=256, verbose_name='Type'),
        ),
        migrations.AlterField(
            model_name='question',
            name='help_text_ar',
            field=models.TextField(blank=True, verbose_name='Help Text (AR)'),
        ),
        migrations.AlterField(
            model_name='question',
            name='help_text_en',
            field=models.TextField(blank=True, verbose_name='Help Text (EN)'),
        ),
        migrations.AlterField(
            model_name='question',
            name='prompt_ar',
            field=models.TextField(blank=True, verbose_name='Prompt (AR)'),
        ),
    ]
