# products/models.py
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
import uuid

class Category(models.Model):
    """Product category model"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    slug = models.SlugField(unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('products:category_detail', kwargs={'slug': self.slug})

class Product(models.Model):
    """Product (Bike) model"""
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('out_of_stock', 'Out of Stock'),
        ('discontinued', 'Discontinued'),
        ('coming_soon', 'Coming Soon'),
    ]
    
    # Basic Information
    name = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    
    # Relationships
    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='products'
    )
    supplier = models.ForeignKey(
        'suppliers.Supplier', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='products'
    )
    
    # Pricing
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Selling price in PKR"
    )
    cost_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Cost price in PKR"
    )
    
    # Stock
    quantity = models.IntegerField(default=0, db_index=True)
    min_stock_level = models.IntegerField(
        default=5,
        help_text="Minimum stock level before alert"
    )
    
    # Product Details
    sku = models.CharField(max_length=50, unique=True)
    brand = models.CharField(max_length=100, blank=True)
    model = models.CharField(max_length=100, blank=True)
    color = models.CharField(max_length=50, blank=True)
    year = models.IntegerField(null=True, blank=True)
    
    # Status & Features
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='available',
        db_index=True,
    )
    is_featured = models.BooleanField(default=False)
    
    # Image
    image = models.ImageField(
        upload_to='products/', 
        null=True, 
        blank=True
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        # Generate slug if not exists
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exclude(id=self.id).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        
        # Generate SKU if not exists
        if not self.sku:
            self.sku = f"BIKE-{uuid.uuid4().hex[:8].upper()}"
        
        # Auto update status based on quantity
        if self.quantity <= 0:
            self.status = 'out_of_stock'
        elif self.status == 'out_of_stock' and self.quantity > 0:
            self.status = 'available'
        
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('products:product_detail', kwargs={'slug': self.slug})
    
    @property
    def stock_status(self):
        """Get stock status as string"""
        if self.quantity <= 0:
            return 'Out of Stock'
        elif self.quantity <= self.min_stock_level:
            return 'Low Stock'
        else:
            return 'In Stock'
    
    @property
    def profit_margin(self):
        """Calculate profit margin percentage"""
        if self.cost_price > 0:
            return ((self.price - self.cost_price) / self.cost_price) * 100
        return 0
    
    @property
    def total_value(self):
        """Calculate total value of stock"""
        return self.price * self.quantity