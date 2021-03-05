fetch('/data')
    .then(response => response.json())
    .then(data => {

        if(data != []) {
            console.log(data)

            let labels = [];
            window.body_data = [];
            window.headline_data = [];
            let i = 0;
            for (var date in data.body) {
                if (data.body.hasOwnProperty(date)) {
                    labels[i] = date
                    window.body_data[i] = data.body[date]
                    window.headline_data[i] = data.headline[date]
                    i++;
                }
            }
            console.log(labels)

            var ctx = document.getElementById('analysis_chart');
            window.analysis_chart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,

                    datasets: generateAverageDatasets(10)
                        // {
                        //     label: 'Headline',
                        //     data: headline_data,
                        //     backgroundColor: '#C5CAE9',
                        //     borderColor: '#C5CAE9'
                        // },
                        // {
                        //     label: 'Body',
                        //     backgroundColor: '#B2EBF2',
                        //     borderColor: '#B2EBF2',
                        //     data: body_data
                        // },
                },
                    options: {
                        elements: {
                            point:{
                                radius: 0
                            }
                        }
                    }
                
            });

        } else {
            console.log('no data on server')
        }
    });


function generateAverageDatasets(raw_percent) {
    let percent = raw_percent / 100;
    datasets = [{
            label: 'Body (avg)',
            borderColor: '#673AB7',
            fill: false,
            data: movingAvg(window.body_data, Math.round(window.headline_data.length * percent))
        },
        {
            label: 'Headline (avg)',
            borderColor: '#4CAF50',
            fill: false,
            data: movingAvg(window.headline_data, Math.round(window.headline_data.length * percent))
        }]

    return datasets
}

// This function is from https://stackoverflow.com/a/39263992/2650094
function movingAvg(array, count, qualifier){
    // calculate average for subarray
    var avg = function(array, qualifier){

        var sum = 0, count = 0, val;
        for (var i in array){
            val = array[i];
            if (!qualifier || qualifier(val)){
                sum += val;
                count++;
            }
        }

        return sum / count;
    };

    var result = [], val;

    // pad beginning of result with null values
    for (var i=0; i < count-1; i++)
        result.push(null);

    // calculate average for each subarray and add to result
    for (var i=0, len=array.length - count; i <= len; i++){

        val = avg(array.slice(i, i + count), qualifier);
        if (isNaN(val))
            result.push(null);
        else
            result.push(val);
    }

    return result;
}


document.getElementById('average_slider').addEventListener('change', function() {
    window.analysis_chart.data.datasets = generateAverageDatasets(this.value);
    window.analysis_chart.update(0);
})