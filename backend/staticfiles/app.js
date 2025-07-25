// Alpine.js data and methods
// Simple product grid with category tabs, no advanced UX

document.addEventListener('alpine:init', () => {
    Alpine.data('app', () => ({
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
            },
            paymentInfo: {
                cardNumber: '',
                expiry: '',
                cvv: ''
            }
        },
        cateringServices: [],
        serviceModalOpen: false,
        selectedService: null,
        siteSettings: {
            site_name: 'CHOPHOUSE',
            tagline: 'Premium finger foods and catering services for all your special occasions.',
            phone: '+1 (555) 123-4567',
            email: 'info@chophouse.com',
            address: '123 Food Street, Culinary District',
            hours: 'Mon-Sat: 9AM-9PM',
        },
        loadingProducts: false,
        selectedProduct: null,
        productModalOpen: false,
        isAuthenticated: true, // Set to true for demo/testing
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
        init() {
            this.fetchProducts();
            this.fetchCateringServices();
        },
        async fetchProducts() {
            this.loadingProducts = true;
            try {
                const res = await fetch('/api/products/');
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
            item.quantity += change;
            if (item.quantity <= 0) {
                this.cart = this.cart.filter(cartItem => cartItem.id !== item.id);
            }
        },
        continueShopping() {
            this.cartOpen = false;
        },
        checkout() {
            this.cartOpen = false;
            this.checkoutOpen = true;
            this.checkoutStep = 1;
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
    }));
}); 