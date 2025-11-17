/* ============================
      CARRITO GLOBAL
============================ */

// --- Cargar carrito desde localStorage ---
let cart = JSON.parse(localStorage.getItem("cart")) || [];

// --- Guardar carrito ---
function saveCart() {
  localStorage.setItem("cart", JSON.stringify(cart));
}

/* ============================
    AGREGAR PRODUCTO AL CARRITO
============================ */
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
    cart.push({ name, price, quantity: 1, stock });
  }

  saveCart();
  updateCart();
}

/* ============================
       MOSTRAR CARRITO
============================ */
function updateCart() {
  const cartItemsDiv = document.getElementById('cart-items');
  if (!cartItemsDiv) return;

  cartItemsDiv.innerHTML = '';

  if (cart.length === 0) {
    cartItemsDiv.innerHTML = '<p class="text-muted mb-0">Aún no hay productos.</p>';
    updateCartCount();
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

  cartItemsDiv.innerHTML += `
    <hr>
    <div class="fw-bold d-flex justify-content-between">
      <span>Total:</span>
      <span>₡${total}</span>
    </div>
  `;

  updateCartCount();
}

/* ============================
    CONTADOR SOBRE EL ÍCONO
============================ */
function updateCartCount() {
  let count = cart.reduce((sum, item) => sum + item.quantity, 0);

  const cartIcon = document.getElementById("cartDropdown");
  if (!cartIcon) return;

  let counter = document.getElementById("cart-count-nav");

  if (!counter) {
    counter = document.createElement("span");
    counter.id = "cart-count-nav";
    counter.style.position = "absolute";
    counter.style.top = "-5px";
    counter.style.right = "-10px";
    counter.style.background = "red";
    counter.style.color = "#fff";
    counter.style.fontSize = "0.75rem";
    counter.style.padding = "3px 6px";
    counter.style.borderRadius = "50%";
    counter.style.fontWeight = "bold";
    cartIcon.parentElement.style.position = "relative";
    cartIcon.parentElement.appendChild(counter);
  }

  counter.textContent = count;
}

/* ============================
    FINALIZAR COMPRA (Con Flask)
============================ */
document.getElementById('checkout-btn')?.addEventListener('click', () => {
  if (cart.length === 0) {
    alert("Tu carrito está vacío.");
    return;
  }

  fetch("/finalizar_compra", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ carrito: cart })
  })
  .then(res => res.json())
  .then(data => {
    if (data.status === "success") {
      alert("Compra finalizada correctamente.");
      cart = [];
      saveCart();
      updateCart();
      location.reload(); // actualiza stock visual
    } else {
      alert(data.message);
    }
  })
  .catch(err => console.error("Error:", err));
});

/* ============================
  INICIALIZAR AL CARGAR PÁGINA
============================ */
document.addEventListener("DOMContentLoaded", () => {
  updateCart();
});
