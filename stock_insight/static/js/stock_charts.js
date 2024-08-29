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

        const ohlc = [],
              volume = [],
              dataLength = dailyCandles.length;

        for (let i = 0; i < dataLength; i += 1) {
            ohlc.push([
                dailyCandles[i][0], // the date
                dailyCandles[i][1], // open
                dailyCandles[i][2], // high
                dailyCandles[i][3], // low
                dailyCandles[i][4] // close
            ]);

            volume.push([
                dailyCandles[i][0], // the date
                dailyCandles[i][5] // the volume
            ]);
        }

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
