from rest_framework import serializers
from .models import Product, Order, OrderItem, SiteSettings, CateringService, ContactMessage, ProductReview, Wishlist, ProductRating, ProductComment

class ProductReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductReview
        fields = ['id', 'customer_name', 'rating', 'comment', 'is_verified_purchase', 'created_at']
        read_only_fields = ['is_verified_purchase', 'created_at']

class CreateProductReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductReview
        fields = ['product', 'customer_name', 'customer_email', 'rating', 'comment']

class ProductSerializer(serializers.ModelSerializer):
    average_rating = serializers.ReadOnlyField()
    review_count = serializers.ReadOnlyField()
    rating_distribution = serializers.ReadOnlyField()
    reviews = ProductReviewSerializer(many=True, read_only=True)
    is_in_wishlist = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = '__all__'
    
    def get_is_in_wishlist(self, obj):
        request = self.context.get('request')
        if request and request.query_params.get('customer_email'):
            customer_email = request.query_params.get('customer_email')
            return Wishlist.objects.filter(
                customer_email=customer_email,
                product=obj
            ).exists()
        return False

class WishlistSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    
    class Meta:
        model = Wishlist
        fields = ['id', 'product', 'added_at']

class CreateWishlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wishlist
        fields = ['customer_email', 'product']

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'quantity', 'price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    customer_name = serializers.CharField(source='customer_name', read_only=True)
    delivery_address = serializers.CharField(source='delivery_address', read_only=True)
    
    class Meta:
        model = Order
        fields = '__all__'

class CreateOrderSerializer(serializers.ModelSerializer):
    items = serializers.ListField(
        child=serializers.DictField(),
        write_only=True
    )
    
    class Meta:
        model = Order
        fields = [
            'first_name', 'last_name', 'email', 'phone',
            'address', 'city', 'state', 'zip_code', 'delivery_instructions',
            'total_amount', 'items'
        ]
    
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)
        
        for item_data in items_data:
            product_id = item_data['product_id']
            quantity = item_data['quantity']
            product = Product.objects.get(id=product_id)
            
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=product.price
            )
        
        return order

class SiteSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteSettings
        fields = '__all__'

class CateringServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CateringService
        fields = '__all__'

class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = '__all__' 

class ProductRatingSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = ProductRating
        fields = ['id', 'product', 'user', 'rating', 'created_at']
        read_only_fields = ['user', 'created_at']

class CreateProductRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductRating
        fields = ['product', 'rating']

class ProductCommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = ProductComment
        fields = ['id', 'product', 'user', 'comment', 'created_at']
        read_only_fields = ['user', 'created_at']

class CreateProductCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductComment
        fields = ['product', 'comment'] 