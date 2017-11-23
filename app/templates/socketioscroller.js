$(document).ready(function() {
            
            var namespace = '/tty';
            var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace);

            socket.on('my_response', function(msg) {
               $('#log').append(msg.data);
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
            }, 1000);
            
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
                        $('#log').append(result);
                        $('#logcontainer').animate({scrollTop: $('#log').prop("scrollHeight")}, 1);
                    },
                    error: function(result) {
                        $('#log').append(result);
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