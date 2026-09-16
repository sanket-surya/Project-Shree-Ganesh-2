/**
 * @file ws_server.hpp
 * @brief Minimal WebSocket Server (RFC 6455) using WinSock2 — Zero External Libraries
 *        Air-Gapped, Defense-Grade. Streams C++ telemetry JSON to React GCS Dashboard.
 * @platform Windows (WinSock2 built-in)
 */

#pragma once

#ifndef WS_SERVER_HPP
#define WS_SERVER_HPP

#define WIN32_LEAN_AND_MEAN
#include <winsock2.h>
#include <ws2tcpip.h>
#include <windows.h>
#pragma comment(lib, "ws2_32.lib")

#include <string>
#include <vector>
#include <functional>
#include <thread>
#include <atomic>
#include <mutex>
#include <sstream>
#include <iostream>
#include <cstdint>
#include <cstring>

// ─── SHA-1 for WebSocket Handshake (RFC 6455 key) ─────────────────────────────
namespace Sha1 {
    static uint32_t rotl(uint32_t x, int n) { return (x << n) | (x >> (32 - n)); }

    static std::vector<uint8_t> hash(const std::string& msg) {
        uint32_t h0 = 0x67452301, h1 = 0xEFCDAB89, h2 = 0x98BADCFE,
                 h3 = 0x10325476, h4 = 0xC3D2E1F0;

        std::vector<uint8_t> data(msg.begin(), msg.end());
        uint64_t bitlen = data.size() * 8ULL;
        data.push_back(0x80);
        while (data.size() % 64 != 56) data.push_back(0);
        for (int i = 7; i >= 0; --i)
            data.push_back((uint8_t)(bitlen >> (i * 8)));

        for (size_t i = 0; i < data.size(); i += 64) {
            uint32_t w[80];
            for (int j = 0; j < 16; ++j)
                w[j] = ((uint32_t)data[i+j*4]<<24)|((uint32_t)data[i+j*4+1]<<16)|
                        ((uint32_t)data[i+j*4+2]<<8)|data[i+j*4+3];
            for (int j = 16; j < 80; ++j)
                w[j] = rotl(w[j-3]^w[j-8]^w[j-14]^w[j-16], 1);

            uint32_t a=h0,b=h1,c=h2,d=h3,e=h4;
            for (int j = 0; j < 80; ++j) {
                uint32_t f, k;
                if      (j<20){f=(b&c)|(~b&d); k=0x5A827999;}
                else if (j<40){f= b^c^d;        k=0x6ED9EBA1;}
                else if (j<60){f=(b&c)|(b&d)|(c&d);k=0x8F1BBCDC;}
                else          {f= b^c^d;        k=0xCA62C1D6;}
                uint32_t tmp=rotl(a,5)+f+e+k+w[j];
                e=d; d=c; c=rotl(b,30); b=a; a=tmp;
            }
            h0+=a; h1+=b; h2+=c; h3+=d; h4+=e;
        }

        std::vector<uint8_t> res(20);
        for (int i = 0; i < 5; ++i) {
            uint32_t h = (i==0)?h0:(i==1)?h1:(i==2)?h2:(i==3)?h3:h4;
            res[i*4+0]=(h>>24)&0xFF; res[i*4+1]=(h>>16)&0xFF;
            res[i*4+2]=(h>>8)&0xFF;  res[i*4+3]= h&0xFF;
        }
        return res;
    }
}

// ─── Base64 Encode ─────────────────────────────────────────────────────────────
static std::string base64Encode(const std::vector<uint8_t>& data) {
    static const char* b64 =
        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
    std::string out;
    int i = 0;
    while (i < (int)data.size()) {
        uint32_t b = 0; int pad = 0;
        for (int j = 0; j < 3; ++j) {
            b <<= 8;
            if (i < (int)data.size()) b |= data[i++];
            else { b |= 0; pad++; }
        }
        out += b64[(b>>18)&63]; out += b64[(b>>12)&63];
        out += (pad<2) ? b64[(b>>6)&63] : '=';
        out += (pad<1) ? b64[b&63] : '=';
    }
    return out;
}

// ─── WebSocket Frame Builder ───────────────────────────────────────────────────
static std::vector<uint8_t> buildWsFrame(const std::string& payload) {
    std::vector<uint8_t> frame;
    frame.push_back(0x81); // FIN + text opcode
    size_t len = payload.size();
    if (len < 126) {
        frame.push_back((uint8_t)len);
    } else if (len < 65536) {
        frame.push_back(126);
        frame.push_back((len >> 8) & 0xFF);
        frame.push_back(len & 0xFF);
    } else {
        frame.push_back(127);
        for (int i = 7; i >= 0; --i) frame.push_back((len >> (i*8)) & 0xFF);
    }
    frame.insert(frame.end(), payload.begin(), payload.end());
    return frame;
}

// ─── Decode masked WebSocket frame from client ────────────────────────────────
static std::string decodeWsFrame(const uint8_t* buf, size_t len) {
    if (len < 2) return "";
    bool masked  = (buf[1] & 0x80) != 0;
    size_t plen  = buf[1] & 0x7F;
    size_t off   = 2;
    if (plen == 126) { plen = ((size_t)buf[2]<<8)|buf[3]; off = 4; }
    if (!masked || off + 4 + plen > len) return "";
    const uint8_t* mask = buf + off; off += 4;
    std::string out(plen, 0);
    for (size_t i = 0; i < plen; ++i) out[i] = buf[off+i] ^ mask[i%4];
    return out;
}

// ─── Main WebSocket Server Class ───────────────────────────────────────────────
class AeroTwinWsServer {
public:
    std::atomic<bool>  running{false};
    std::atomic<bool>  clientConnected{false};
    std::mutex         sendMtx;
    SOCKET             clientSock = INVALID_SOCKET;
    SOCKET             listenSock = INVALID_SOCKET;
    int                port;

    explicit AeroTwinWsServer(int p = 9001) : port(p) {}

    bool start() {
        WSADATA wsa;
        if (WSAStartup(MAKEWORD(2,2), &wsa) != 0) return false;

        listenSock = socket(AF_INET, SOCK_STREAM, 0);
        if (listenSock == INVALID_SOCKET) return false;

        int opt = 1;
        setsockopt(listenSock, SOL_SOCKET, SO_REUSEADDR, (char*)&opt, sizeof(opt));

        sockaddr_in addr{};
        addr.sin_family      = AF_INET;
        addr.sin_addr.s_addr = htonl(INADDR_LOOPBACK); // 127.0.0.1 only (air-gapped)
        addr.sin_port        = htons((u_short)port);

        if (bind(listenSock, (sockaddr*)&addr, sizeof(addr)) == SOCKET_ERROR) {
            closesocket(listenSock); return false;
        }
        listen(listenSock, 1);
        running = true;
        std::cout << "[AeroTwin C++] WebSocket server on ws://127.0.0.1:" << port << "\n";
        return true;
    }

    // Accept loop — blocks until client connects
    void acceptLoop() {
        while (running) {
            sockaddr_in cli{}; int clen = sizeof(cli);
            SOCKET s = accept(listenSock, (sockaddr*)&cli, &clen);
            if (s == INVALID_SOCKET) continue;

            if (doHandshake(s)) {
                clientSock      = s;
                clientConnected = true;
                std::cout << "[AeroTwin C++] React GCS Dashboard connected.\n";
                // Read loop (ignore client messages, just keep connection alive)
                char buf[1024];
                while (running) {
                    int n = recv(s, buf, sizeof(buf), 0);
                    if (n <= 0) break;
                }
                clientConnected = false;
                clientSock      = INVALID_SOCKET;
                closesocket(s);
                std::cout << "[AeroTwin C++] Dashboard disconnected. Waiting...\n";
            } else {
                closesocket(s);
            }
        }
    }

    // Send JSON telemetry string to connected React client
    bool sendJson(const std::string& json) {
        if (!clientConnected) return false;
        auto frame = buildWsFrame(json);
        std::lock_guard<std::mutex> lk(sendMtx);
        int sent = send(clientSock, (const char*)frame.data(), (int)frame.size(), 0);
        return sent > 0;
    }

    void stop() {
        running = false;
        closesocket(listenSock);
        if (clientSock != INVALID_SOCKET) closesocket(clientSock);
        WSACleanup();
    }

private:
    bool doHandshake(SOCKET s) {
        char buf[2048] = {};
        int n = recv(s, buf, sizeof(buf)-1, 0);
        if (n <= 0) return false;

        std::string req(buf, n);
        // Extract Sec-WebSocket-Key
        const std::string keyHeader = "Sec-WebSocket-Key: ";
        size_t pos = req.find(keyHeader);
        if (pos == std::string::npos) return false;
        pos += keyHeader.size();
        size_t end = req.find("\r\n", pos);
        std::string key = req.substr(pos, end - pos);

        // Compute accept key (RFC 6455)
        std::string magic = key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11";
        auto sha = Sha1::hash(magic);
        std::string accept = base64Encode(sha);

        std::string resp =
            "HTTP/1.1 101 Switching Protocols\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            "Access-Control-Allow-Origin: *\r\n"
            "Sec-WebSocket-Accept: " + accept + "\r\n\r\n";

        send(s, resp.c_str(), (int)resp.size(), 0);
        return true;
    }
};

#endif // WS_SERVER_HPP
