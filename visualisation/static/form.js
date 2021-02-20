window.onload = function() {
    
    // Get some key elements of the form
    form_el = document.getElementsByTagName('form')[0];
    period_full_el = document.getElementById('period_full');
    period_start_el = document.getElementById('period_start');
    period_end_el = document.getElementById('period_end');

    analysis_method_el = document.getElementById('analysis_method');
    analysis_options_els = document.getElementsByClassName('analysis-options');

    fieldset_els = document.getElementsByTagName('fieldset')

    // Disable period dates when full period is selected
    period_full_el.onchange = function() {
        period_start_el.disabled = this.checked;
        period_end_el.disabled = this.checked;
    }

    // Change the analysis options depending on which sort is selected
    analysis_method_el.onchange = function() {
        for(let i = 0; i < analysis_options_els.length; i++) {

            let analysis_options_el = analysis_options_els[i];

            if(analysis_options_el.getAttribute('data-for') == analysis_method_el.value) {
                analysis_options_els[i].style.display = 'block';    
                analysis_options_el.setAttribute('aria-hidden', 'false');
            } else {
                analysis_options_els[i].style.display = 'none';    
                analysis_options_el.setAttribute('aria-hidden', 'true');
            }
        }
    }

    // Add error messages (passed back through the URL)
    let url_parameters = new URL(window.location.href).searchParams; 

    let fieldset_name = url_parameters.get('fieldset');
    let error_message = url_parameters.get('message');

    if(fieldset_name && error_message) {
        // Find the fieldset with the error
        for(let i = 0; i < fieldset_els.length; i++) {
            fieldset_el = fieldset_els[i];

            if(fieldset_el.getAttribute('data-for') == fieldset_name) {
                // Create the error element
                error_el = document.createElement('div');
                error_el.innerHTML = error_message;
                error_el.classList.add('error');

                // Add it to the end of the fieldset
                fieldset_el.append(error_el);
            }
        }
    }
}
