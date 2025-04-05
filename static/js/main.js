// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    const popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Handle favorite button click with AJAX
    const favoriteButtons = document.querySelectorAll('.btn-favorite');
    favoriteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Get recipe ID from data attribute
            const recipeId = this.getAttribute('data-recipe-id');
            
            // Send AJAX request
            fetch(`/toggle_favorite/${recipeId}`, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Type': 'application/json'
                },
                credentials: 'same-origin'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Toggle active class on button
                    this.classList.toggle('active');
                    
                    // Update icon
                    const icon = this.querySelector('i');
                    if (icon) {
                        if (data.is_favorite) {
                            icon.classList.remove('fa-heart-o');
                            icon.classList.add('fa-heart');
                        } else {
                            icon.classList.remove('fa-heart');
                            icon.classList.add('fa-heart-o');
                        }
                    }
                    
                    // Show a toast or small notification
                    showToast(data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showToast('An error occurred. Please try again.', 'danger');
            });
        });
    });

    // Function to show toast notifications
    function showToast(message, type = 'success') {
        // Check if toast container exists, if not create it
        let toastContainer = document.querySelector('.toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
            document.body.appendChild(toastContainer);
        }
        
        // Create the toast element
        const toastElement = document.createElement('div');
        toastElement.className = `toast align-items-center text-white bg-${type} border-0`;
        toastElement.setAttribute('role', 'alert');
        toastElement.setAttribute('aria-live', 'assertive');
        toastElement.setAttribute('aria-atomic', 'true');
        
        // Create the toast content
        toastElement.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;
        
        // Add the toast to the container
        toastContainer.appendChild(toastElement);
        
        // Initialize and show the toast
        const toast = new bootstrap.Toast(toastElement, {
            autohide: true,
            delay: 3000
        });
        toast.show();
        
        // Remove the toast element after it's hidden
        toastElement.addEventListener('hidden.bs.toast', function() {
            toastElement.remove();
        });
    }

    // Form validation for recipe form
    const recipeForm = document.querySelector('.recipe-form');
    if (recipeForm) {
        recipeForm.addEventListener('submit', function(e) {
            if (!this.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            
            this.classList.add('was-validated');
        });
    }

    // Handle ingredient add/remove
    const addIngredientBtn = document.getElementById('add-ingredient');
    if (addIngredientBtn) {
        addIngredientBtn.addEventListener('click', function() {
            const ingredientsContainer = document.getElementById('ingredients-container');
            const ingredientInputs = ingredientsContainer.querySelectorAll('.ingredient-input');
            const newIndex = ingredientInputs.length;
            
            const newIngredientRow = document.createElement('div');
            newIngredientRow.className = 'input-group mb-2 ingredient-input';
            newIngredientRow.innerHTML = `
                <input type="text" class="form-control" 
                       name="ingredient_${newIndex}" required
                       placeholder="Enter ingredient">
                <button type="button" class="btn btn-outline-danger remove-ingredient">
                    <i class="fa fa-times"></i>
                </button>
            `;
            
            ingredientsContainer.appendChild(newIngredientRow);
            
            // Add event listener to the remove button
            const removeBtn = newIngredientRow.querySelector('.remove-ingredient');
            removeBtn.addEventListener('click', function() {
                newIngredientRow.remove();
            });
        });
    }

    // Handle existing remove ingredient buttons
    const removeIngredientBtns = document.querySelectorAll('.remove-ingredient');
    removeIngredientBtns.forEach(button => {
        button.addEventListener('click', function() {
            this.closest('.ingredient-input').remove();
        });
    });

    // Handle instruction add/remove
    const addInstructionBtn = document.getElementById('add-instruction');
    if (addInstructionBtn) {
        addInstructionBtn.addEventListener('click', function() {
            const instructionsContainer = document.getElementById('instructions-container');
            const instructionInputs = instructionsContainer.querySelectorAll('.instruction-input');
            const newIndex = instructionInputs.length;
            
            const newInstructionRow = document.createElement('div');
            newInstructionRow.className = 'input-group mb-2 instruction-input';
            newInstructionRow.innerHTML = `
                <span class="input-group-text">${newIndex + 1}</span>
                <textarea class="form-control" 
                          name="instruction_${newIndex}" required
                          placeholder="Enter instruction step"></textarea>
                <button type="button" class="btn btn-outline-danger remove-instruction">
                    <i class="fa fa-times"></i>
                </button>
            `;
            
            instructionsContainer.appendChild(newInstructionRow);
            
            // Add event listener to the remove button
            const removeBtn = newInstructionRow.querySelector('.remove-instruction');
            removeBtn.addEventListener('click', function() {
                newInstructionRow.remove();
                // Renumber the steps
                renumberInstructions();
            });
        });
    }

    // Handle existing remove instruction buttons
    const removeInstructionBtns = document.querySelectorAll('.remove-instruction');
    removeInstructionBtns.forEach(button => {
        button.addEventListener('click', function() {
            this.closest('.instruction-input').remove();
            // Renumber the steps
            renumberInstructions();
        });
    });

    // Function to renumber instruction steps
    function renumberInstructions() {
        const instructionInputs = document.querySelectorAll('.instruction-input');
        instructionInputs.forEach((input, index) => {
            const stepNumber = input.querySelector('.input-group-text');
            if (stepNumber) {
                stepNumber.textContent = index + 1;
            }
        });
    }

    // Handle recipe delete confirmation
    const deleteRecipeForm = document.getElementById('delete-recipe-form');
    if (deleteRecipeForm) {
        deleteRecipeForm.addEventListener('submit', function(e) {
            if (!confirm('Are you sure you want to delete this recipe? This action cannot be undone.')) {
                e.preventDefault();
            }
        });
    }

    // Handle cuisine delete confirmation
    const deleteCuisineForm = document.getElementById('delete-cuisine-form');
    if (deleteCuisineForm) {
        deleteCuisineForm.addEventListener('submit', function(e) {
            if (!confirm('Are you sure you want to delete this cuisine? This action cannot be undone.')) {
                e.preventDefault();
            }
        });
    }

    // Animate elements when they come into view
    const animateOnScroll = function() {
        const elementsToAnimate = document.querySelectorAll('.animate-on-scroll');
        
        elementsToAnimate.forEach(element => {
            const elementPosition = element.getBoundingClientRect().top;
            const screenPosition = window.innerHeight / 1.2;
            
            if (elementPosition < screenPosition) {
                element.classList.add('fade-in');
            }
        });
    };
    
    // Run animation check on scroll and on load
    window.addEventListener('scroll', animateOnScroll);
    animateOnScroll(); // Run once on page load
});
