(async () => {
    const timeframes = ['30minute', 'day'];

    // Store latestClose and percentageChange globally to keep them consistent
    let latestClose, percentageChange;

    const updateChart = async (stockSymbol, timeframe = 'day') => {
        // Fetch data for both daily and the selected timeframe
        const response = await fetch(`/fetch-historical-data/${stockSymbol}/?timeframe=${timeframe}`);
        const data = await response.json();

        if (data.error) {
            console.error('Error fetching data:', data.error);
            return;
        }

        // Calculate latestClose and percentageChange based on daily data only once
        if (timeframe === 'day' || (!latestClose && !percentageChange)) {
            if (data['day'] && data['day'].data && data['day'].data.candles.length > 1) {
                const dayCandles = data['day'].data.candles;

                // Extract the close price of the latest complete day (first candle in the array)
                latestClose = dayCandles[0][4];  // Latest close (first candle)

                // Extract the close price of the previous day (second candle in the array)
                const previousDayClose = dayCandles[1][4];  // Previous day's close (second candle)

                // Calculate the percentage change from the previous day's close
                percentageChange = ((latestClose - previousDayClose) / previousDayClose * 100).toFixed(2);
            } else {
                percentageChange = "N/A"; // Handle the case where there isn't enough data
                latestClose = "N/A";
            }
        }

        // Set the color based on positive or negative percentage change
        const changeColor = percentageChange >= 0 ? 'text-green-500' : 'text-red-500';

        // Update stock information display (This remains consistent)
        document.getElementById('stock-info').innerHTML = `
            ${stockSymbol} - ₹${latestClose} <span class="${changeColor}">(${percentageChange}%)</span>
        `;

        // Now process the data for the selected timeframe
        const candles = data[timeframe]?.data?.candles || [];
        const ohlc = [], volume = [];
        const dataLength = candles.length;

        for (let i = 0; i < dataLength; i += 1) {
            let timestamp;

            if (timeframe === 'day') {
                // Parse timestamp for daily data (yyyy-mm-dd)
                timestamp = Date.parse(candles[i][0].split('T')[0]);
            } else {
                // Parse timestamp for 30-minute data
                timestamp = Date.parse(candles[i][0]);

                const date = new Date(timestamp);
                const hours = date.getUTCHours() + 5;
                const minutes = date.getUTCMinutes() + 30;

                if (!((hours > 9 || (hours === 9 && minutes >= 15)) && (hours < 15 || (hours === 15 && minutes <= 30)))) {
                    continue;
                }
            }

            ohlc.push([
                timestamp,
                candles[i][1], // Open
                candles[i][2], // High
                candles[i][3], // Low
                candles[i][4]  // Close
            ]);

            volume.push([
                timestamp,
                candles[i][5] // Volume
            ]);
        }

        // Ensure sorted data for the chart
        ohlc.sort((a, b) => a[0] - b[0]);
        volume.sort((a, b) => a[0] - b[0]);

        let rangeSelectorButtons = [];
        let selectedRangeIndex = 0;

        if (timeframe === '30minute') {
            rangeSelectorButtons = [
                { type: 'day', count: 1, text: '1d' },
                { type: 'day', count: 5, text: '5d' },
                { type: 'day', count: 15, text: '15d' },
                { type: 'day', count: 30, text: '30d' },
                { type: 'all', text: 'All' }
            ];
            selectedRangeIndex = 1;
        } else {
            rangeSelectorButtons = [
                { type: 'month', count: 1, text: '1m' },
                { type: 'month', count: 3, text: '3m' },
                { type: 'month', count: 6, text: '6m' },
                { type: 'year', count: 1, text: '1y' },
                { type: 'all', text: 'All' }
            ];
            selectedRangeIndex = 1;
        }

        Highcharts.setOptions({
            time: {
                timezoneOffset: -330
            }
        });

        Highcharts.stockChart('chart-data', {
            chart: {
                height: 600
            },
            rangeSelector: {
                buttons: rangeSelectorButtons,
                selected: selectedRangeIndex
            },
            yAxis: [{
                height: '60%',
                labels: {
                    align: 'left',
                    x: -3
                }
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
                yAxis: 2,
                lineWidth: 1.5,
                macdLine: {
                    styles: {
                        lineWidth: 1.5
                    }
                }
            }]
        });

        highlightTimeframeButton(timeframe);
    };

    const highlightTimeframeButton = (timeframe) => {
        document.querySelectorAll('.timeframe-button').forEach(button => {
            if (button.getAttribute('data-timeframe') === timeframe) {
                button.classList.add('bg-blue-500', 'text-white');
            } else {
                button.classList.remove('bg-blue-500', 'text-white');
            }
        });
    };

    const initializeTimeframeButtons = (stockSymbol) => {
        const timeframeButtonsContainer = document.getElementById('timeframe-buttons');
        timeframeButtonsContainer.innerHTML = '';

        timeframes.forEach(timeframe => {
            const button = document.createElement('button');
            button.innerText = timeframe.charAt(0).toUpperCase() + timeframe.slice(1);
            button.className = 'timeframe-button px-1 py-1 text-xs rounded-lg border border-blue-500';
            button.setAttribute('data-timeframe', timeframe);
            button.addEventListener('click', () => {
                highlightTimeframeButton(timeframe);
                updateChart(stockSymbol, timeframe);
            });
            timeframeButtonsContainer.appendChild(button);
        });

        highlightTimeframeButton('day');
    };

    document.querySelectorAll('.stock-item').forEach(item => {
        item.addEventListener('click', () => {
            const stockSymbol = item.getAttribute('data-symbol');
            initializeTimeframeButtons(stockSymbol);
            updateChart(stockSymbol);
        });
    });

    const firstStock = document.querySelector('.stock-item').getAttribute('data-symbol');
    if (firstStock) {
        initializeTimeframeButtons(firstStock);
        updateChart(firstStock);
    }
})();

// Search functionality for filtering stocks in the sidebar
document.getElementById('stock-search').addEventListener('input', function () {
    const searchValue = this.value.toLowerCase();
    const stockItems = document.querySelectorAll('.stock-item');

    stockItems.forEach(item => {
        const stockName = item.textContent.toLowerCase();
        if (stockName.includes(searchValue)) {
            item.style.display = 'block';
        } else {
            item.style.display = 'none';
        }
    });
});
