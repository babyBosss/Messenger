import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:socket_io_client/socket_io_client.dart' as IO;
import 'package:intl/intl.dart';
import 'package:http/http.dart' as http;

void main() {
  runApp(const MaterialApp(
    home: MessengerApp(),
  ));
}

class MessengerApp extends StatefulWidget {
  const MessengerApp({Key? key}) : super(key: key);

  @override
  _State createState() => _State();
}

class _State extends State<MessengerApp> {
  final IO.Socket socket = IO.io('http://127.0.0.1:5000', <String, dynamic>{
    'transports': ['websocket'],
  });

  var appTitle = "Messenger";
  late List<String> msgs = <String>[];
  TextEditingController messageController = TextEditingController();

  _connectSocket() {
    socket.onConnect((data) => sonnSuccess(data));
    socket.onConnectError((data) => connError(data));
    socket.on('message', ((data) => messageReceived(data)));
  }

  @override
  void initState() {
    super.initState();
    _connectSocket();
  }

  void sonnSuccess(data) {
    // print('Socket connected!');
    http.get(Uri.parse('http://127.0.0.1:5000/messages/0')).then((response) {
      saveOldMessages(response.body);
    }).catchError((error) {
      print("Error: $error");
    });
    setState(() {
      appTitle = "Messenger";
    });
  }

  void connError(data) {
    print('Connect Error $data');
    setState(() {
      appTitle = "Lost connection";
    });
  }

  void saveOldMessages(old_m) {
    late List<String> old_msgs = <String>[];
    for (var message in json.decode(old_m)['messages']) {
      var time = DateFormat('hh:mm:ss, MM/dd').format(
          DateTime.fromMillisecondsSinceEpoch(
              (message['time'] * 1000).toInt()));
      var m = "${message['username']}   $time\n${message['text']}";
      old_msgs.add(m);
    }
    setState(() {
      msgs = msgs + old_msgs;
    });
  }

  Future<http.Response> sendToDB(String text) {
    return http.post(
      Uri.parse('http://127.0.0.1:5000/send_msg'),
      headers: <String, String>{
        'Content-Type': 'application/json; charset=UTF-8',
      },
      body: jsonEncode(<String, String>{
        'username': 'Mobile User',
        'text': text,
      }),
    );
  }

  void sendMessage() {
    socket.emit('message', {
      'username': 'Mobile User',
      'text': messageController.text.trim(),
      'time': DateTime.now().millisecondsSinceEpoch / 1000
    });
    sendToDB(messageController.text.trim());
  }

  void messageReceived(data) {
    setState(() {
      var time = DateFormat('hh:mm:ss, MM/dd').format(
          DateTime.fromMillisecondsSinceEpoch((data['time'] * 1000).toInt()));
      var m = "${data['username']}    $time\n${data['text']}";
      // msgs.insert(0, m);
      msgs.add(m);
    });
  }

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
        onTap: () => FocusManager.instance.primaryFocus?.unfocus(),
        child: Scaffold(
          appBar: AppBar(
            title: Text(appTitle),
          ),
          body: Column(children: <Widget>[
            Expanded(
              child: ListView.builder(
                // reverse: true,
                  padding: const EdgeInsets.all(8),
                  itemCount: msgs.length,
                  itemBuilder: (BuildContext context, int index) {
                    return Container(
                        margin: const EdgeInsets.all(3),
                        decoration: BoxDecoration(
                          borderRadius: BorderRadius.circular(12),
                          color: const Color.fromRGBO(173, 224, 255, 0.8),
                        ),
                        child: Padding(
                          padding: const EdgeInsets.only(top: 10, bottom: 10),
                          child: Center(
                            child: Align(
                              alignment: Alignment.centerLeft,
                              child: Container(
                                  margin: const EdgeInsets.only(
                                      left: 15, right: 15),
                                  child: Text(
                                    msgs[index].toString(),
                                    style: const TextStyle(fontSize: 18),
                                    maxLines: 30,
                                    softWrap: true,
                                    overflow: TextOverflow.fade,
                                  )),
                            ),
                          ),
                        ));
                  }),
            ),
            Padding(
                padding: const EdgeInsets.only(left: 20, right: 20, bottom: 20),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.end,
                  crossAxisAlignment: CrossAxisAlignment.end,
                  children: [
                    Expanded(
                      flex: 8,
                      child: Padding(
                        padding: const EdgeInsets.only(
                            top: 10, bottom: 1, left: 1, right: 1),
                        child: TextField(
                          controller: messageController,
                          decoration: const InputDecoration(
                            border: OutlineInputBorder(),
                            labelText: 'Write message',
                          ),
                        ),
                      ),
                    ),
                    Expanded(
                      flex: 2,
                      child: Container(
                          width: 40,
                          margin: const EdgeInsets.only(
                              top: 5, bottom: 5, left: 15),
                          child: Center(
                            child: IconButton(
                              icon: const Icon(Icons.send),
                              onPressed: () {
                                if (messageController.text.trim().isNotEmpty) {
                                  sendMessage();
                                  messageController.text = "";
                                }
                              },
                            ),
                          )),
                    )
                  ],
                ))
          ]),
        ));
  }
}

// child: Text('${msgs[index]}',
//snapshot.hasData ? '${snapshot.data}' : ''
