// Alpine.js data and methods
// Simple product grid with category tabs, no advanced UX

document.addEventListener('alpine:init', () => {
    Alpine.data('app', (isAuthenticated = false, userEmail = '') => ({
        products: [],
        activeCategory: 'all',
        cart: [],
        cartOpen: false,
        checkoutOpen: false,
        checkoutStep: 1,
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
        cateringServices: [],
        serviceModalOpen: false,
        selectedService: null,
        siteSettings: {
            site_name: 'TASTY FINGERS',
            tagline: 'Premium finger foods and catering services for all your special occasions.',
            phone: '+1 (555) 123-4567',
            email: 'info@tastyfingers.com',
            address: '123 Food Street, Culinary District',
            hours: 'Mon-Sat: 9AM-9PM',
        },
        loadingProducts: false,
        selectedProduct: null,
        productModalOpen: false,
        isAuthenticated,
        userEmail,
        ratingModalOpen: false,
        commentModalOpen: false,
        ratingValue: 3,
        commentText: '',
        ratings: [],
        comments: [],
        ratingSubmitting: false,
        commentSubmitting: false,
        ratingError: '',
        commentError: '',
        reviewForm: {
            name: '',
            email: '',
            rating: 0,
            hoverRating: 0,
            comment: ''
        },
        reviewSuccess: '',
        reviewError: '',
        wishlistItems: [],
        wishlistModalOpen: false,
        
        // Stripe payment variables
        stripe: null,
        cardElement: null,
        paymentProcessing: false,
        orderSuccess: false,
        orderSuccessMessage: '',
        orderError: false,
        orderErrorMessage: '',
        
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
        
        blogPosts: [],
        blogPostModalOpen: false,
        selectedBlogPost: null,
        async fetchBlogPosts() {
            try {
                console.log('Fetching blog posts...');
                const res = await fetch('/api/blog/');
                if (res.ok) {
                    const posts = await res.json();
                    console.log('Blog posts received:', posts);
                    // Add excerpt property for preview
                    this.blogPosts = posts.map(post => ({
                        ...post,
                        excerpt: post.content.length > 120 ? post.content.slice(0, 120) + '...' : post.content
                    }));
                    console.log('Blog posts processed:', this.blogPosts);
                } else {
                    console.error('Failed to fetch blog posts:', res.status);
                }
            } catch (e) { 
                console.error('Error fetching blog posts:', e);
                this.blogPosts = []; 
            }
        },
        openBlogPostModal(post) {
            this.selectedBlogPost = post;
            this.blogPostModalOpen = true;
        },
        closeBlogPostModal() {
            this.blogPostModalOpen = false;
            this.selectedBlogPost = null;
        },
        
        init() {
            this.fetchProducts();
            this.fetchCateringServices();
            this.fetchWishlist();
            this.initializeStripe();
            this.fetchBlogPosts();
        },
        
        // Initialize Stripe
        initializeStripe() {
            if (typeof Stripe !== 'undefined') {
                this.stripe = Stripe('pk_test_your_stripe_publishable_key_here');
                this.setupStripeElements();
            }
        },
        
        // Setup Stripe Elements
        setupStripeElements() {
            if (!this.stripe) return;
            
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
            
            // Mount the card element when checkout opens
            this.$watch('checkoutOpen', (value) => {
                if (value && this.checkoutStep === 3) {
                    setTimeout(() => {
                        const cardContainer = document.getElementById('card-element');
                        if (cardContainer && this.cardElement) {
                            this.cardElement.mount('#card-element');
                        }
                    }, 100);
                }
            });
        },
        
        async fetchProducts() {
            this.loadingProducts = true;
            let url = '/api/products/';
            const params = [];
            if (this.searchQuery) params.push(`search=${encodeURIComponent(this.searchQuery)}`);
            if (this.selectedCategory && this.selectedCategory !== 'all') params.push(`category=${encodeURIComponent(this.selectedCategory)}`);
            if (this.minPrice) params.push(`price__gte=${this.minPrice}`);
            if (this.maxPrice) params.push(`price__lte=${this.maxPrice}`);
            if (params.length) url += '?' + params.join('&');
            try {
                const res = await fetch(url);
                if (res.ok) {
                    this.products = await res.json();
                }
            } catch (e) { this.products = []; }
            this.loadingProducts = false;
        },
        get filteredProducts() {
            if (this.activeCategory === 'all') return this.products;
            return this.products.filter(p => p.category === this.activeCategory);
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
        get cartTotal() {
            return this.cart.reduce((total, item) => total + (item.price * item.quantity), 0);
        },
        updateQuantity(item, change) {
            const newQuantity = item.quantity + change;
            
            if (newQuantity <= 0) {
                // Remove item from cart if quantity would be 0 or less
                this.cart = this.cart.filter(cartItem => cartItem.id !== item.id);
            } else {
                // Update quantity, ensuring it's at least 1
                item.quantity = Math.max(1, newQuantity);
            }
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
        fetchCateringServices() {
            fetch('/api/catering-services/')
                .then(res => res.json())
                .then(data => { this.cateringServices = data; })
                .catch(() => { this.cateringServices = []; });
        },
        showServiceDetails(service) {
            this.selectedService = service;
            this.serviceModalOpen = true;
        },
        closeServiceModal() {
            this.serviceModalOpen = false;
            this.selectedService = null;
        },
        openProductModal(product) {
            this.selectedProduct = product;
            this.productModalOpen = true;
            this.fetchRatings(product.id);
            this.fetchComments(product.id);
        },
        closeProductModal() {
            this.productModalOpen = false;
            this.selectedProduct = null;
            this.ratings = [];
            this.comments = [];
        },
        openRatingModal() {
            this.ratingModalOpen = true;
            this.ratingValue = 3;
            this.ratingError = '';
        },
        closeRatingModal() {
            this.ratingModalOpen = false;
        },
        openCommentModal() {
            this.commentModalOpen = true;
            this.commentText = '';
            this.commentError = '';
        },
        closeCommentModal() {
            this.commentModalOpen = false;
        },
        async fetchRatings(productId) {
            try {
                const res = await fetch(`/api/product-ratings/?product_id=${productId}`);
                if (res.ok) {
                    this.ratings = await res.json();
                } else {
                    this.ratings = [];
                }
            } catch (e) {
                this.ratings = [];
            }
        },
        async fetchComments(productId) {
            try {
                const res = await fetch(`/api/product-comments/?product_id=${productId}`);
                if (res.ok) {
                    this.comments = await res.json();
                } else {
                    this.comments = [];
                }
            } catch (e) {
                this.comments = [];
            }
        },
        async submitRating() {
            if (!this.selectedProduct) return;
            this.ratingSubmitting = true;
            this.ratingError = '';
            try {
                const res = await fetch('/api/product-ratings/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        product: this.selectedProduct.id,
                        rating: this.ratingValue
                    })
                });
                if (res.ok) {
                    this.closeRatingModal();
                    await this.fetchRatings(this.selectedProduct.id);
                } else {
                    const data = await res.json();
                    this.ratingError = data.detail || 'Failed to submit rating.';
                }
            } catch (e) {
                this.ratingError = 'Failed to submit rating.';
            }
            this.ratingSubmitting = false;
        },
        async submitComment() {
            if (!this.selectedProduct) return;
            this.commentSubmitting = true;
            this.commentError = '';
            try {
                const res = await fetch('/api/product-comments/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        product: this.selectedProduct.id,
                        comment: this.commentText
                    })
                });
                if (res.ok) {
                    this.closeCommentModal();
                    await this.fetchComments(this.selectedProduct.id);
                } else {
                    const data = await res.json();
                    this.commentError = data.detail || 'Failed to submit comment.';
                }
            } catch (e) {
                this.commentError = 'Failed to submit comment.';
            }
            this.commentSubmitting = false;
        },
        async submitReview() {
            this.reviewSuccess = '';
            this.reviewError = '';
            if (!this.selectedProduct) return;
            if (!this.reviewForm.name || !this.reviewForm.email || !this.reviewForm.rating || !this.reviewForm.comment) {
                this.reviewError = 'Please fill in all fields and select a rating.';
                return;
            }
            const csrftoken = getCookie('csrftoken');
            try {
                const res = await fetch('/api/reviews/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrftoken
                    },
                    body: JSON.stringify({
                        product: this.selectedProduct.id,
                        customer_name: this.reviewForm.name,
                        customer_email: this.reviewForm.email,
                        rating: this.reviewForm.rating,
                        comment: this.reviewForm.comment
                    })
                });
                if (res.ok) {
                    this.reviewSuccess = 'Thank you! Your review has been submitted and will appear soon.';
                    this.reviewForm = { name: '', email: '', rating: 0, hoverRating: 0, comment: '' };
                    if (typeof this.fetchReviews === 'function') {
                        await this.fetchReviews(this.selectedProduct.id);
                    }
                } else {
                    const data = await res.json();
                    if (data.errors && (JSON.stringify(data.errors).includes('unique') || JSON.stringify(data.errors).includes('unique set'))) {
                        this.reviewError = 'You have already submitted a review for this product.';
                    } else {
                        this.reviewError = (data.detail || (data.errors && Object.values(data.errors).join(' ')) || 'Failed to submit review.');
                    }
                }
            } catch (e) {
                this.reviewError = 'Failed to submit review.';
            }
        },
        async fetchWishlist() {
            if (!this.isAuthenticated || !this.userEmail) return;
            try {
                const res = await fetch(`/api/wishlist/?customer_email=${encodeURIComponent(this.userEmail)}`);
                if (res.ok) {
                    this.wishlistItems = await res.json();
                } else {
                    this.wishlistItems = [];
                }
            } catch (e) {
                this.wishlistItems = [];
            }
        },
        async addToWishlist(product) {
            if (!this.isAuthenticated || !this.userEmail) {
                alert('Please log in to use the wishlist.');
                return;
            }
            const csrftoken = getCookie('csrftoken');
            try {
                const res = await fetch('/api/wishlist/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrftoken
                    },
                    body: JSON.stringify({
                        customer_email: this.userEmail,
                        product: product.id
                    })
                });
                if (res.ok) {
                    await this.fetchWishlist();
                } else {
                    const data = await res.json();
                    if (data.errors && JSON.stringify(data.errors).includes('unique')) {
                        // Already in wishlist, remove it
                        await this.removeFromWishlist(product);
                    }
                }
            } catch (e) {
                console.error('Failed to add to wishlist:', e);
            }
        },
        async removeFromWishlist(product) {
            if (!this.isAuthenticated || !this.userEmail) return;
            const csrftoken = getCookie('csrftoken');
            try {
                const res = await fetch('/api/wishlist/remove_item/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrftoken
                    },
                    body: JSON.stringify({
                        customer_email: this.userEmail,
                        product: product.id
                    })
                });
                if (res.ok) {
                    await this.fetchWishlist();
                }
            } catch (e) {
                console.error('Failed to remove from wishlist:', e);
            }
        },
        isInWishlist(product) {
            return this.wishlistItems.some(item => item.product.id === product.id);
        },
        
        // Checkout navigation methods
        nextCheckoutStep() {
            if (this.validateCurrentStep()) {
                if (this.checkoutStep < 3) {
                    this.checkoutStep++;
                    if (this.checkoutStep === 3) {
                        // Setup Stripe Elements when reaching payment step
                        setTimeout(() => {
                            if (this.cardElement) {
                                this.cardElement.mount('#card-element');
                            }
                        }, 100);
                    }
                }
            }
        },
        
        prevCheckoutStep() {
            if (this.checkoutStep > 1) {
                this.checkoutStep--;
            }
        },
        
        validateCurrentStep() {
            if (this.checkoutStep === 1) {
                const { customerInfo } = this.orderDetails;
                if (!customerInfo.firstName || !customerInfo.lastName || !customerInfo.email || !customerInfo.phone) {
                    alert('Please fill in all customer information fields.');
                    return false;
                }
            } else if (this.checkoutStep === 2) {
                const { deliveryInfo } = this.orderDetails;
                if (!deliveryInfo.address || !deliveryInfo.city || !deliveryInfo.state || !deliveryInfo.zipCode) {
                    alert('Please fill in all delivery information fields.');
                    return false;
                }
            }
            return true;
        },
        
        // Main payment processing function
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
                // Create order on backend
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
                
                const orderResponse = await fetch('/api/orders/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: JSON.stringify(orderData)
                });
                
                if (!orderResponse.ok) {
                    throw new Error('Failed to create order');
                }
                
                const orderResult = await orderResponse.json();
                
                // Confirm payment with Stripe
                const { error, paymentIntent } = await this.stripe.confirmCardPayment(
                    orderResult.client_secret,
                    {
                        payment_method: {
                            card: this.cardElement,
                            billing_details: {
                                name: `${this.orderDetails.customerInfo.firstName} ${this.orderDetails.customerInfo.lastName}`,
                                email: this.orderDetails.customerInfo.email,
                            },
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
                            'X-CSRFToken': getCookie('csrftoken')
                        },
                        body: JSON.stringify({
                            payment_intent_id: paymentIntent.id
                        })
                    });
                    
                    if (confirmResponse.ok) {
                        // Success!
                        this.orderSuccess = true;
                        this.orderSuccessMessage = 'Order placed successfully! You will receive a confirmation email shortly.';
                        this.cart = [];
                        this.checkoutOpen = false;
                        this.checkoutStep = 1;
                        
                        // Reset form
                        this.orderDetails = {
                            customerInfo: { firstName: '', lastName: '', email: '', phone: '' },
                            deliveryInfo: { address: '', city: '', state: '', zipCode: '', instructions: '' }
                        };
                    } else {
                        throw new Error('Failed to confirm payment');
                    }
                } else {
                    throw new Error('Payment was not successful');
                }
                
            } catch (error) {
                this.orderError = true;
                this.orderErrorMessage = error.message || 'An error occurred while processing your payment.';
            } finally {
                this.paymentProcessing = false;
            }
        }
    }));
});

function getCookie(name) {
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
} 