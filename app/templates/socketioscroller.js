$(document).ready(function() {
            
            var namespace = '/tty';
            
            var connectionOptions =  {
                "force new connection" : true,
                "reconnection": true,
                "reconnectionDelay": 2000,                  //starts with 2 secs delay, then 4, 6, 8, until 60 where it stays forever until it reconnects
                "reconnectionDelayMax" : 30000,             //30 seconds maximum delay between connections
                "reconnectionAttempts": "Infinity",         //to prevent dead clients, having the user to having to manually reconnect after a server restart.
                "timeout" : 5000,                           //5 seconds before connect_error and connect_timeout are emitted.
                "transports" : ["websocket"]                //forces the transport to be only websocket. Server needs to be setup as well/
            }

            var url = location.protocol + '//' + document.domain + ':' + location.port + namespace;
            
            var socket = io(url, connectionOptions); 
            socket.on('my_response', function(msg) {
               $('#log').append(msg.data + '\n');
               $('#logcontainer').animate({scrollTop: $('#log').prop("scrollHeight")}, 1);
            });
            
            socket.emit('join', {room: '{{ roomhash }}'});
             // rejoin if there's a disconnect
            socket.on('reconnect', () => {
                socket.emit('join', {room: '{{ roomhash }}'})
            });

            var ping_pong_times = [];
            var start_time;
            window.setInterval(function() {
                start_time = (new Date).getTime();
                socket.emit('my_ping');
            }, 5000);

            socket.on('my_pong', function() {
                var latency = (new Date).getTime() - start_time;
                ping_pong_times.push(latency);
                ping_pong_times = ping_pong_times.slice(-30); // keep last 30 samples
                var sum = 0;
                for (var i = 0; i < ping_pong_times.length; i++)
                    sum += ping_pong_times[i];
                $('#ping-pong').text(Math.round(10 * sum / ping_pong_times.length) / 10);
            });

                        
            $("#doaction").click(function(e) {
                e.preventDefault();
                $.ajax({
                    type: "POST",
                    url: "{{ action }}",
                    data: { 
                        id: $(this).val()
                    },
                    success: function(result) {
                        $('#log').append(result + '\n');
                        $('#logcontainer').animate({scrollTop: $('#log').prop("scrollHeight")}, 1);
                    },
                    error: function(result) {
                        $('#log').append(result + '\n');
                        $('#logcontainer').animate({scrollTop: $('#log').prop("scrollHeight")}, 1);
                    }
                });
            });

            $("#reset").click(function(e) {
                e.preventDefault();
                // as we got here via a post, we can't just reload()
                window.location.href=window.location.href
            });



        });