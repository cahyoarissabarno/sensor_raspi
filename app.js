const express = require('express');
const mysql = require('mysql');
const http = require('http');
const socketIo = require('socket.io');

// Setup Express
const app = express();
const server = http.createServer(app);
const io = socketIo(server);

// Setup MySQL connection
const connection = mysql.createConnection({
    host: '127.0.0.1',
    user: 'jovial',
    password: 'jovial',
    database: 'sensor_data'
});

// Serve static files (frontend)
app.use(express.static('public'));

// Fetch data from MySQL
function fetchData(callback) {
    connection.query('SELECT * FROM sensor_table ORDER BY timestamp DESC LIMIT 10', (err, results) => {
        if (err) throw err;
        callback(results);
    });
}

// Setup WebSocket for real-time data
io.on('connection', (socket) => {
    console.log('New client connected');

    // Send initial data on connection
    fetchData((data) => {
        socket.emit('initialData', data);
    });

    // Fetch new data every 5 seconds
    setInterval(() => {
        fetchData((data) => {
            socket.emit('updateData', data);
        });
    }, 5000);

    socket.on('disconnect', () => {
        console.log('Client disconnected');
    });
});

// Start server
server.listen(3000, () => {
    console.log('Server is running on port 3000');
});
