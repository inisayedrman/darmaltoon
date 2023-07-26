document.addEventListener('DOMContentLoaded', function() {
    // Keep track of medicine stock quantities
    const medicineStocks = {};
  
    // Fetch company data automatically when medicine is selected in cart
    $('#medicine-select').change(function() {
      var selectedOption = $(this).find('option:selected');
      var companyName = selectedOption.data('company');
      var price = selectedOption.data('price');
      var stock = selectedOption.data('total-in-stock');
      var strip = selectedOption.data('strip');
      var medicineId = selectedOption.val();
  
      // Update the company name, price, stock, and strip fields with the fetched data
      $('#company-name').val(companyName);
      $('#base-price').val(price);
      $('#stock-number').val(stock);
      $('#strip-number').val(strip);
  
      // Limit the stock number input to the available quantity
      $('#stock-number').attr('max', stock);
      $('#stock-number').attr('min', 0);
  
      // Update the medicine stock quantity
      medicineStocks[medicineId] = stock;
  
      // Recalculate total price when medicine is changed
      calculateTotalPrice();
    });
  
    // Select customer search in cart
    $('#customer-select').select2({
      theme: 'classic',
      placeholder: 'Choose Customer',
      allowClear: true
    });
  
    $('#medicine-select').select2({
      theme: 'classic',
      placeholder: 'Choose Medicine',
      allowClear: true
    });
  
    $('#customer_name').on('input', function() {
      var filter = $(this).val().toLowerCase();
      $('#customer-select option').each(function() {
        var text = $(this).text().toLowerCase();
        if (text.includes(filter)) {
          $(this).show();
        } else {
          $(this).hide();
        }
      });
    });
  
    const medicineSelect = document.getElementById('medicine-select');
    const priceInput = document.getElementById('base-price');
    const stockInput = document.getElementById('stock-number');
    const stripInput = document.getElementById('strip-number');
    const discountInput = document.getElementById('discount');
    const totalPriceInput = document.getElementById('total-price');
    const cartTableBody = document.getElementById('cart-table-body');
  
    function calculateTotalPrice() {
      const stock = parseInt(stockInput.value) || 0;
      const price = parseFloat(priceInput.value) || 0;
      const discount = parseFloat(discountInput.value) || 0;
  
      const totalPrice = (stock * price) - (stock * discount);
      totalPriceInput.value = totalPrice.toFixed(2);
    }
  
    function calculateStockInCart(medicineId) {
      let stockInCart = 0;
      const rows = cartTableBody.querySelectorAll('tr');
      rows.forEach(function(row) {
        const cartMedicineId = row.getAttribute('data-medicine-id');
        if (cartMedicineId === medicineId) {
          const quantityCell = row.querySelector('.quantity');
          const quantity = parseInt(quantityCell.textContent);
          stockInCart += quantity;
        }
      });
      return stockInCart;
    }
  
  document.addEventListener('DOMContentLoaded', function() {
      // Your code here, including the line that causes the error
   
    medicineSelect.addEventListener('change', function() {
      const selectedOption = medicineSelect.options[medicineSelect.selectedIndex];
      const price = selectedOption.getAttribute('data-price');
      const stock = selectedOption.getAttribute('data-total-in-stock');
      const strip = selectedOption.getAttribute('data-strip');
  
      // Update the input values with the fetched data
      priceInput.value = price;
      stockInput.value = stock;
      stripInput.value = strip;
  
      // Recalculate total price when medicine is changed
      calculateTotalPrice();
    });
  
    stockInput.addEventListener('input', calculateTotalPrice);
    discountInput.addEventListener('input', calculateTotalPrice);
  });
  
  
  
    const addToCartButton = document.getElementById('add-to-cart');
  
    addToCartButton.addEventListener('click', function(event) {
      event.preventDefault();
  
      const customerSelect = document.getElementById('customer-select');
      const selectedCustomer = customerSelect.options[customerSelect.selectedIndex];
      const customerName = selectedCustomer.text;
  
      const medicineSelect = document.getElementById('medicine-select');
      const selectedMedicine = medicineSelect.options[medicineSelect.selectedIndex];
      const medicineName = selectedMedicine.text;
      const medicineId = selectedMedicine.value;
  
      const companyName = $('#company-name').val();
      const quantity = parseInt(stockInput.value) || 0;
      const price = parseFloat(priceInput.value) || 0;
      const discount = parseFloat(discountInput.value) || 0;
      const totalPrice = parseFloat(totalPriceInput.value) || 0;
  
      // Check if any required fields are empty
      if (customerName.trim() === '' || medicineName.trim() === '' || companyName.trim() === '' || quantity === 0) {
        alert('Please fill in all the required fields.');
        return; // Stop execution if any required fields are empty
      }
  
      // Check if the selected medicine has reached the maximum stock quantity in the cart
      const selectedMedicineStock = medicineStocks[medicineId];
      if (selectedMedicineStock < quantity) {
        alert('The maximum stock quantity has been reached for this medicine.');
        return; // Stop execution if the maximum stock quantity has been reached
      } else if (selectedMedicineStock === quantity) {
        // Remove the medicine from the options list if the stock is completely used
        selectedMedicine.remove();
      }
  
      // Decrease the medicine stock quantity
      medicineStocks[medicineId] -= quantity;
  
      // Check if the medicine is already in the cart
      const medicineInCart = Array.from(cartTableBody.children).find(row => {
        const medicineIdCell = row.querySelector('.medicine-id');
        const medicineNameCell = row.querySelector('.medicine-name');
        const companyNameCell = row.querySelector('.company-name');
  
        // Check if any of the required cells are null
        if (!medicineIdCell || !medicineNameCell || !companyNameCell) {
          return false;
        }
  
        const cartMedicineId = medicineIdCell.textContent;
        const cartMedicineName = medicineNameCell.textContent;
        const cartCompanyName = companyNameCell.textContent;
  
        return cartMedicineId !== medicineId && cartMedicineName === medicineName && cartCompanyName === companyName;
      });
  
      if (medicineInCart) {
        alert('Medicine is already added to the cart.');
        return; // Stop execution if the medicine is already in the cart
      }
  
      // Create a new row in the cart table
      const newRow = document.createElement('tr');
  
      // Create customer cell
      const customerCell = document.createElement('td');
      customerCell.textContent = customerName;
      newRow.appendChild(customerCell);
  
      // Create medicine cell
      const medicineCell = document.createElement('td');
      medicineCell.textContent = medicineName;
      newRow.appendChild(medicineCell);
  
      // Create company cell
      const companyCell = document.createElement('td');
      companyCell.textContent = companyName;
      newRow.appendChild(companyCell);
  
      // Create quantity cell
      const quantityCell = document.createElement('td');
      quantityCell.textContent = quantity;
      newRow.appendChild(quantityCell);
  
      // Create price cell
      const priceCell = document.createElement('td');
      priceCell.textContent = 'AFN ' + price.toFixed(2);
      newRow.appendChild(priceCell);
  
      // Create discount cell
      const discountCell = document.createElement('td');
      discountCell.textContent = discount.toFixed(2);
      newRow.appendChild(discountCell);
  
      // Create total cell
      const totalCell = document.createElement('td');
      totalCell.textContent = 'AFN ' + totalPrice.toFixed(2);
      newRow.appendChild(totalCell);
  
      const initialStockQuantity = selectedMedicineStock;
  
      // Fetch the remaining stock from the selected medicine option
      const remainingStock = parseInt(selectedMedicine.dataset.totalInStock);
  
      // Check if the selected quantity exceeds the remaining stock
      if (quantity > remainingStock) {
        alert('Selected quantity exceeds the available stock.');
        return; // Stop execution if the selected quantity exceeds the stock
      }
  
      // Deduct the selected quantity from the remaining stock
      const updatedRemainingStock = remainingStock - quantity;
  
      // Update the stock value in the medicine select options list
      selectedMedicine.dataset.totalInStock = updatedRemainingStock;
  
      // Create edit button cell
      const editButtonCell = document.createElement('td');
      const editButton = document.createElement('button');
      editButton.textContent = 'Edit';
      editButton.addEventListener('click', function() {
        handleEditButtonClick(medicineId, price, discount);
      });
      editButtonCell.appendChild(editButton);
      newRow.appendChild(editButtonCell);
  
      // Create delete button cell
      const deleteButtonCell = document.createElement('td');
      const deleteButton = document.createElement('button');
      deleteButton.textContent = 'Delete';
      deleteButton.addEventListener('click', function() {
        // Handle delete button click event
        // You can implement your own logic here
        // Restore the stock quantity in the medicine select options
        const optionToUpdate = $('#medicine-select').find(`option[value="${medicineId}"]`);
        const originalStock = optionToUpdate.data('total-in-stock');
        optionToUpdate.data('total-in-stock', originalStock + quantity);
        optionToUpdate.attr('data-total-in-stock', originalStock + quantity);
        // Remove the row from the table
        newRow.remove();
        // Add the medicine back to the options list
        const option = document.createElement('option');
        option.value = medicineId;
        option.textContent = medicineName;
        medicineSelect.appendChild(option);
  
        // Perform any necessary calculations or updates here
        calculateTotalPrice(); // Recalculate the total price
      });
      deleteButtonCell.appendChild(deleteButton);
      newRow.appendChild(deleteButtonCell);
  
      // Append the new row to the cart table
      cartTableBody.appendChild(newRow);
  
      // Reset the form and price input
      $('#cart-form')[0].reset();
      priceInput.value = ''; // Reset the price input field
  
      // Remove currency symbol before submitting the price to the database
      const priceWithoutCurrency = price.toFixed(2); // Price without currency symbol
  
      // Now you can submit the priceWithoutCurrency value to the database
      // ...
    });
  });
  