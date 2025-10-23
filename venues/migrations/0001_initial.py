import django.db.models.deletion
import django.core.validators
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('slug', models.SlugField(max_length=120, unique=True)),
            ],
            options={'ordering': ['name']},
        ),
        migrations.CreateModel(
            name='Venue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=150)),
                ('slug', models.SlugField(max_length=170, unique=True)),
                ('description', models.TextField()),
                ('location', models.CharField(max_length=150)),
                ('city', models.CharField(max_length=100)),
                ('address', models.TextField(blank=True)),
                ('price_per_hour', models.DecimalField(decimal_places=2, max_digits=10)),
                ('capacity', models.PositiveIntegerField(default=1)),
                ('facilities', models.TextField(help_text='Comma separated facilities list.')),
                ('image_url', models.URLField(blank=True)),
                ('available_start_time', models.TimeField(default='07:00:00')),
                ('available_end_time', models.TimeField(default='22:00:00')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='venues', to='venues.category')),
            ],
            options={'ordering': ['name']},
        ),
        migrations.CreateModel(
            name='VenueAvailability',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('start_datetime', models.DateTimeField()),
                ('end_datetime', models.DateTimeField()),
                ('venue', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='availabilities', to='venues.venue')),
            ],
            options={'ordering': ['start_datetime'], 'verbose_name_plural': 'Venue availabilities'},
        ),
        migrations.CreateModel(
            name='Wishlist',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='wishlists', to=settings.AUTH_USER_MODEL)),
                ('venue', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='wishlisted_by', to='venues.venue')),
            ],
            options={'ordering': ['-created_at'], 'unique_together': {('user', 'venue')}},
        ),
        migrations.CreateModel(
            name='AddOn',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=120)),
                ('description', models.TextField(blank=True)),
                ('price', models.DecimalField(decimal_places=2, max_digits=9)),
                ('venue', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='addons', to='venues.venue')),
            ],
            options={'ordering': ['name']},
        ),
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('start_datetime', models.DateTimeField()),
                ('end_datetime', models.DateTimeField()),
                ('notes', models.TextField(blank=True)),
                ('addons', models.ManyToManyField(blank=True, related_name='bookings', to='venues.addon')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bookings', to=settings.AUTH_USER_MODEL)),
                ('venue', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bookings', to='venues.venue')),
            ],
            options={'ordering': ['-start_datetime']},
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('rating', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ('comment', models.TextField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to=settings.AUTH_USER_MODEL)),
                ('venue', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='venues.venue')),
            ],
            options={'ordering': ['-created_at'], 'unique_together': {('user', 'venue')}},
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('method', models.CharField(choices=[('qris', 'QRIS'), ('gopay', 'GoPay')], max_length=20)),
                ('status', models.CharField(choices=[('waiting', 'Waiting for confirmation'), ('confirmed', 'Confirmed'), ('completed', 'Completed')], default='waiting', max_length=20)),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('deposit_amount', models.DecimalField(decimal_places=2, default=10000, max_digits=10)),
                ('reference_code', models.CharField(max_length=100, unique=True)),
                ('booking', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='payment', to='venues.booking')),
            ],
            options={'ordering': ['-created_at']},
        ),
    ]
