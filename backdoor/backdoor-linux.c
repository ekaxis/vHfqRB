#include <stdio.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <errno.h>
#include <netinet/in.h>
#include <netinet/ip.h>
#include <string.h>

#define is_debug 		1
#define buffer_mesg 	100
#define dns_host 		""
#define ip_host_master 	""

void __debug(char* mesg) {
	if ( is_debug ) printf(" [debug] %s\n", mesg);
}

__send(int sockf, char *mesg) {}

int main(int argc, char* argv[]) {

	char buffer_errno[buffer_mesg];
	int sockf, output;

	/*
 	* int socekt(int domain, int type, int protocol)
 	*/
	sockf = socket(AF_INET, SOCK_STREAM, 0);
	if ( sockf == -1 ) {
		sprintf(buffer_errno, "err call socket() [%d]", errno);
		__debug(buffer_errno);
		return errno;
	} __debug("sucessful create socket.");

	/*
	* struct sockaddr_in {
	* 	sa_family_t    sin_family;  	address family: AF_INET 
	* 	in_port_t      sin_port;    	port in network byte order 
	* 	struct in_addr sin_addr;   		internet address 
	* };
	*/
	struct sockaddr_in host_addr;
	memset(&host_addr, 0, sizeof(host_addr));
	host_addr.sin_family = AF_INET;
	host_addr.sin_port = htons(8080);	
	
	/*
	*	struct in_addr {
	*		uint32_t       s_addr;     address in network byte order
	*	}
	*/ 
	host_addr.sin_addr.s_addr = inet_addr(ip_host_master);

	output = connect(sockf, (struct sockaddr*)&host_addr, sizeof(host_addr));
	if ( output == -1 ) {
		sprintf(buffer_errno, "err call connect() [%d]", errno);
		__debug(buffer_errno);
		return errno;
	}	__debug("successful call connect()");

	close(sockf);
	return 0;
}
