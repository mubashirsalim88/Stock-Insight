(async () => {
    const timeframes = ['30minute', 'day'];

    const updateChart = async (stockSymbol, timeframe = 'day') => {
        const dailyResponse = await fetch(`/fetch-historical-data/${stockSymbol}/?timeframe=day`);
        const dailyData = await dailyResponse.json();

        if (dailyData.error) {
            console.error('Error fetching daily data:', dailyData.error);
            return;
        }

        const dailyCandles = dailyData.day.data.candles;
        const dailyDataLength = dailyCandles.length;

        const latestPrice = dailyCandles[dailyDataLength - 1][4];
        const previousClose = dailyCandles[dailyDataLength - 2][4];
        const percentageChange = ((latestPrice - previousClose) / previousClose * 100).toFixed(2);

        // Set the color based on positive or negative percentage change
        const changeColor = percentageChange >= 0 ? 'text-green-500' : 'text-red-500';

        document.getElementById('stock-info').innerHTML = `
            ${stockSymbol} - ₹${latestPrice} <span class="${changeColor}">(${percentageChange}%)</span>
        `;

        const response = await fetch(`/fetch-historical-data/${stockSymbol}/?timeframe=${timeframe}`);
        const data = await response.json();

        if (data.error) {
            console.error('Error fetching data:', data.error);
            return;
        }

        const candles = data[timeframe].data.candles;

        const ohlc = [],
            volume = [],
            dataLength = candles.length;

        for (let i = 0; i < dataLength; i += 1) {
            let timestamp;

            if (timeframe === 'day') {
                timestamp = Date.parse(candles[i][0].split('T')[0]);
            } else {
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
                candles[i][1],
                candles[i][2],
                candles[i][3],
                candles[i][4]
            ]);

            volume.push([
                timestamp,
                candles[i][5]
            ]);
        }

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
                    align: 'left', // Align labels to the left to give more space
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
            },  {
                type: 'macd',
                id: 'macd',
                linkedTo: 'stock',
                yAxis: 2,
                lineWidth: 1.5, // Adjust this value to make the MACD line thinner
                macdLine: {
                    styles: {
                        lineWidth: 1.5 // This controls the thickness of the MACD line (red line)
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
document.getElementById('stock-search').addEventListener('input', function() {
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
