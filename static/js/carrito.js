let cart = [];

function addToCart(name, price, stock) {
  const existing = cart.find(item => item.name === name);
  if (existing) {
    if (existing.quantity < stock) {
      existing.quantity++;
    } else {
      alert("No hay más stock disponible para " + name);
      return;
    }
  } else {
    cart.push({ name: name, price: price, quantity: 1, stock: stock });
  }
  updateCart();
}

function updateCart() {
  const cartItemsDiv = document.getElementById('cart-items');
  if (!cartItemsDiv) return;

  cartItemsDiv.innerHTML = '';
  if (cart.length === 0) {
    cartItemsDiv.innerHTML = '<p class="text-muted mb-0">Aún no hay productos.</p>';
    return;
  }

  let total = 0;
  cart.forEach(item => {
    total += item.price * item.quantity;
    cartItemsDiv.innerHTML += `
      <div class="d-flex justify-content-between align-items-center mb-2">
        <span>${item.name} x${item.quantity}</span>
        <span>₡${item.price * item.quantity}</span>
      </div>`;
  });

  cartItemsDiv.innerHTML += `<hr><div class="fw-bold d-flex justify-content-between"><span>Total:</span><span>₡${total}</span></div>`;
}

document.getElementById('checkout-btn')?.addEventListener('click', () => {
  if (cart.length === 0) {
    alert("Tu carrito está vacío.");
  } else {
    alert("Compra finalizada correctamente.");
    cart = [];
    updateCart();
  }
});