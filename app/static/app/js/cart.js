var updateBtns = document.getElementsByClassName('update-cart');
console.log("💡 Đang gắn event update-cart:", updateBtns.length);

for (var i = 0; i < updateBtns.length; i++) {
    updateBtns[i].onclick = function(event) {
        event.preventDefault(); 
        var productId = this.dataset.product;
        var action = this.dataset.action;
        console.log('productId', productId, 'action', action);
        console.log('user: ', user);

        if (user === "AnonymousUser") {
            console.log('user not logged in');
        } else {
            updateUserOrder(productId, action);
        }
    }
}

function updateUserOrder(productId, action) {
    console.log('User logged in, success add');

    // URL cho API endpoint để cập nhật sản phẩm
    var url = '/update_item/';

    // Sử dụng fetch để gửi yêu cầu POST tới server
    fetch(url, {
        method: 'POST', // Phương thức POST
        headers: {
            'Content-Type': 'application/json', // Định dạng dữ liệu là JSON
            'X-CSRFToken': csrftoken
        },
        // Gửi dữ liệu dưới dạng JSON trong body
        body: JSON.stringify({ 'productId': productId, 'action': action }) 
    })
    .then((response) => {
        // Kiểm tra phản hồi từ server và chuyển đổi thành JSON
        return response.json(); 
    })
.then((data) => {
    console.log('Data:', data);

    // ✅ Cập nhật số lượng trong badge giỏ hàng
    const cartBadge = document.querySelector('.cart-badge');
    if (cartBadge) {
        cartBadge.innerText = data.cartItems;

        // Hiệu ứng nhấp nháy
        cartBadge.classList.add('flash');
        setTimeout(() => {
            cartBadge.classList.remove('flash');
        }, 500);
    }

    // ✅ Cập nhật số lượng hiển thị cho từng sản phẩm (trong bảng)
    const quantityEl = document.getElementById(`quantity-${data.productId}`);
    if (quantityEl) {
        quantityEl.innerText = data.newQuantity;
    }

    // ✅ Nếu số lượng = 0 → reload để xóa sản phẩm khỏi DOM
    if (data.newQuantity <= 0) {
        location.reload();
    }
})
    .catch((error) => {
        // Bắt lỗi nếu có bất kỳ vấn đề gì trong quá trình fetch
        console.error('Error:', error);
    });
}
console.log("✅ cart.js is loaded");