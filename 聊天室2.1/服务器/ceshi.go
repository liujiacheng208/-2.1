package main

import (
	"fmt"
	"io"
	"net"
	"sync"
)

var (
	connections = make(map[net.Conn]struct{})
	mu          sync.Mutex
)

func handleConnection(conn net.Conn) {
	defer conn.Close()
	defer func() {
		mu.Lock()
		delete(connections, conn)
		mu.Unlock()
	}()

	buf := make([]byte, 1024)
	for {
		n, err := conn.Read(buf)
		if err != nil {
			if err != io.EOF {
				fmt.Println("读取错误:", err)
			}
			return
		}
		data := string(buf[:n])
		fmt.Println("收到数据:", data)
		broadcast(data, conn)
	}
}

func broadcast(message string, conn net.Conn) {
	mu.Lock()
	defer mu.Unlock()
	for conns := range connections {
		if conn != conns {
			_, err := conns.Write([]byte(message))
			if err != nil {
				fmt.Println("写入错误:", err)
				conns.Close()
				delete(connections, conns)

			}
		}
	}
}

func main() {
	fmt.Println("服务器正在监听...")
	listen, err := net.Listen("tcp", ":8080")
	if err != nil {
		fmt.Println("启动服务器错误:", err)
		return
	}
	defer listen.Close()

	for {
		conn, err := listen.Accept()
		if err != nil {
			fmt.Println("接受连接错误:", err)
			continue
		}

		mu.Lock()
		connections[conn] = struct{}{}
		mu.Unlock()

		fmt.Printf("接受来自 %s 的连接\n", conn.RemoteAddr().String())
		go handleConnection(conn)
	}
}
