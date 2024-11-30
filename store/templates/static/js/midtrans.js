document.getElementById('payButton').addEventListener('click', function () {
    const order_id = document.getElementById('order_id').value;
    const gross_amount = document.getElementById('gross_amount').value;
    const first_name = document.getElementById('first_name').value;
    const last_name = document.getElementById('last_name').value;
    const email = document.getElementById('email').value;
    const phone = document.getElementById('phone').value;

    console.log("Sending data to backend...");

    // Fetch Snap Token from backendpu
    fetch('/create-transaction/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            order_id: order_id,
            gross_amount: parseInt(gross_amount),
            first_name: first_name,
            last_name: last_name,
            email: email,
            phone: phone
        }),
    })
    .then(response => response.json())
    .then(data => {
        console.log("Snap Token received:", data);

        // Check if token exists
        if (data.token) {
            snap.pay(data.token, {
                onSuccess: function (result) {
                    console.log(result);
                    alert("Payment Successful!");
                    window.location.href = "/payment-success/";
                },
                onPending: function (result) {
                    console.log(result);
                    alert("Payment Pending!");
                },
                onError: function (result) {
                    console.log(result);
                    alert("Payment Failed!");
                }
            });
        } else {
            alert("Failed to get Snap Token!");
        }
    })
    .catch(error => console.error('Error:', error));
});
