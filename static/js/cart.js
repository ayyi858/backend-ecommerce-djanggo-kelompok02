// Update Cart Buttons
const updateBtns = document.querySelectorAll('.update-cart');

// Add click event listeners to all update buttons
updateBtns.forEach((btn) => {
    btn.addEventListener('click', async () => {
        const productId = btn.dataset.product;
        const action = btn.dataset.action;

        console.log(`Product ID: ${productId}, Action: ${action}`);
        console.log(`User: ${user}`);

        // Add animation feedback for button click
        animateButton(btn);

        // Show loading spinner
        const spinner = createLoadingSpinner();
        btn.appendChild(spinner);

        // Handle cart update based on user authentication
        if (user === 'AnonymousUser') {
            addCookieItem(productId, action);
        } else {
            await updateUserOrder(productId, action);
        }

        // Remove loading spinner after action
        spinner.remove();
    });
});

// Function to update order for authenticated users
const updateUserOrder = async (productId, action) => {
    console.log('User is authenticated, sending data...');

    const url = '/update_item/';
    const payload = { productId, action };

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken,
            },
            body: JSON.stringify(payload),
        });

        const data = await response.json();
        console.log('Order updated successfully:', data);

        // Reload page to reflect changes
        location.reload();
    } catch (error) {
        console.error('Error updating order:', error);
    }
};

// Function to handle cart updates for anonymous users
const addCookieItem = (productId, action) => {
    console.log('User is not authenticated');

    if (action === 'add') {
        cart[productId] = cart[productId] || { quantity: 0 };
        cart[productId].quantity += 1;
    }

    if (action === 'remove') {
        if (cart[productId]) {
            cart[productId].quantity -= 1;

            // Remove item from cart if quantity is zero or less
            if (cart[productId].quantity <= 0) {
                console.log('Item removed from cart');
                delete cart[productId];
            }
        }
    }

    console.log('Updated Cart:', cart);
    document.cookie = `cart=${JSON.stringify(cart)};domain=;path=/`;

    // Reload page to reflect changes
    location.reload();
};

// Function to add animation feedback to buttons
const animateButton = (btn) => {
    btn.style.transition = 'transform 0.2s ease-in-out';
    btn.style.transform = 'scale(1.1)';
    setTimeout(() => {
        btn.style.transform = 'scale(1)';
    }, 200);
};

// Function to create a loading spinner
const createLoadingSpinner = () => {
    const spinner = document.createElement('span');
    spinner.className = 'loading-spinner';
    spinner.style.display = 'inline-block';
    spinner.style.width = '12px';
    spinner.style.height = '12px';
    spinner.style.marginLeft = '8px';
    spinner.style.border = '2px solid #f3f3f3';
    spinner.style.borderTop = '2px solid #3498db';
    spinner.style.borderRadius = '50%';
    spinner.style.animation = 'spin 0.6s linear infinite';
    return spinner;
};

// CSS Animation for Spinner (added dynamically via JS)
const style = document.createElement('style');
style.innerHTML = `
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
`;
document.head.appendChild(style);
