#!/usr/bin/env python3
"""Run only on a disposable local Minecraft 26.1.1 server with test-only RCON.
Requires the previously generated datapack ZIP installed before first start.
"""
import os
import socket
import struct
import time

HOST='127.0.0.1'
PORT=25575
PASS=os.environ.get('NUTOASTER_TEST_RCON','nutoaster-test-only')

def read_exact(sock,n):
    buf=b''
    while len(buf)<n:
        part=sock.recv(n-len(buf))
        if not part:raise RuntimeError('RCON EOF')
        buf+=part
    return buf

class Rcon:
    def __init__(self):
        self.s=socket.create_connection((HOST,PORT),timeout=10)
        self.s.settimeout(10)
        self.serial=0
        auth_id=self.packet(3,PASS)
        # Minecraft RCON may emit an empty RESPONSE_VALUE packet before AUTH_RESPONSE.
        for _ in range(4):
            _,response_id,kind,body=self.receive()
            if response_id==-1:raise RuntimeError('RCON auth refused')
            if response_id==auth_id and kind==2:
                break
        else:
            raise RuntimeError('No RCON auth response')

    def packet(self,kind,body):
        self.serial+=1
        payload=struct.pack('<ii',self.serial,kind)+body.encode('utf-8')+b'\x00\x00'
        self.s.sendall(struct.pack('<i',len(payload))+payload)
        return self.serial

    def receive(self):
        length=struct.unpack('<i',read_exact(self.s,4))[0]
        if not (8<=length<=1048576):raise RuntimeError('Invalid RCON length '+str(length))
        raw=read_exact(self.s,length)
        return length,*struct.unpack('<ii',raw[:8]),raw[8:-2].decode('utf-8',errors='replace')

    def cmd(self,s):
        ident=self.packet(2,s)
        _,rid,_,text=self.receive()
        if rid!=ident:raise RuntimeError('Mismatched RCON response')
        return text

    def close(self):self.s.close()


def main():
    conn=Rcon()
    try:
        print('forceload',conn.cmd('forceload add 0 0 64 40'))
        print('build',conn.cmd('execute positioned 0 90 0 run function nutoaster:build'))
        time.sleep(3)
        checks=[
            (10,111,8,'iron_block'),(30,111,8,'iron_block'),
            (55,111,8,'weathered_copper'),
            (6,112,8,'orange_concrete'),(24,112,8,'orange_concrete'),
            (23,112,8,'cut_copper'),(10,113,8,'light_gray_concrete'),
            (9,91,34,'lime_concrete'),
        ]
        def check(x,y,z,block):
            response=conn.cmd(f'execute if block {x} {y} {z} minecraft:{block} run seed')
            if not ('Seed' in response and 'fail' not in response.lower()):
                raise AssertionError(f'EXPECTED {block} at ({x},{y},{z}) received {response!r}')
            print('MATCH',x,y,z,block)
        for c in checks:check(*c)
        print('press_high',conn.cmd('execute positioned 0 90 0 run function nutoaster:press_high'))
        check(18,91,34,'red_concrete')
        check(9,91,34,'gray_concrete')
        print('press_off',conn.cmd('execute positioned 0 90 0 run function nutoaster:press_off'))
        check(9,91,34,'lime_concrete')
        check(18,91,34,'gray_concrete')
        print('PASS: REAL OFFICIAL MINECRAFT JAVA 26.1.1 executed NuToaster 2-bay voxel model and display controls; NO heat/pressure simulated.')
    finally:conn.close()

if __name__=='__main__':main()
