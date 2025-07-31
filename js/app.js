// Alpine.js data and methods
document.addEventListener('alpine:init', () => {
    Alpine.data('app', (isAuthenticated = false, userEmail = '', siteSettings = null) => ({
        // Core data
        products: [],
        activeCategory: 'all',
        loadingProducts: false,
        cateringServices: [],
        mobileMenuOpen: false,
        
        // Search and Filter variables
        searchQuery: '',
        selectedCategory: 'all',
        minPrice: '',
        maxPrice: '',
        categories: [
            { value: 'all', label: 'All' },
            { value: 'finger-foods', label: 'Finger Foods' },
            { value: 'beverages', label: 'Beverages' },
            { value: 'desserts', label: 'Desserts' }
        ],
        
        siteSettings: siteSettings || {
            site_name: 'CHOPHOUSE',
            tagline: 'Premium finger foods and catering services for all your special occasions.',
            phone: '+1 (555) 123-4567',
            email: 'info@chophouse.com',
            address: '123 Food Street, Culinary District',
            hours: 'Mon-Sat: 9AM-9PM',
        },

        // Cart functionality
        cart: [],
        cartOpen: false,
        get cartTotal() {
            return this.cart.reduce((total, item) => total + (item.price * item.quantity), 0);
        },

        // Checkout functionality
        checkoutOpen: false,
        checkoutStep: 'cart',
        orderDetails: {},

        // Product modal
        selectedProduct: null,
        productModalOpen: false,

        // Review system
        isAuthenticated: isAuthenticated,
        userEmail: userEmail,
        ratingModalOpen: false,
        commentModalOpen: false,
        ratingValue: 0,
        hoverRating: 0,
        commentText: '',
        commentName: '',
        ratings: [],
        comments: [],
        ratingSubmitting: false,
        commentSubmitting: false,
        ratingError: '',
        commentError: '',
        reviewSuccess: '',
        reviewError: '',

        // Wishlist
        wishlistItems: [],
        wishlistModalOpen: false,

        // Blog
        blogPosts: [],
        selectedPost: null,
        blogModalOpen: false,

        // Newsletter
        newsletterForm: {
            email: '',
            name: ''
        },
        newsletterSubmitting: false,
        newsletterMessage: '',
        newsletterSuccess: false,

        // Contact Form
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

        // Service modal
        serviceModalOpen: false,
        selectedService: null,

        // Stripe
        stripe: null,
        cardElement: null,
        paymentProcessing: false,
        orderSuccess: false,
        orderError: false,
        orderErrorMessage: '',
        orderDetails: {},

        // Initialize
        init() {
            console.log('Alpine.js initialized');
            console.log('Site Settings:', this.siteSettings);
            this.fetchProducts();
            this.fetchCateringServices();
            this.fetchBlogPosts();
            if (this.isAuthenticated) {
                this.fetchWishlist();
                // Initialize contact form with user email
                this.contactForm.email = this.userEmail;
                console.log('Contact form email initialized:', this.contactForm.email);
            }
        },

        // Product methods
        async fetchProducts() {
            console.log('Fetching products...');
            this.loadingProducts = true;
            let url = '/api/products/';
            const params = [];
            
            // Add search and filter parameters
            if (this.searchQuery) params.push(`search=${encodeURIComponent(this.searchQuery)}`);
            if (this.selectedCategory && this.selectedCategory !== 'all') params.push(`category=${encodeURIComponent(this.selectedCategory)}`);
            if (this.minPrice) params.push(`price__gte=${this.minPrice}`);
            if (this.maxPrice) params.push(`price__lte=${this.maxPrice}`);
            
            if (params.length) url += '?' + params.join('&');
            console.log('Products API URL:', url);
            
            try {
                const res = await fetch(url);
                console.log('Products API response:', res);
                if (res.ok) {
                    this.products = await res.json();
                    console.log('Products loaded:', this.products);
                } else {
                    console.error('Products API error:', res.status);
                    this.products = [];
                }
            } catch (e) {
                console.error('Products fetch error:', e);
                this.products = [];
            }
            this.loadingProducts = false;
        },

        get filteredProducts() {
            console.log('Filtering products. Active category:', this.activeCategory);
            console.log('All products:', this.products);
            if (this.activeCategory === 'all') {
                console.log('Returning all products:', this.products);
                return this.products;
            }
            const filtered = this.products.filter(p => p.category === this.activeCategory);
            console.log('Filtered products:', filtered);
            return filtered;
        },

        // Catering methods
        async fetchCateringServices() {
            console.log('Fetching catering services...');
            try {
                const res = await fetch('/api/catering-services/');
                console.log('Catering API response:', res);
                if (res.ok) {
                    this.cateringServices = await res.json();
                    console.log('Catering services loaded:', this.cateringServices);
                } else {
                    console.error('Catering API error:', res.status);
                }
            } catch (e) {
                console.error('Catering fetch error:', e);
                this.cateringServices = [];
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

        // Cart methods
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
            const newQuantity = item.quantity + change;
            if (newQuantity <= 0) {
                this.cart = this.cart.filter(cartItem => cartItem.id !== item.id);
            } else {
                item.quantity = newQuantity;
            }
        },

        continueShopping() {
            this.cartOpen = false;
        },

        checkout() {
            this.checkoutOpen = true;
            this.cartOpen = false;
        },

        // Product modal methods
        openProductModal(product) {
            this.selectedProduct = product;
            this.productModalOpen = true;
            this.ratingValue = 0;
            this.hoverRating = 0;
            this.commentText = '';
            this.commentName = '';
            this.commentError = '';
            this.reviewSuccess = '';
            this.reviewError = '';
            this.fetchRatings(product.id);
            this.fetchComments(product.id);
        },

        closeProductModal() {
            this.productModalOpen = false;
            this.selectedProduct = null;
        },

        // Review methods
        async fetchRatings(productId) {
            try {
                const res = await fetch(`/api/product-ratings/?product=${productId}`);
                if (res.ok) {
                    this.ratings = await res.json();
                }
            } catch (e) {
                console.error('Error fetching ratings:', e);
            }
        },

        async fetchComments(productId) {
            try {
                const res = await fetch(`/api/product-comments/?product=${productId}`);
                if (res.ok) {
                    this.comments = await res.json();
                }
            } catch (e) {
                console.error('Error fetching comments:', e);
            }
        },

        async submitRating() {
            if (!this.isAuthenticated) {
                alert('Please log in to submit a rating');
                return;
            }
            if (this.ratingValue === 0) {
                this.ratingError = 'Please select a rating';
                return;
            }

            this.ratingSubmitting = true;
            this.ratingError = '';

            try {
                const csrfToken = this.getCookie('csrftoken');
                const res = await fetch('/api/product-ratings/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    body: JSON.stringify({
                        product: this.selectedProduct.id,
                        rating: this.ratingValue,
                        user_email: this.userEmail
                    })
                });

                if (res.ok) {
                    this.ratingValue = 0;
                    this.ratingModalOpen = false;
                    this.fetchRatings(this.selectedProduct.id);
                } else {
                    const error = await res.json();
                    if (error.detail && error.detail.includes('unique')) {
                        this.ratingError = 'You have already rated this product';
                    } else {
                        this.ratingError = 'Error submitting rating';
                    }
                }
            } catch (e) {
                this.ratingError = 'Network error';
            }
            this.ratingSubmitting = false;
        },

        async submitComment() {
            if (!this.isAuthenticated) {
                alert('Please log in to submit a comment');
                return;
            }
            if (!this.commentText.trim()) {
                this.commentError = 'Please enter a comment';
                return;
            }

            this.commentSubmitting = true;
            this.commentError = '';

            try {
                const csrfToken = this.getCookie('csrftoken');
                const res = await fetch('/api/product-comments/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    body: JSON.stringify({
                        product: this.selectedProduct.id,
                        comment: this.commentText,
                        user_email: this.userEmail
                    })
                });

                if (res.ok) {
                    this.commentText = '';
                    this.commentModalOpen = false;
                    this.fetchComments(this.selectedProduct.id);
                } else {
                    this.commentError = 'Error submitting comment';
                }
            } catch (e) {
                this.commentError = 'Network error';
            }
            this.commentSubmitting = false;
        },

        async submitReview() {
            if (!this.isAuthenticated) {
                alert('Please log in to submit a review');
                return;
            }
            if (!this.commentName.trim()) {
                this.commentError = 'Please enter your name';
                return;
            }
            if (this.ratingValue === 0) {
                this.commentError = 'Please select a rating';
                return;
            }
            if (!this.commentText.trim()) {
                this.commentError = 'Please enter your review';
                return;
            }

            this.commentSubmitting = true;
            this.commentError = '';

            try {
                const csrfToken = this.getCookie('csrftoken');
                
                // Submit rating first
                const ratingRes = await fetch('/api/product-ratings/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    body: JSON.stringify({
                        product: this.selectedProduct.id,
                        rating: this.ratingValue,
                        user_email: this.userEmail
                    })
                });

                // Submit comment
                const commentRes = await fetch('/api/product-comments/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    body: JSON.stringify({
                        product: this.selectedProduct.id,
                        comment: this.commentText,
                        user_email: this.userEmail
                    })
                });

                if (ratingRes.ok && commentRes.ok) {
                    // Clear form
                    this.commentName = '';
                    this.commentText = '';
                    this.ratingValue = 0;
                    
                    // Refresh data
                    this.fetchRatings(this.selectedProduct.id);
                    this.fetchComments(this.selectedProduct.id);
                    
                    // Show success message
                    this.reviewSuccess = 'Review submitted successfully!';
                    setTimeout(() => {
                        this.reviewSuccess = '';
                    }, 3000);
                } else {
                    this.commentError = 'Error submitting review. Please try again.';
                }
            } catch (e) {
                this.commentError = 'Network error. Please try again.';
            }
            this.commentSubmitting = false;
        },

        closeRatingModal() {
            this.ratingModalOpen = false;
            this.ratingValue = 0;
            this.ratingError = '';
        },

        closeCommentModal() {
            this.commentModalOpen = false;
            this.commentText = '';
            this.commentError = '';
        },

        getCookie(name) {
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                const cookies = document.cookie.split(';');
                for (let i = 0; i < cookies.length; i++) {
                    const cookie = cookies[i].trim();
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        },

        // Wishlist methods
        async fetchWishlist() {
            if (!this.isAuthenticated) return;
            try {
                const res = await fetch(`/api/wishlist/?customer_email=${encodeURIComponent(this.userEmail)}`);
                if (res.ok) {
                    this.wishlistItems = await res.json();
                }
            } catch (e) {
                console.error('Error fetching wishlist:', e);
            }
        },

        async addToWishlist(product) {
            if (!this.isAuthenticated) {
                alert('Please log in to add items to wishlist');
                return;
            }
            try {
                const csrfToken = this.getCookie('csrftoken');
                const res = await fetch('/api/wishlist/add_item/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    body: JSON.stringify({
                        product: product.id,
                        user_email: this.userEmail
                    })
                });
                if (res.ok) {
                    this.fetchWishlist();
                }
            } catch (e) {
                console.error('Error adding to wishlist:', e);
            }
        },

        async removeFromWishlist(productId) {
            try {
                const csrfToken = this.getCookie('csrftoken');
                const res = await fetch('/api/wishlist/remove_item/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    body: JSON.stringify({
                        product: productId,
                        user_email: this.userEmail
                    })
                });
                if (res.ok) {
                    this.fetchWishlist();
                }
            } catch (e) {
                console.error('Error removing from wishlist:', e);
            }
        },

        isInWishlist(productId) {
            return this.wishlistItems.some(item => item.product.id === productId);
        },

        // Blog methods
        async fetchBlogPosts() {
            try {
                const res = await fetch('/api/blog/');
                if (res.ok) {
                    this.blogPosts = await res.json();
                }
            } catch (e) {
                console.error('Error fetching blog posts:', e);
            }
        },

        openBlogPost(post) {
            this.selectedPost = post;
            this.blogModalOpen = true;
        },

        closeBlogModal() {
            this.blogModalOpen = false;
            this.selectedPost = null;
        },

        // Newsletter methods
        async subscribeToNewsletter() {
            if (!this.newsletterForm.email) {
                this.newsletterMessage = 'Please enter your email address';
                return;
            }

            this.newsletterSubmitting = true;
            this.newsletterMessage = '';

            try {
                const csrfToken = this.getCookie('csrftoken');
                const res = await fetch('/api/newsletter-subscribers/subscribe/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    body: JSON.stringify(this.newsletterForm)
                });

                if (res.ok) {
                    this.newsletterSuccess = true;
                    this.newsletterMessage = 'Successfully subscribed to newsletter!';
                    this.newsletterForm = { email: '', firstName: '', lastName: '' };
                } else {
                    const error = await res.json();
                    this.newsletterMessage = error.detail || 'Error subscribing to newsletter';
                }
            } catch (e) {
                this.newsletterMessage = 'Network error';
            }
            this.newsletterSubmitting = false;
        },

        // Contact Form methods
        async submitContactForm() {
            console.log('Submit contact form called');
            console.log('Contact form data:', this.contactForm);
            console.log('Is authenticated:', this.isAuthenticated);
            console.log('User email:', this.userEmail);
            
            if (!this.contactForm.firstName || !this.contactForm.lastName || !this.contactForm.email || !this.contactForm.message) {
                console.log('Validation failed - missing required fields');
                this.contactError = true;
                this.contactErrorMessage = 'Please fill in all required fields';
                return;
            }

            this.contactSubmitting = true;
            this.contactError = false;
            this.contactSuccess = false;
            this.contactErrorMessage = '';
            this.contactSuccessMessage = '';

            try {
                const csrfToken = this.getCookie('csrftoken');
                const requestData = {
                    first_name: this.contactForm.firstName,
                    last_name: this.contactForm.lastName,
                    email: this.contactForm.email,
                    phone: this.contactForm.phone || '',
                    message: this.contactForm.message
                };
                
                console.log('Sending contact form data:', requestData);
                console.log('CSRF Token:', csrfToken);
                
                const res = await fetch('/api/contact/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    body: JSON.stringify(requestData)
                });

                console.log('Response status:', res.status);
                const data = await res.json();
                console.log('Contact API response:', data);

                if (res.ok && data.success) {
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
                    this.contactErrorMessage = data.errors ? Object.values(data.errors).flat().join(', ') : 'Error sending message. Please try again.';
                }
            } catch (e) {
                console.error('Contact form error:', e);
                this.contactError = true;
                this.contactErrorMessage = 'Network error. Please try again.';
            }
            this.contactSubmitting = false;
        },

        // Stripe Payment Integration
        initializeStripe() {
            if (typeof Stripe !== 'undefined') {
                this.stripe = Stripe('pk_test_your_stripe_publishable_key_here');
                this.setupStripeElements();
            }
        },

        setupStripeElements() {
            if (this.stripe) {
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
                this.cardElement.mount('#card-element');
            }
        },

        async placeOrder() {
            if (!this.stripe || !this.cardElement) {
                this.orderError = true;
                this.orderErrorMessage = 'Payment system not initialized. Please refresh the page.';
                return;
            }

            this.paymentProcessing = true;
            this.orderError = false;
            this.orderSuccess = false;

            try {
                // Create order
                const orderData = {
                    first_name: this.orderDetails.firstName,
                    last_name: this.orderDetails.lastName,
                    email: this.orderDetails.email,
                    phone: this.orderDetails.phone,
                    address: this.orderDetails.address,
                    city: this.orderDetails.city,
                    state: this.orderDetails.state,
                    zip_code: this.orderDetails.zipCode,
                    total_amount: this.cartTotal,
                    items: this.cart.map(item => ({
                        product_id: item.id,
                        quantity: item.quantity
                    }))
                };

                const csrfToken = this.getCookie('csrftoken');
                const orderResponse = await fetch('/api/orders/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    body: JSON.stringify(orderData)
                });

                const orderResult = await orderResponse.json();

                if (!orderResponse.ok) {
                    throw new Error(orderResult.error || 'Failed to create order');
                }

                // Confirm payment with Stripe
                const { error, paymentIntent } = await this.stripe.confirmCardPayment(
                    orderResult.client_secret,
                    {
                        payment_method: {
                            card: this.cardElement,
                            billing_details: {
                                name: `${this.orderDetails.firstName} ${this.orderDetails.lastName}`,
                                email: this.orderDetails.email,
                                address: {
                                    line1: this.orderDetails.address,
                                    city: this.orderDetails.city,
                                    state: this.orderDetails.state,
                                    postal_code: this.orderDetails.zipCode,
                                }
                            }
                        }
                    }
                );

                if (error) {
                    throw new Error(error.message);
                }

                if (paymentIntent.status === 'succeeded') {
                    // Confirm payment on backend
                    const confirmResponse = await fetch(`/api/orders/${orderResult.order.id}/confirm_payment/`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': csrfToken
                        },
                        body: JSON.stringify({
                            payment_intent_id: paymentIntent.id
                        })
                    });

                    const confirmResult = await confirmResponse.json();

                    if (confirmResponse.ok && confirmResult.success) {
                        this.orderSuccess = true;
                        this.orderDetails = orderResult.order;
                        this.cart = [];
                        this.checkoutOpen = false;
                        this.checkoutStep = 'cart';
                    } else {
                        throw new Error(confirmResult.error || 'Payment confirmation failed');
                    }
                } else {
                    throw new Error('Payment was not completed');
                }

            } catch (error) {
                this.orderError = true;
                this.orderErrorMessage = error.message;
            }

            this.paymentProcessing = false;
        },

        nextCheckoutStep() {
            if (this.checkoutStep === 'cart') {
                this.checkoutStep = 'customer-info';
            } else if (this.checkoutStep === 'customer-info') {
                this.checkoutStep = 'delivery-info';
            } else if (this.checkoutStep === 'delivery-info') {
                this.checkoutStep = 'payment';
                this.initializeStripe();
            }
        },

        prevCheckoutStep() {
            if (this.checkoutStep === 'payment') {
                this.checkoutStep = 'delivery-info';
            } else if (this.checkoutStep === 'delivery-info') {
                this.checkoutStep = 'customer-info';
            } else if (this.checkoutStep === 'customer-info') {
                this.checkoutStep = 'cart';
            }
        }
    }));
}); 