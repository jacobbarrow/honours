const start_time = new Date().getTime() / 1000;

const form = document.getElementsByTagName('form')[0];
const rating_input = document.getElementById('rating');
const time_taken_input = document.getElementById('time_taken');

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

form.onsubmit = function() {
    const end_time = new Date().getTime() / 1000;

    time_taken_input.value = end_time-start_time | 0;

    return true

}