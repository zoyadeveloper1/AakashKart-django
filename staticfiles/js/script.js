document.addEventListener("DOMContentLoaded", function () {
    alert("Welcome to GreatKart! 🎉 Best deals on Home Appliances & Beauty!");
});

fetch("{% url 'create_paypal_order' %}", {
    method: "POST",
    body: new URLSearchParams({ "order_id": "{{ order.id }}" })
})

fetch(`/paypal/order/${data.orderID}/capture/`, {
    method: "POST",
    body: new URLSearchParams({ "order_id": "{{ order.id }}" }),
    headers: {"X-CSRFToken": "{{ csrf_token }}"}
})
