// Alpine.js data and methods
// Simple product grid with category tabs, no advanced UX

document.addEventListener('alpine:init', () => {
    Alpine.data('app', () => ({
        products: [],
        activeCategory: 'all',
        init() {
            this.fetchProducts();
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
    }));
}); 