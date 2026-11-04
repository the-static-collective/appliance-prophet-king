#!/usr/bin/env python3
"""ONLY run against disposable official vanilla Minecraft test world.
No power, heat, spring force, food-safety, or actual machining implied.
"""
import os, socket, struct, time

HOST='127.0.0.1'
PORT=25575
PASS=os.environ.get('NUTOASTER_TEST_RCON','nutoaster-p0-ci-only')

def read_exact(sock, n):
    buf=b''
    while len(buf)<n:
        c=sock.recv(n-len(buf))
        if not c:raise RuntimeError('RCON connection closed')
        buf+=c
    return buf

class Rcon:
    def __init__(self):
        self.sock=socket.create_connection((HOST,PORT),timeout=30)
        self.sock.settimeout(30)
        self.serial=0
        auth=self.packet(3,PASS)
        for _ in range(4):
            rid,kind,_=self.receive()
            if rid==-1:raise RuntimeError('RCON authentication refused')
            if rid==auth and kind==2:break
        else:raise RuntimeError('No RCON auth response')
    def packet(self,kind,body):
        self.serial+=1
        payload=struct.pack('<ii',self.serial,kind)+body.encode()+b'\0\0'
        self.sock.sendall(struct.pack('<i',len(payload))+payload)
        return self.serial
    def receive(self):
        n=struct.unpack('<i',read_exact(self.sock,4))[0]
        if not 10<=n<=8192:raise RuntimeError('RCON response size invalid')
        raw=read_exact(self.sock,n)
        serial,kind=struct.unpack('<ii',raw[:8])
        return serial,kind,raw[8:-2].decode('utf-8',errors='replace')
    def cmd(self,s):
        sent=self.packet(2,s)
        rid,_,message=self.receive()
        if rid!=sent:raise RuntimeError('RCON response mismatch')
        return message
    def close(self):self.sock.close()

def main():
    c=Rcon()
    try:
        print('forceload:',c.cmd('forceload add 0 0 70 50'))
        result=c.cmd('execute positioned 0 90 0 run function nutoaster_p0:build')
        print('build:',result)
        if 'unknown' in result.lower() or 'not found' in result.lower() or 'error' in result.lower():
            raise AssertionError('Minecraft did not find generated function')
        checks=[
            (10,121,9,'iron_block'),(27,121,9,'iron_block'),
            (55,121,9,'weathered_copper'),
            (4,122,9,'orange_concrete'),(39,122,9,'orange_concrete'),
            (21,122,9,'cut_copper'),(6,126,9,'light_gray_concrete'),
            (7,91,44,'lime_concrete')]
        def check(entry):
            x,y,z,material=entry
            for _ in range(30):
                response=c.cmd(f'execute if block {x} {y} {z} minecraft:{material} run seed')
                if 'Seed' in response and 'fail' not in response.lower():
                    print('MATCH',x,y,z,material)
                    return
                time.sleep(.25)
            raise AssertionError(f'Expected {material} at {x,y,z}; got {response!r}')
        for x in checks:check(x)
        result=c.cmd('execute positioned 0 90 0 run function nutoaster_p0:press_high')
        print('high mode',result)
        check((16,91,44,'red_concrete'))
        check((7,91,44,'gray_concrete'))
        c.cmd('execute positioned 0 90 0 run function nutoaster_p0:press_off')
        check((7,91,44,'lime_concrete'))
        check((16,91,44,'gray_concrete'))
        print('PASS: real vanilla Minecraft P0 voxel shell, dual bays, control markers. NOT measured, no mechanical or heating simulation.')
    finally:c.close()

if __name__=='__main__':main()
