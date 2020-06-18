<?php

/*
GNU General Public License v3.0

Copyright (C) 2007 Free Software Foundation, Inc. <https://fsf.org/>
Everyone is permitted to copy and distribute verbatim copies
of this license document, but changing it is not allowed.
*/

if ( sizeof($argv) < 2 ) {
  __debug('usage: '.$argv[0].' path_file');
  exit(0);
}

function __debug($mesg, $debug=true) { if ( $debug ) {	echo "$mesg\n"; } }
$dir = new DirectoryIterator($argv[1]);

foreach ($dir as $file) {
	if ( !$file->isDot() ) {
		if  ( $file->isDir() )
			recursivo($file->getFilename(), $file->getPathname());
		else send_file($file);
	}
}
function recursivo($path, $dir_name){
	global $dir_name;
	$DI = new DirectoryIterator( $path );
	foreach ($DI as $file){
		if (!$file->isDot()) {
			if  ( $file->isFile() ) { 
				if ( !send_file($file) ) { __debug(" [!] não possível enviar o arquivo.");	} 
			}
		}
	}
}
function send_file($file) {
	$address = 'ops...';
	$service_port = 80;
	__debug("\n [*] send file :: ".$file->getFilename());
	$socket = socket_create(AF_INET, SOCK_STREAM, SOL_TCP);
	__debug(" [?] attempting to connect to '$address' on port '$service_port'...");
	if ( !socket_connect($socket, $address, $service_port) ) {
		__debug(' [!] unable to connect with host.');
		return false;
	}
	$file_name = $file->getFilename();
	$file_path = $file->getPathname();
	$file_size = filesize($file_path);
	$response = "is_file:$file_name:$file_size";
	socket_send($socket, $response, strlen($response), 0);
	$bytes_data = '';
	socket_recv($socket, $bytes_data, 2, 0);
	__debug(" [/] recv before: $bytes_data");
	if ( $file_size == 0 ) {
		$content = 'ops...não deu pra ler esse';
		__debug(" [*] $file_name ops... não deu pra ler...");
	} else {
		__debug(" [*] $file_name with $file_size bytes...");
		$file_handler = fopen($file_path, 'rb');
		$content = fread($file_handler, $file_size);
		fclose($file_handler);
	}
	socket_send($socket, $content, strlen($content), 0);
	$bytes_data = '';
	socket_recv($socket, $bytes_data, 2, 0);
	__debug(" [\\] recv after: $bytes_data");
	socket_close($socket);
	__debug(" [+] ok :: $file_path");
	return true;
}
