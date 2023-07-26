document.addEventListener('DOMContentLoaded', function() {
  // Keep track of medicine stock quantities
  const medicineStocks = {};

  
  // Fetch medicine data automatically when input value changes
  $('#medicine-select').on('input', function() {
    var selectedOption = $('#medicine-select-datalist option[value="' + $(this).val() + '"]');
    var medicineId = selectedOption.val();
    var price = selectedOption.data('price');
    var stock = selectedOption.data('total-in-stock');
    

    // Update the input values with the fetched data
    $('#medicine-id').val(medicineId);
    $('#base-price').val(price);
    $('#stock-number').val(stock);
    $('#selected-medicine-name').text(selectedOption.text());
    // Update the total stock number display
    $('#total-stock-number').text('(Available: ' + stock + ')');


  // Show or hide the hand-point-right icon
  if (selectedOption.text() !== '') {
    $('#hand-icon-medicine').show();
    $('#total-stock-number').show();
    $('#medicine-message').hide();
  } else {
    $('#hand-icon-medicine').hide();
    $('#total-stock-number').hide();
    $('#medicine-message').show();
  }



  

    // Limit the stock number input to the available quantity
    $('#stock-number').attr('max', stock); 
    $('#stock-number').attr('min', 1);

    // Update the tooltip based on the stock availability
    if (stock > 0) {
      $('#stock-number').addClass('is-valid');
      $('#stock-number').removeClass('is-invalid');
      $('#stock-number').siblings('.valid-tooltip').text('Looks good!');
      $('#stock-number').siblings('.invalid-tooltip').text('min order 1 | Available in stock: ' + stock);
    } else {
      $('#stock-number').addClass('is-invalid');
      $('#stock-number').removeClass('is-valid');
      $('#stock-number').siblings('.valid-tooltip').text('');
      $('#stock-number').siblings('.invalid-tooltip').text('Please Select medicine');
    }


    // Reset the stock input if it's empty or 0 or an invalid number
    if ($('#stock-number').val() === '' || $('#stock-number').val() === '0' || !/^(?:[1-9]\d*|0[1-9]\d*)$/.test($('#stock-number').val())) {
      $('#stock-number').addClass('is-invalid');
      $('#stock-number').removeClass('is-valid');
      $('#stock-number').siblings('.valid-tooltip').text('');
      $('#stock-number').siblings('.invalid-tooltip').text('stock not available!');
    }


  });

});


// Prevent submitting the form if the stock number is 0 or above the total stock quantity
$('#invoice-item-form').on('submit', function(e) {
  var stockNumber = parseInt($('#stock-number').val());
  var totalStock = parseInt($('#stock-number').attr('max'));

  if (stockNumber === 0 || stockNumber > totalStock) {
    e.preventDefault();
    $('#stock-number').siblings('.invalid-tooltip').text('min order 1 | Available in stock: ' + stock);
  }
});




$('#invoice-select').on('input', function() {
  var selectedOption = $('#invoice-select-datalist option[value="' + $(this).val() + '"]');
  var invoiceNumber = selectedOption.text();

  // Show or hide the invoice number and the hand-point-right icon
  if (invoiceNumber !== '') {
    $('#selected-invoice-number').text(invoiceNumber);
    $('#hand-icon-invoice-after').show();
    $('#hand-icon-invoice-before').hide();
    $('#invoice-message').hide();
  } else {
    $('#selected-invoice-number').text('');
    $('#hand-icon-invoice-before').show();
    $('#hand-icon-invoice-after').hide();
    $('#invoice-message').show();
  }
});





function updatePaymentFields() {
  var paymentMethod = document.getElementById('payment-method-field').value;
  var totalAmount = parseFloat(document.getElementById('total-amount-field').value);
  var cashAmount = document.getElementById('id_cash_payment_amount');
  var payLaterAmount = document.getElementById('id_pay_later_payment_amount');

  function updateCashAndPayLaterAmounts() {
      var cashInput = parseFloat(cashAmount.value);
      var payLaterInput = parseFloat(payLaterAmount.value);

      if (isNaN(cashInput)) {
          cashInput = 0;
      }
      if (isNaN(payLaterInput)) {
          payLaterInput = 0;
      }

      if (paymentMethod === 'split') {
          cashAmount.value = totalAmount - payLaterInput;
          payLaterAmount.value = totalAmount - cashInput;
      }
  }

  cashAmount.addEventListener('input', function () {
      updateCashAndPayLaterAmounts();
  });

  payLaterAmount.addEventListener('input', function () {
      updateCashAndPayLaterAmounts();
  });
}

// Call the function to initialize the event listeners
updatePaymentFields();