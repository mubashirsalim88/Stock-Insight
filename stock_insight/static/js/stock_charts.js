(async () => {
    // Function to fetch and update chart data
    const updateChart = async (stockSymbol) => {
        const response = await fetch(`/fetch-historical-data/${stockSymbol}/`);
        const data = await response.json();

        if (data.error) {
            console.error('Error fetching data:', data.error);
            return;
        }

        const dailyCandles = data.day.data.candles;

        console.log("Original API Data:", dailyCandles);

        const ohlc = [],
              volume = [],
              dataLength = dailyCandles.length;

        for (let i = 0; i < dataLength; i += 1) {
            const timestamp = new Date(dailyCandles[i][0]).getTime();

            ohlc.push([
                timestamp,             // Date as timestamp
                dailyCandles[i][1],    // Open
                dailyCandles[i][2],    // High
                dailyCandles[i][3],    // Low
                dailyCandles[i][4]     // Close
            ]);

            volume.push([
                timestamp,             // Date as timestamp
                dailyCandles[i][5]     // Volume
            ]);
        }

        // Sort the arrays by timestamp (the first element in each array)
        ohlc.sort((a, b) => a[0] - b[0]);
        volume.sort((a, b) => a[0] - b[0]);

        console.log("Sorted OHLC Data:", ohlc);
        console.log("Sorted Volume Data:", volume);

        Highcharts.stockChart('chart-data', {
            chart: {
                height: 600
            },
            title: {
                text: `Historical Candlestick Chart - ${stockSymbol}`
            },
            legend: {
                enabled: true
            },
            rangeSelector: {
                selected: 2
            },
            yAxis: [{
                height: '60%'
            }, {
                top: '60%',
                height: '20%'
            }, {
                top: '80%',
                height: '20%'
            }],
            plotOptions: {
                series: {
                    showInLegend: true
                }
            },
            series: [{
                type: 'candlestick',
                id: 'stock',
                name: 'Stock Data',
                data: ohlc
            }, {
                type: 'column',
                id: 'volume',
                name: 'Volume',
                data: volume,
                yAxis: 1
            }, {
                type: 'macd',
                id: 'macd',
                linkedTo: 'stock',
                yAxis: 2
            }]
        });
    };

    // Attach event listeners to stock items
    document.querySelectorAll('.stock-item').forEach(item => {
        item.addEventListener('click', () => {
            const stockSymbol = item.getAttribute('data-symbol');
            updateChart(stockSymbol);
        });
    });

    // Load default chart for the first stock in the list
    const firstStock = document.querySelector('.stock-item').getAttribute('data-symbol');
    if (firstStock) {
        updateChart(firstStock);
    }
})();
