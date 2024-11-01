let latestPrice;

(async () => {
    const timeframes = ['30minute', 'day'];
    let latestClose, percentageChange;

    const updateTradeButtons = (enabled) => {
        document.getElementById('buy-button').disabled = !enabled;
        document.getElementById('sell-button').disabled = !enabled;
    };

    const updateChart = async (stockSymbol, timeframe = 'day') => {
        const response = await fetch(`/fetch-historical-data/${stockSymbol}/?timeframe=${timeframe}`);
        const data = await response.json();

        if (data.error) {
            console.error('Error fetching data:', data.error);
            document.getElementById('trade-message').innerText = "Failed to load data.";
            updateTradeButtons(false);
            return;
        }

        // Calculate latest close and percentage change
        if (timeframe === 'day' || (!latestClose && !percentageChange)) {
            if (data['day'] && data['day'].data && data['day'].data.candles.length > 1) {
                const dayCandles = data['day'].data.candles;
                latestClose = dayCandles[0][4];
                const previousDayClose = dayCandles[1][4];
                percentageChange = ((latestClose - previousDayClose) / previousDayClose * 100).toFixed(2);
                latestPrice = latestClose; // Ensure latestPrice is set here
            } else {
                percentageChange = "N/A";
                latestClose = "N/A";
                latestPrice = null; // Set to null if data is not available
            }
        }

        const changeColor = percentageChange >= 0 ? 'text-green-500' : 'text-red-500';
        document.getElementById('stock-info').innerHTML = `
            ${stockSymbol} - ₹${latestClose} <span class="${changeColor}">(${percentageChange}%)</span>
        `;

        const candles = data[timeframe]?.data?.candles || [];
        const ohlc = [], volume = [];
        candles.forEach(candle => {
            const timestamp = timeframe === 'day'
                ? Date.parse(candle[0].split('T')[0])
                : Date.parse(candle[0]);
            ohlc.push([timestamp, candle[1], candle[2], candle[3], candle[4]]);
            volume.push([timestamp, candle[5]]);
        });

        ohlc.sort((a, b) => a[0] - b[0]);
        volume.sort((a, b) => a[0] - b[0]);

        Highcharts.setOptions({ time: { timezoneOffset: -330 } });
        Highcharts.stockChart('chart-data', {
            chart: { height: 600 },
            rangeSelector: {
                buttons: timeframe === '30minute' ? [
                    { type: 'day', count: 1, text: '1d' },
                    { type: 'day', count: 5, text: '5d' },
                    { type: 'day', count: 15, text: '15d' },
                    { type: 'day', count: 30, text: '30d' },
                    { type: 'all', text: 'All' }
                ] : [
                    { type: 'month', count: 1, text: '1m' },
                    { type: 'month', count: 3, text: '3m' },
                    { type: 'month', count: 6, text: '6m' },
                    { type: 'year', count: 1, text: '1y' },
                    { type: 'all', text: 'All' }
                ],
                selected: 1
            },
            yAxis: [{
                height: '60%',
                labels: { align: 'left', x: -3 }
            }, {
                top: '60%',
                height: '20%'
            }, {
                top: '80%',
                height: '20%'
            }],
            plotOptions: { series: { showInLegend: true } },
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
                macdLine: { styles: { lineWidth: 1.5 } }
            }]
        });
        highlightTimeframeButton(timeframe);
        updateTradeButtons(latestPrice !== null);
    };

    const highlightTimeframeButton = (timeframe) => {
        document.querySelectorAll('.timeframe-button').forEach(button => {
            button.classList.toggle('bg-blue-500', button.getAttribute('data-timeframe') === timeframe);
            button.classList.toggle('text-white', button.getAttribute('data-timeframe') === timeframe);
        });
    };

    const initializeTimeframeButtons = (stockSymbol) => {
        document.getElementById('trade-symbol').value = stockSymbol;  // Update trade-symbol with selected stock
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
        item.addEventListener('click', async () => {
            const stockSymbol = item.getAttribute('data-symbol');
            initializeTimeframeButtons(stockSymbol);
            await updateChart(stockSymbol);
        });
    });

    // Load the first stock on page load
    const firstStock = document.querySelector('.stock-item').getAttribute('data-symbol');
    if (firstStock) {
        initializeTimeframeButtons(firstStock);
        await updateChart(firstStock);
    }
})();

// Search and buy/sell event listeners
document.getElementById('stock-search').addEventListener('input', function () {
    const searchValue = this.value.toLowerCase();
    document.querySelectorAll('.stock-item').forEach(item => {
        item.style.display = item.textContent.toLowerCase().includes(searchValue) ? 'block' : 'none';
    });
});

const tradeStock = async (action) => {
    const stockSymbol = document.getElementById('trade-symbol').value;
    const shares = document.getElementById('trade-shares').value;

    if (!stockSymbol || !shares || shares <= 0) {
        document.getElementById('trade-message').innerText = "Please enter a valid stock and number of shares.";
        return;
    }

    if (latestPrice == null) { // Check if the latestPrice is set
        console.log('Latest Price is not set.'); // Log for debugging
        document.getElementById('trade-message').innerText = "Price is required.";
        return;
    }

    console.log('Price being sent:', latestPrice); // Log price before sending
    const response = await fetch('/trade-stock/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            symbol: stockSymbol,
            shares: shares,
            action: action,
            price: latestPrice // Include the latestPrice in the request
        }),
    });

    const data = await response.json();
    if (data.error) {
        document.getElementById('trade-message').innerText = data.error;
    } else {
        document.getElementById('trade-message').innerText = `Trade successful! ${action} ${shares} shares of ${stockSymbol} at ₹${latestPrice}.`;
        document.getElementById('trade-shares').value = ''; // Clear shares input after trade
    }
};

document.getElementById('buy-button').addEventListener('click', () => tradeStock('buy'));
document.getElementById('sell-button').addEventListener('click', () => tradeStock('sell'));
