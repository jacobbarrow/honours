const rating_input = document.getElementById('rating');
const form = document.getElementsByTagName('form')[0];
const options = document.getElementsByClassName('option');

for(let i=0; i<options.length; i++) {
    options[i].addEventListener('click', clickHandler);
}

function clickHandler() {
    // First, unselect everything
    for(let i=0; i<options.length; i++) {
        options[i].classList.remove('selected');
    }

    // Then, select this option
    this.classList.add('selected')

    // Add the option's value to the hidden input
    rating_input.value = this.getAttribute('data-rating');
}
