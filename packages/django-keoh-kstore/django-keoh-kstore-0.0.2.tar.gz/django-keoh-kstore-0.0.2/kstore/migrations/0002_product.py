# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kstore', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='Product Name')),
                ('description', models.TextField(null=True, verbose_name='Product description', blank=True)),
                ('description_short', models.TextField(null=True, verbose_name='Short description', blank=True)),
                ('ean13', models.CharField(max_length=13, null=True, verbose_name='Codigo de barras', blank=True)),
                ('width', models.DecimalField(null=True, verbose_name='Width in cm', max_digits=20, decimal_places=2, blank=True)),
                ('height', models.DecimalField(null=True, verbose_name='Height in cm', max_digits=20, decimal_places=2, blank=True)),
                ('depth', models.DecimalField(null=True, verbose_name='Depth in cm', max_digits=20, decimal_places=2, blank=True)),
                ('weight', models.DecimalField(null=True, verbose_name='Weight in kg', max_digits=20, decimal_places=2, blank=True)),
                ('quantity', models.PositiveSmallIntegerField(default=0, verbose_name='Quantity')),
                ('price', models.DecimalField(verbose_name='Price in euros', max_digits=20, decimal_places=2)),
                ('cost_price', models.DecimalField(verbose_name='Cost price in euros', max_digits=20, decimal_places=2)),
                ('taxes', models.DecimalField(verbose_name='Taxes', max_digits=20, decimal_places=2)),
                ('out_of_stock', models.BooleanField(default=True, verbose_name='Out of Stock')),
                ('manufacturer', models.ForeignKey(verbose_name=b'Manufacturer', blank=True, to='kstore.Manufacturer', null=True)),
                ('supplier', models.ForeignKey(verbose_name=b'Supplier', blank=True, to='kstore.Supplier', null=True)),
            ],
            options={
                'db_table': 'ks_product',
                'verbose_name': 'product',
                'verbose_name_plural': 'products',
            },
        ),
    ]
