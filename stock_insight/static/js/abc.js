$(document).ready(function () {
    function fetchStockData(symbol, timeframe = 'day') {
        $.get(`/fetch-historical-data/${symbol}/`, function (data) {
            console.log('API Response:', data);

            if (data.error) {
                $('#chart-data').html('<p>Error: ' + data.error + '</p>');
                return;
            }

            // Select the appropriate data based on the timeframe
            var chartData = [];
            var latestClose, previousDayClose, percentageChange;

            // Process daily data to calculate percentage change
            if (data['day'].data && data['day'].data.candles.length > 1) {
                var dayCandles = data['day'].data.candles;

                // Extract the close price of the latest complete day
                latestClose = dayCandles[0][4];  // Latest close (first candle)

                // Extract the close price of the previous day
                previousDayClose = dayCandles[1][4];  // Previous day's close (second candle)

                // Calculate the percentage change from the previous day's close
                percentageChange = ((latestClose - previousDayClose) / previousDayClose * 100).toFixed(2);
            } else {
                percentageChange = "N/A"; // Handle case where there isn't enough data
            }

            $('#stock-info').html(`${symbol} - ₹${latestClose} (${percentageChange}%)`);


            if (timeframe === '30minute' && data['30minute'].data && data['30minute'].data.candles.length > 0) {
                chartData = data['30minute'].data.candles.map(candle => [
                    candle[0],  // Timestamp in milliseconds
                    candle[1],  // Open
                    candle[2],  // High
                    candle[3],  // Low
                    candle[4]   // Close
                ]).reverse();
            } else if (timeframe === 'day' && data['day'].data && data['day'].data.candles.length > 0) {
                chartData = data['day'].data.candles.map(candle => [
                    candle[0],  // Timestamp in milliseconds
                    candle[1],  // Open
                    candle[2],  // High
                    candle[3],  // Low
                    candle[4]   // Close
                ]).reverse();
            } else {
                $('#chart-data').html('<p>No data available for ' + symbol + '</p>');
                return;
            }

            // Render the chart with the selected timeframe data
            Highcharts.stockChart('chart-data', {
                chart: {
                    marginRight: 50
                },
                yAxis: {
                    labels: {
                        align: 'left',
                        x: 15
                    }
                },
                rangeSelector: {
                    allButtonsEnabled: true,
                    buttons: [{
                        type: 'minute',
                        count: 30,
                        text: '30m',
                        events: {
                            click: function () {
                                fetchStockData(symbol, '30minute');
                            }
                        }
                    }, {
                        type: 'day',
                        count: 1,
                        text: '1D',
                        events: {
                            click: function () {
                                fetchStockData(symbol, 'day');
                            }
                        }
                    }],
                    selected: timeframe === 'day' ? 0 : 1,
                    inputEnabled: false
                },
                series: [{
                    name: symbol,
                    type: 'candlestick',
                    data: chartData,
                    tooltip: {
                        valueDecimals: 2
                    }
                }]
            });
        }).fail(function (jqXHR, textStatus, errorThrown) {
            $('#chart-data').html('<p>Failed to fetch data: ' + textStatus + '</p>');
        });
    }

    // Fetch data for the initially selected stock with default timeframe day
    fetchStockData($('.stock-item:first').data('symbol'), 'day');

    // Handle stock selection from the list
    $('.stock-item').click(function () {
        fetchStockData($(this).data('symbol'), 'day');
    });

    // Implement search functionality
    $('#stock-search').on('keyup', function () {
        var searchTerm = $(this).val().toLowerCase();
        $('.stock-item').each(function () {
            var stockName = $(this).text().toLowerCase();
            if (stockName.indexOf(searchTerm) !== -1) {
                $(this).show();
            } else {
                $(this).hide();
            }
        });
    });
});