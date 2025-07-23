// Alpine.js data and methods
document.addEventListener('alpine:init', () => {
    Alpine.data('app', () => ({
        // State
        products: [],
        siteSettings: null,
        cart: [],
        cartOpen: false,
        checkoutOpen: false,
        checkoutStep: 1,
        activeCategory: 'all',
        loadingProducts: true,
        mobileMenuOpen: false,
        cateringServices: [],
        selectedService: null,
        serviceModalOpen: false,
        stripe: null,
        cardElement: null,
        paymentProcessing: false,
        orderSuccess: false,
        orderError: false,
        orderSuccessMessage: '',
        orderErrorMessage: '',

        // Contact form state
        contactForm: {
            firstName: '',
            lastName: '',
            email: '',
            phone: '',
            message: ''
        },
        contactSubmitting: false,
        contactSuccess: false,
        contactError: false,
        contactSuccessMessage: '',
        contactErrorMessage: '',

        // Order details
        orderDetails: {
            customerInfo: {
                firstName: '',
                lastName: '',
                email: '',
                phone: ''
            },
            deliveryInfo: {
                address: '',
                city: '',
                state: '',
                zipCode: '',
                instructions: ''
            }
        },

        // New features state
        searchQuery: '',
        priceFilter: { min: '', max: '' },
        ratingFilter: '',
        sortBy: 'name',
        wishlistItems: [],
        wishlistModalOpen: false,
        selectedProduct: null,
        productModalOpen: false,
        showReviewForm: false,
        reviewForm: {
            name: '',
            email: '',
            rating: 0,
            comment: ''
        },
        reviewSubmitting: false,

        // Computed properties
        get cartTotal() {
            return this.cart.reduce((total, item) => total + (item.price * item.quantity), 0);
        },

        get filteredProducts() {
            let filtered = this.products;

            // Category filter
            if (this.activeCategory !== 'all') {
                filtered = filtered.filter(product => product.category === this.activeCategory);
            }

            // Search filter
            if (this.searchQuery.trim()) {
                const query = this.searchQuery.toLowerCase();
                filtered = filtered.filter(product => 
                    product.name.toLowerCase().includes(query) ||
                    product.description.toLowerCase().includes(query)
                );
            }

            // Price filter
            if (this.priceFilter.min !== '') {
                filtered = filtered.filter(product => product.price >= parseFloat(this.priceFilter.min));
            }
            if (this.priceFilter.max !== '') {
                filtered = filtered.filter(product => product.price <= parseFloat(this.priceFilter.max));
            }

            // Rating filter
            if (this.ratingFilter !== '') {
                const minRating = parseFloat(this.ratingFilter);
                filtered = filtered.filter(product => (product.average_rating || 0) >= minRating);
            }

            // Sort
            filtered.sort((a, b) => {
                switch (this.sortBy) {
                    case 'name':
                        return a.name.localeCompare(b.name);
                    case 'price':
                        return a.price - b.price;
                    case 'rating':
                        return (b.average_rating || 0) - (a.average_rating || 0);
                    case 'newest':
                        return new Date(b.created_at) - new Date(a.created_at);
                    default:
                        return 0;
                }
            });

            return filtered;
        },

        // Methods
        async init() {
            await this.fetchProducts();
            await this.fetchSiteSettings();
            await this.fetchCateringServices();
            this.initializeStripe();
            this.loadWishlistFromStorage();
        },

        initializeStripe() {
            // Initialize Stripe - you'll need to get the publishable key from your backend
            this.stripe = Stripe('pk_test_your_stripe_publishable_key_here');
            
            // Create card element when checkout step 3 is reached
            this.$watch('checkoutStep', (step) => {
                if (step === 3 && !this.cardElement) {
                    this.createCardElement();
                }
            });
        },

        createCardElement() {
            // Create card element
            const elements = this.stripe.elements();
            this.cardElement = elements.create('card', {
                style: {
                    base: {
                        fontSize: '16px',
                        color: '#424770',
                        '::placeholder': {
                            color: '#aab7c4',
                        },
                    },
                    invalid: {
                        color: '#9e2146',
                    },
                },
            });
            
            // Mount the card element
            this.cardElement.mount('#card-element');
            
            // Handle validation errors
            this.cardElement.on('change', ({error}) => {
                const displayError = document.getElementById('card-errors');
                if (error) {
                    displayError.textContent = error.message;
                } else {
                    displayError.textContent = '';
                }
            });
        },

        async fetchProducts() {
            try {
                this.loadingProducts = true;
                const response = await fetch('http://127.0.0.1:8000/api/products/');
                if (response.ok) {
                    this.products = await response.json();
                } else {
                    console.error('Failed to fetch products');
                }
            } catch (error) {
                console.error('Error fetching products:', error);
            } finally {
                this.loadingProducts = false;
            }
        },

        async fetchSiteSettings() {
            try {
                const response = await fetch('http://127.0.0.1:8000/api/settings/');
                if (response.ok) {
                    this.siteSettings = await response.json();
                }
            } catch (error) {
                console.error('Error fetching site settings:', error);
            }
        },

        async fetchCateringServices() {
            try {
                const response = await fetch('http://127.0.0.1:8000/api/catering-services/');
                if (response.ok) {
                    this.cateringServices = await response.json();
                }
            } catch (error) {
                console.error('Error fetching catering services:', error);
            }
        },

        async submitContactForm() {
            this.contactSubmitting = true;
            this.contactSuccess = false;
            this.contactError = false;

            try {
                const response = await fetch('http://127.0.0.1:8000/api/contact/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        first_name: this.contactForm.firstName,
                        last_name: this.contactForm.lastName,
                        email: this.contactForm.email,
                        phone: this.contactForm.phone,
                        message: this.contactForm.message
                    })
                });

                const data = await response.json();

                if (response.ok && data.success) {
                    this.contactSuccess = true;
                    this.contactSuccessMessage = data.message;
                    // Reset form
                    this.contactForm = {
                        firstName: '',
                        lastName: '',
                        email: '',
                        phone: '',
                        message: ''
                    };
                } else {
                    this.contactError = true;
                    if (data.errors) {
                        const errorMessages = Object.values(data.errors).flat();
                        this.contactErrorMessage = errorMessages.join(', ');
                    } else {
                        this.contactErrorMessage = 'Failed to send message. Please try again.';
                    }
                }
            } catch (error) {
                console.error('Network error:', error);
                this.contactError = true;
                this.contactErrorMessage = 'Network error. Please check your connection and try again.';
            } finally {
                this.contactSubmitting = false;
            }
        },

        addToCart(product) {
            const existingItem = this.cart.find(item => item.id === product.id);
            if (existingItem) {
                existingItem.quantity += 1;
            } else {
                this.cart.push({
                    ...product,
                    quantity: 1
                });
            }
            this.cartOpen = true;
        },

        updateQuantity(item, change) {
            item.quantity += change;
            if (item.quantity <= 0) {
                this.cart = this.cart.filter(cartItem => cartItem.id !== item.id);
            }
        },

        removeFromCart(item) {
            this.cart = this.cart.filter(cartItem => cartItem.id !== item.id);
        },

        continueShopping() {
            this.cartOpen = false;
        },

        checkout() {
            this.cartOpen = false;
            this.checkoutOpen = true;
            this.checkoutStep = 1;
            this.orderSuccess = false;
            this.orderError = false;
        },

        nextCheckoutStep() {
            if (this.checkoutStep < 3) {
                this.checkoutStep++;
            }
        },

        prevCheckoutStep() {
            if (this.checkoutStep > 1) {
                this.checkoutStep--;
            }
        },

        async placeOrder() {
            if (this.cart.length === 0) {
                this.orderError = true;
                this.orderErrorMessage = 'Your cart is empty.';
                return;
            }

            this.paymentProcessing = true;
            this.orderError = false;

            try {
                // Create order data
                const orderData = {
                    first_name: this.orderDetails.customerInfo.firstName,
                    last_name: this.orderDetails.customerInfo.lastName,
                    email: this.orderDetails.customerInfo.email,
                    phone: this.orderDetails.customerInfo.phone,
                    address: this.orderDetails.deliveryInfo.address,
                    city: this.orderDetails.deliveryInfo.city,
                    state: this.orderDetails.deliveryInfo.state,
                    zip_code: this.orderDetails.deliveryInfo.zipCode,
                    delivery_instructions: this.orderDetails.deliveryInfo.instructions,
                    total_amount: this.cartTotal,
                    items: this.cart.map(item => ({
                        product_id: item.id,
                        quantity: item.quantity
                    }))
                };

                // Create order
                const response = await fetch('http://127.0.0.1:8000/api/orders/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(orderData)
                });

                const data = await response.json();

                if (response.ok && data.client_secret) {
                    // Confirm payment with Stripe
                    const { error } = await this.stripe.confirmCardPayment(data.client_secret, {
                        payment_method: {
                            card: this.cardElement,
                            billing_details: {
                                name: `${this.orderDetails.customerInfo.firstName} ${this.orderDetails.customerInfo.lastName}`,
                                email: this.orderDetails.customerInfo.email,
                                phone: this.orderDetails.customerInfo.phone,
                                address: {
                                    line1: this.orderDetails.deliveryInfo.address,
                                    city: this.orderDetails.deliveryInfo.city,
                                    state: this.orderDetails.deliveryInfo.state,
                                    postal_code: this.orderDetails.deliveryInfo.zipCode,
                                }
                            }
                        }
                    });

                    if (error) {
                        this.orderError = true;
                        this.orderErrorMessage = error.message || 'Payment failed. Please try again.';
                    } else {
                        // Payment successful
                        this.orderSuccess = true;
                        this.orderSuccessMessage = 'Order placed successfully! You will receive a confirmation email shortly.';
                        
                        // Clear cart
                        this.cart = [];
                        this.checkoutOpen = false;
                        
                        // Reset order details
                        this.orderDetails = {
                            customerInfo: {
                                firstName: '',
                                lastName: '',
                                email: '',
                                phone: ''
                            },
                            deliveryInfo: {
                                address: '',
                                city: '',
                                state: '',
                                zipCode: '',
                                instructions: ''
                            }
                        };
                    }
                } else {
                    this.orderError = true;
                    this.orderErrorMessage = data.error || 'Failed to create order. Please try again.';
                }
            } catch (error) {
                console.error('Order error:', error);
                this.orderError = true;
                this.orderErrorMessage = 'An error occurred. Please try again.';
            } finally {
                this.paymentProcessing = false;
            }
        },

        showServiceDetails(service) {
            this.selectedService = service;
            this.serviceModalOpen = true;
        },

        closeServiceModal() {
            this.serviceModalOpen = false;
            this.selectedService = null;
        },

        setActiveCategory(category) {
            this.activeCategory = category;
        },

        toggleMobileMenu() {
            this.mobileMenuOpen = !this.mobileMenuOpen;
        },

        // Wishlist functionality
        loadWishlistFromStorage() {
            const stored = localStorage.getItem('chophouse_wishlist');
            if (stored) {
                this.wishlistItems = JSON.parse(stored);
            }
        },

        saveWishlistToStorage() {
            localStorage.setItem('chophouse_wishlist', JSON.stringify(this.wishlistItems));
        },

        async toggleWishlist(product) {
            const existingIndex = this.wishlistItems.findIndex(item => item.product.id === product.id);
            
            if (existingIndex > -1) {
                // Remove from wishlist
                this.wishlistItems.splice(existingIndex, 1);
                product.is_in_wishlist = false;
            } else {
                // Add to wishlist
                this.wishlistItems.push({ product: { ...product } });
                product.is_in_wishlist = true;
            }
            
            this.saveWishlistToStorage();
        },

        openWishlist() {
            this.wishlistModalOpen = true;
        },

        closeWishlistModal() {
            this.wishlistModalOpen = false;
        },

        removeFromWishlist(product) {
            this.toggleWishlist(product);
        },

        // Product details functionality
        showProductDetails(product) {
            this.selectedProduct = product;
            this.productModalOpen = true;
            this.showReviewForm = false;
            this.reviewForm = {
                name: '',
                email: '',
                rating: 0,
                comment: ''
            };
        },

        closeProductModal() {
            this.productModalOpen = false;
            this.selectedProduct = null;
            this.showReviewForm = false;
        },

        // Review functionality
        async submitReview() {
            if (!this.selectedProduct || this.reviewForm.rating === 0) {
                return;
            }

            this.reviewSubmitting = true;

            try {
                const response = await fetch('http://127.0.0.1:8000/api/reviews/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        product: this.selectedProduct.id,
                        customer_name: this.reviewForm.name,
                        customer_email: this.reviewForm.email,
                        rating: this.reviewForm.rating,
                        comment: this.reviewForm.comment
                    })
                });

                const data = await response.json();

                if (response.ok) {
                    // Refresh product data to get updated reviews
                    await this.fetchProducts();
                    
                    // Reset form
                    this.reviewForm = {
                        name: '',
                        email: '',
                        rating: 0,
                        comment: ''
                    };
                    this.showReviewForm = false;
                    
                    // Show success message
                    alert('Review submitted successfully!');
                } else {
                    alert('Failed to submit review. Please try again.');
                }
            } catch (error) {
                console.error('Review submission error:', error);
                alert('An error occurred. Please try again.');
            } finally {
                this.reviewSubmitting = false;
            }
        }
    }));
}); 